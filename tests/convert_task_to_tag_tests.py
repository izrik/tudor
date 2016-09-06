#!/usr/bin/env python

import unittest

from tudor import generate_app


class ConvertTaskToTagTest(unittest.TestCase):

    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.ds = self.app.ds
        self.db = self.ds.db
        self.db.create_all()
        self.Task = self.app.Task
        self.Tag = self.app.Tag
        self.TaskTagLink = self.app.TaskTagLink
        self.user = self.ds.User('name@example.org', None, True)

    def test_old_task_becomes_a_tag(self):
        # given
        task = self.Task('some_task')
        self.db.session.add(task)
        self.db.session.commit()

        self.assertEquals(0, self.Tag.query.count())

        # when
        tag = self.app._convert_task_to_tag(task.id, self.user)

        # then
        self.assertIsNotNone(tag)
        self.assertEquals(1, self.Tag.query.count())
        self.assertIs(tag, self.Tag.query.first())

    def test_old_task_gets_deleted(self):
        # given
        task = self.Task('some_task')
        self.db.session.add(task)
        self.db.session.commit()

        self.assertEquals(1, self.Task.query.count())

        # when
        tag = self.app._convert_task_to_tag(task.id, self.user)

        # then
        self.assertEquals(0, self.Task.query.count())

    def test_child_tasks_get_the_new_tag(self):
        # given
        task = self.Task('some_task')
        self.db.session.add(task)

        child1 = self.Task('child1')
        child1.parent = task
        self.db.session.add(child1)
        child2 = self.Task('child2')
        child2.parent = task
        self.db.session.add(child2)
        child3 = self.Task('child3')
        child3.parent = task
        self.db.session.add(child3)

        self.db.session.commit()

        self.assertEquals(4, self.Task.query.count())
        self.assertEquals(0, child1.tags.count())
        self.assertEquals(0, child2.tags.count())
        self.assertEquals(0, child3.tags.count())

        self.assertIs(task, child1.parent)
        self.assertIs(task, child2.parent)
        self.assertIs(task, child3.parent)

        # when
        tag = self.app._convert_task_to_tag(task.id, self.user)

        # then
        self.assertEquals(3, self.Task.query.count())
        self.assertEquals(1, child1.tags.count())
        self.assertEquals(1, child2.tags.count())
        self.assertEquals(1, child3.tags.count())

        self.assertIsNone(child1.parent)
        self.assertIsNone(child2.parent)
        self.assertIsNone(child3.parent)

    def test_child_tasks_get_the_old_tasks_tags(self):
        # given

        tag1 = self.Tag('tag1')
        self.db.session.add(tag1)

        task = self.Task('some_task')
        self.db.session.add(task)

        self.db.session.commit()

        ttl = self.TaskTagLink(task.id, tag1.id)
        self.db.session.add(ttl)

        child1 = self.Task('child1')
        child1.parent = task
        self.db.session.add(child1)
        child2 = self.Task('child2')
        child2.parent = task
        self.db.session.add(child2)
        child3 = self.Task('child3')
        child3.parent = task
        self.db.session.add(child3)

        self.db.session.commit()

        self.assertEquals(1, tag1.tasks.count())
        self.assertEquals(0, child1.tags.count())
        self.assertEquals(0, child2.tags.count())
        self.assertEquals(0, child3.tags.count())

        # when
        tag = self.app._convert_task_to_tag(task.id, self.user)

        # then
        self.assertEquals(3, tag1.tasks.count())
        self.assertEquals(2, child1.tags.count())
        self.assertEquals(2, child2.tags.count())
        self.assertEquals(2, child3.tags.count())

    def test_children_of_old_task_become_children_of_old_tasks_parent(self):
        # given

        grand_parent = self.Task('grand_parent')
        self.db.session.add(grand_parent)

        task = self.Task('some_task')
        task.parent = grand_parent
        self.db.session.add(task)

        child1 = self.Task('child1')
        child1.parent = task
        self.db.session.add(child1)
        child2 = self.Task('child2')
        child2.parent = task
        self.db.session.add(child2)
        child3 = self.Task('child3')
        child3.parent = task
        self.db.session.add(child3)

        self.db.session.commit()

        self.assertEquals(1, grand_parent.children.count())
        self.assertIs(task, child1.parent)
        self.assertIs(task, child2.parent)
        self.assertIs(task, child3.parent)

        # when
        tag = self.app._convert_task_to_tag(task.id, self.user)

        # then
        self.assertEquals(3, grand_parent.children.count())
        self.assertIs(grand_parent, child1.parent)
        self.assertIs(grand_parent, child2.parent)
        self.assertIs(grand_parent, child3.parent)
