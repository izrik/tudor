#!/usr/bin/env python

import unittest

from werkzeug.exceptions import Forbidden

from tests.logic_layer_t.util import generate_ll
from models.task import Task
from models.user import User
from models.tag import Tag


class LogicLayerTaskTagsTest(unittest.TestCase):

    def setUp(self):
        self.ll = generate_ll(db_uri='sqlite://')
        self.pl = self.ll.pl
        self.pl.create_all()
        self.admin = User('name@example.org', None, True)
        self.pl.add(self.admin)
        self.user = User('name2@example.org', None, False)
        self.pl.add(self.user)

    def test_add_tag_to_task_admin_nonexistent_adds_tag(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(task.tags))

        # when
        tag = self.ll.do_add_tag_to_task(task, 'ghi', self.admin)

        # then
        self.assertEqual(1, len(task.tags))
        self.assertIsNotNone(tag)
        self.assertIsInstance(tag, Tag)
        self.assertEqual('ghi', tag.value)

    def test_add_tag_to_task_admin_existent_adds_tag(self):
        # given
        task = Task('task')
        tag1 = Tag('jkl')
        self.pl.add(task)
        self.pl.add(tag1)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(task.tags))

        # when
        tag2 = self.ll.do_add_tag_to_task(task, 'jkl', self.admin)

        # then
        self.assertEqual(1, len(task.tags))
        self.assertIsNotNone(tag2)
        self.assertIsInstance(tag2, Tag)
        self.assertEqual('jkl', tag2.value)
        self.assertIs(tag1, tag2)

    def test_add_tag_to_task_user_nonexistent_adds_tag(self):
        # given
        task = Task('task')
        task.users.append(self.user)
        self.pl.add(task)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(task.tags))

        # when
        tag = self.ll.do_add_tag_to_task(task, 'mno', self.user)

        # then
        self.assertEqual(1, len(task.tags))
        self.assertIsNotNone(tag)
        self.assertIsInstance(tag, Tag)
        self.assertEqual('mno', tag.value)

    def test_add_tag_to_task_user_existent_adds_tag(self):
        # given
        task = Task('task')
        tag1 = Tag('pqr')
        task.users.append(self.user)
        self.pl.add(task)
        self.pl.add(tag1)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(task.tags))

        # when
        tag2 = self.ll.do_add_tag_to_task(task, 'pqr', self.user)

        # then
        self.assertEqual(1, len(task.tags))
        self.assertIsNotNone(tag2)
        self.assertIsInstance(tag2, Tag)
        self.assertEqual('pqr', tag2.value)
        self.assertIs(tag1, tag2)

    def test_add_tag_to_task_none_raises_value_error(self):
        # precondition
        self.assertEqual(0, self.pl.count_tasks())

        # expect
        self.assertRaises(ValueError,
                          self.ll.do_add_tag_to_task,
                          None, 'abc', self.admin)

    def test_add_tag_to_task_user_not_authorized_raises_forbidden(self):
        # given
        other_user = User('name3@example.org', None, False)
        self.pl.add(other_user)
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(task.tags))

        # expect
        self.assertRaises(Forbidden,
                          self.ll.do_add_tag_to_task,
                          task, 'abc', other_user)
