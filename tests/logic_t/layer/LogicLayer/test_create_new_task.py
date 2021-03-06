#!/usr/bin/env python

import unittest

import werkzeug.exceptions

from models.object_types import ObjectTypes
from tests.logic_t.layer.LogicLayer.util import generate_ll


class CreateNewTaskTest(unittest.TestCase):

    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.admin = self.pl.create_user('name@example.org', None, True)
        self.pl.add(self.admin)
        self.user = self.pl.create_user('name2@example.org', None, False)
        self.pl.add(self.user)

    def test_admin_adds_first_task(self):
        # when
        task = self.ll.create_new_task(summary='t1', current_user=self.admin)

        # then
        self.assertIsNotNone(task)
        self.assertEqual(task.object_type, ObjectTypes.Task)
        self.assertEqual('t1', task.summary)
        self.assertIsNone(task.parent)
        self.assertEqual(0, task.order_num)

    def test_admin_adds_second_task(self):
        # given
        t1 = self.pl.create_task('t1')
        t1.order_num = 1

        self.pl.add(t1)

        # when
        task = self.ll.create_new_task(summary='t2', current_user=self.admin)

        # then
        self.assertIsNotNone(task)
        self.assertEqual(task.object_type, ObjectTypes.Task)
        self.assertEqual('t2', task.summary)
        self.assertIsNone(task.parent)

    def test_admin_adds_child_task_to_parent(self):
        # given
        p = self.pl.create_task('p')
        p.order_num = 1

        self.pl.add(p)
        self.pl.commit()

        # when
        task = self.ll.create_new_task(summary='c', parent_id=p.id,
                                       current_user=self.admin)

        # then
        self.assertIsNotNone(task)
        self.assertEqual(task.object_type, ObjectTypes.Task)
        self.assertEqual('c', task.summary)
        self.assertIs(p, task.parent)

    def test_user_adds_task_to_authorized_parent_succeeds(self):
        # given
        p = self.pl.create_task('p')
        p.order_num = 1
        p.users.append(self.user)

        self.pl.add(p)
        self.pl.commit()

        # when
        task = self.ll.create_new_task(summary='c', parent_id=p.id,
                                       current_user=self.user)

        # then
        self.assertIsNotNone(task)
        self.assertEqual(task.object_type, ObjectTypes.Task)
        self.assertEqual('c', task.summary)
        self.assertIs(p, task.parent)

    def test_user_adds_task_to_non_authorized_parent_raises_403(self):
        # given
        p = self.pl.create_task('p')
        p.order_num = 1

        self.pl.add(p)
        self.pl.commit()

        # expect
        self.assertRaises(werkzeug.exceptions.Forbidden,
                          self.ll.create_new_task,
                          summary='c', parent_id=p.id, current_user=self.user)

    def test_is_public_sets_is_public(self):
        # when
        task = self.ll.create_new_task('summary', current_user=self.user,
                                       is_public=True)
        # then
        self.assertTrue(task.is_public)

    def test_order_num_specified_gets_set(self):
        # when
        task = self.ll.create_new_task(summary='task', current_user=self.admin,
                                       order_num=123)

        # then
        self.assertIsNotNone(task)
        self.assertEqual(123, task.order_num)
