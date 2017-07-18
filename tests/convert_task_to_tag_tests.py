#!/usr/bin/env python

import unittest

from tudor import generate_app
from models.task import Task
from models.tag import Tag
from models.user import User


class ConvertTaskToTagTest(unittest.TestCase):

    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.user = User('name@example.org', None, True)

    def test_old_task_becomes_a_tag(self):
        # given
        task = Task('some_task')
        self.pl.add(task)
        self.pl.commit()

        self.assertEquals(0, self.pl.count_tags())

        # when
        tag = self.app._convert_task_to_tag(task.id, self.user)

        # then
        self.assertIsNotNone(tag)
        self.assertEquals(1, self.pl.count_tags())
        self.assertIs(tag, list(self.pl.get_tags())[0])

    def test_old_task_gets_deleted(self):
        # given
        task = Task('some_task')
        self.pl.add(task)
        self.pl.commit()

        self.assertEquals(1, self.pl.count_tasks())

        # when
        tag = self.app._convert_task_to_tag(task.id, self.user)

        # then
        self.assertEquals(0, self.pl.count_tasks())

    def test_child_tasks_get_the_new_tag(self):
        # given
        task = Task('some_task')
        self.pl.add(task)

        child1 = Task('child1')
        child1.parent = task
        self.pl.add(child1)
        child2 = Task('child2')
        child2.parent = task
        self.pl.add(child2)
        child3 = Task('child3')
        child3.parent = task
        self.pl.add(child3)

        self.pl.commit()

        self.assertEquals(4, self.pl.count_tasks())
        self.assertEquals(0, len(child1.tags))
        self.assertEquals(0, len(child2.tags))
        self.assertEquals(0, len(child3.tags))

        self.assertIs(task, child1.parent)
        self.assertIs(task, child2.parent)
        self.assertIs(task, child3.parent)

        # when
        tag = self.app._convert_task_to_tag(task.id, self.user)

        # then
        self.assertEquals(3, self.pl.count_tasks())
        self.assertEquals(1, len(child1.tags))
        self.assertEquals(1, len(child2.tags))
        self.assertEquals(1, len(child3.tags))

        self.assertIsNone(child1.parent)
        self.assertIsNone(child2.parent)
        self.assertIsNone(child3.parent)

    def test_child_tasks_get_the_old_tasks_tags(self):
        # given

        tag1 = Tag('tag1')
        self.pl.add(tag1)

        task = Task('some_task')
        self.pl.add(task)
        task.tags.append(tag1)

        self.pl.commit()

        child1 = Task('child1')
        child1.parent = task
        self.pl.add(child1)
        child2 = Task('child2')
        child2.parent = task
        self.pl.add(child2)
        child3 = Task('child3')
        child3.parent = task
        self.pl.add(child3)

        self.pl.commit()

        self.assertEquals(1, len(tag1.tasks))
        self.assertEquals(0, len(child1.tags))
        self.assertEquals(0, len(child2.tags))
        self.assertEquals(0, len(child3.tags))

        # when
        tag = self.app._convert_task_to_tag(task.id, self.user)

        # then
        self.assertEquals({child1, child2, child3}, set(tag1.tasks))
        self.assertIn(tag1, child1.tags)
        self.assertIn(tag, child1.tags)
        self.assertIn(tag1, child2.tags)
        self.assertIn(tag, child2.tags)
        self.assertIn(tag1, child3.tags)
        self.assertIn(tag, child3.tags)

    def test_children_of_old_task_become_children_of_old_tasks_parent(self):
        # given

        grand_parent = Task('grand_parent')
        self.pl.add(grand_parent)

        task = Task('some_task')
        task.parent = grand_parent
        self.pl.add(task)

        child1 = Task('child1')
        child1.parent = task
        self.pl.add(child1)
        child2 = Task('child2')
        child2.parent = task
        self.pl.add(child2)
        child3 = Task('child3')
        child3.parent = task
        self.pl.add(child3)

        self.pl.commit()

        self.assertEquals(1, len(grand_parent.children))
        self.assertIs(task, child1.parent)
        self.assertIs(task, child2.parent)
        self.assertIs(task, child3.parent)

        # when
        tag = self.app._convert_task_to_tag(task.id, self.user)

        # then
        self.assertEquals(3, len(grand_parent.children))
        self.assertIs(grand_parent, child1.parent)
        self.assertIs(grand_parent, child2.parent)
        self.assertIs(grand_parent, child3.parent)
