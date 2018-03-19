#!/usr/bin/env python

import unittest

from werkzeug.exceptions import Forbidden

from models.object_types import ObjectTypes
from tests.logic_t.layer.LogicLayer.util import generate_ll


class LogicLayerTaskTagsTest(unittest.TestCase):

    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.admin = self.pl.create_user('name@example.org', None, True)
        self.pl.add(self.admin)
        self.user = self.pl.create_user('name2@example.org', None, False)
        self.pl.add(self.user)

    def test_add_tag_to_task_admin_nonexistent_adds_tag(self):
        # given
        task = self.pl.create_task('task')
        self.pl.add(task)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(task.tags))

        # when
        tag = self.ll.do_add_tag_to_task(task, 'ghi', self.admin)

        # then
        self.assertEqual(1, len(task.tags))
        self.assertIsNotNone(tag)
        self.assertEqual(tag.object_type, ObjectTypes.Tag)
        self.assertEqual('ghi', tag.value)

    def test_add_tag_to_task_admin_existent_adds_tag(self):
        # given
        task = self.pl.create_task('task')
        tag1 = self.pl.create_tag('jkl')
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
        self.assertEqual(tag2.object_type, ObjectTypes.Tag)
        self.assertEqual('jkl', tag2.value)
        self.assertIs(tag1, tag2)

    def test_add_tag_to_task_user_nonexistent_adds_tag(self):
        # given
        task = self.pl.create_task('task')
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
        self.assertEqual(tag.object_type, ObjectTypes.Tag)
        self.assertEqual('mno', tag.value)

    def test_add_tag_to_task_user_existent_adds_tag(self):
        # given
        task = self.pl.create_task('task')
        tag1 = self.pl.create_tag('pqr')
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
        self.assertEqual(tag2.object_type, ObjectTypes.Tag)
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
        other_user = self.pl.create_user('name3@example.org', None, False)
        self.pl.add(other_user)
        task = self.pl.create_task('task')
        self.pl.add(task)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(task.tags))

        # expect
        self.assertRaises(Forbidden,
                          self.ll.do_add_tag_to_task,
                          task, 'abc', other_user)
