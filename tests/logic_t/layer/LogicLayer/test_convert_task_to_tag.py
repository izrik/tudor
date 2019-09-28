#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound, Forbidden, Conflict

from .util import generate_ll


class ConvertTaskToTagTest(unittest.TestCase):

    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.user = self.pl.create_user('name@example.org', None, True)

    def test_old_task_becomes_a_tag(self):
        # given
        task = self.pl.create_task('some_task')
        self.pl.add(task)
        self.pl.commit()

        self.assertEqual(0, self.pl.count_tags())

        # when
        tag = self.ll.convert_task_to_tag(task.id, self.user)

        # then
        self.assertIsNotNone(tag)
        self.assertEqual(1, self.pl.count_tags())
        self.assertIs(tag, list(self.pl.get_tags())[0])

    def test_old_task_gets_deleted(self):
        # given
        task = self.pl.create_task('some_task')
        self.pl.add(task)
        self.pl.commit()

        self.assertEqual(1, self.pl.count_tasks())

        # when
        tag = self.ll.convert_task_to_tag(task.id, self.user)

        # then
        self.assertIsNotNone(tag)
        self.assertEqual(0, self.pl.count_tasks())

    def test_child_tasks_get_the_new_tag(self):
        # given
        task = self.pl.create_task('some_task')
        self.pl.add(task)

        child1 = self.pl.create_task('child1')
        child1.parent = task
        self.pl.add(child1)
        child2 = self.pl.create_task('child2')
        child2.parent = task
        self.pl.add(child2)
        child3 = self.pl.create_task('child3')
        child3.parent = task
        self.pl.add(child3)

        self.pl.commit()

        self.assertEqual(4, self.pl.count_tasks())
        self.assertEqual(0, len(child1.tags))
        self.assertEqual(0, len(child2.tags))
        self.assertEqual(0, len(child3.tags))

        self.assertIs(task, child1.parent)
        self.assertIs(task, child2.parent)
        self.assertIs(task, child3.parent)

        # when
        tag = self.ll.convert_task_to_tag(task.id, self.user)

        # then
        self.assertIsNotNone(tag)

        self.assertEqual(3, self.pl.count_tasks())
        self.assertEqual(1, len(child1.tags))
        self.assertEqual(1, len(child2.tags))
        self.assertEqual(1, len(child3.tags))

        self.assertIsNone(child1.parent)
        self.assertIsNone(child2.parent)
        self.assertIsNone(child3.parent)

    def test_child_tasks_get_the_old_tasks_tags(self):
        # given

        tag1 = self.pl.create_tag('tag1')
        self.pl.add(tag1)

        task = self.pl.create_task('some_task')
        self.pl.add(task)
        task.tags.append(tag1)

        self.pl.commit()

        child1 = self.pl.create_task('child1')
        child1.parent = task
        self.pl.add(child1)
        child2 = self.pl.create_task('child2')
        child2.parent = task
        self.pl.add(child2)
        child3 = self.pl.create_task('child3')
        child3.parent = task
        self.pl.add(child3)

        self.pl.commit()

        self.assertEqual(1, len(tag1.tasks))
        self.assertEqual(0, len(child1.tags))
        self.assertEqual(0, len(child2.tags))
        self.assertEqual(0, len(child3.tags))

        # when
        tag = self.ll.convert_task_to_tag(task.id, self.user)

        # then
        self.assertEqual({child1, child2, child3}, set(tag1.tasks))
        self.assertIn(tag1, child1.tags)
        self.assertIn(tag, child1.tags)
        self.assertIn(tag1, child2.tags)
        self.assertIn(tag, child2.tags)
        self.assertIn(tag1, child3.tags)
        self.assertIn(tag, child3.tags)

    def test_children_of_old_task_become_children_of_old_tasks_parent(self):
        # given

        grand_parent = self.pl.create_task('grand_parent')
        self.pl.add(grand_parent)

        task = self.pl.create_task('some_task')
        task.parent = grand_parent
        self.pl.add(task)

        child1 = self.pl.create_task('child1')
        child1.parent = task
        self.pl.add(child1)
        child2 = self.pl.create_task('child2')
        child2.parent = task
        self.pl.add(child2)
        child3 = self.pl.create_task('child3')
        child3.parent = task
        self.pl.add(child3)

        self.pl.commit()

        self.assertEqual(1, grand_parent.children.count())
        self.assertIs(task, child1.parent)
        self.assertIs(task, child2.parent)
        self.assertIs(task, child3.parent)

        # when
        tag = self.ll.convert_task_to_tag(task.id, self.user)

        # then
        self.assertIsNotNone(tag)

        self.assertEqual(3, grand_parent.children.count())
        self.assertIs(grand_parent, child1.parent)
        self.assertIs(grand_parent, child2.parent)
        self.assertIs(grand_parent, child3.parent)

    def test_task_not_found_raises(self):
        # precondition
        self.assertEqual(0, self.pl.count_tags())
        self.assertIsNone(self.pl.get_tag(123))
        # expect
        self.assertRaises(
            NotFound,
            self.ll.convert_task_to_tag,
            123, self.user)
        # and
        self.assertEqual(0, self.pl.count_tags())

    def test_user_not_authorized_for_private_task_raises(self):
        # given
        task = self.pl.create_task('some_task', is_public=False)
        self.pl.add(task)
        user2 = self.pl.create_user('user2@example.com')
        self.pl.add(user2)
        self.pl.commit()
        # precondition
        self.assertEqual(0, self.pl.count_tags())
        self.assertNotIn(user2, task.users)
        self.assertNotIn(task, user2.tasks)
        self.assertFalse(task.is_public)
        # expect
        self.assertRaises(
            NotFound,
            self.ll.convert_task_to_tag,
            task.id, user2)
        # and
        self.assertEqual(0, self.pl.count_tags())

    def test_user_not_authorized_for_public_task_raises(self):
        # given
        task = self.pl.create_task('some_task', is_public=True)
        self.pl.add(task)
        user2 = self.pl.create_user('user2@example.com')
        self.pl.add(user2)
        self.pl.commit()
        # precondition
        self.assertEqual(0, self.pl.count_tags())
        self.assertNotIn(user2, task.users)
        self.assertNotIn(task, user2.tasks)
        self.assertTrue(task.is_public)
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.convert_task_to_tag,
            task.id, user2)
        # and
        self.assertEqual(0, self.pl.count_tags())

    def test_tag_name_already_exists_raises(self):
        # given
        task = self.pl.create_task('some_task')
        self.pl.add(task)
        tag = self.pl.create_tag('some_task')
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertEqual(1, self.pl.count_tags())
        # expect
        self.assertRaises(
            Conflict,
            self.ll.convert_task_to_tag,
            task.id, self.user)
        # and
        self.assertEqual(1, self.pl.count_tags())
