#!/usr/bin/env python

import unittest

import werkzeug.exceptions

from tests.logic_layer_t.util import generate_ll
from models.task import Task
from models.user import User


class CreateNewTaskTest(unittest.TestCase):

    def setUp(self):
        self.ll = generate_ll(db_uri='sqlite://')
        self.pl = self.ll.pl
        self.pl.create_all()
        self.admin = User('name@example.org', None, True)
        self.pl.add(self.admin)
        self.user = User('name2@example.org', None, False)
        self.pl.add(self.user)

    def test_admin_adds_first_task(self):
        # when
        task = self.ll.create_new_task(summary='t1', current_user=self.admin)

        # then
        self.assertIsNotNone(task)
        self.assertIsInstance(task, Task)
        self.assertEqual('t1', task.summary)
        self.assertIsNone(task.parent)

    def test_admin_adds_second_task(self):
        # given
        t1 = Task('t1')
        t1.order_num = 1

        self.pl.add(t1)

        # when
        task = self.ll.create_new_task(summary='t2', current_user=self.admin)

        # then
        self.assertIsNotNone(task)
        self.assertIsInstance(task, Task)
        self.assertEqual('t2', task.summary)
        self.assertIsNone(task.parent)

    def test_admin_adds_child_task_to_parent(self):
        # given
        p = Task('p')
        p.order_num = 1

        self.pl.add(p)
        self.pl.commit()

        # when
        task = self.ll.create_new_task(summary='c', parent_id=p.id,
                                       current_user=self.admin)

        # then
        self.assertIsNotNone(task)
        self.assertIsInstance(task, Task)
        self.assertEqual('c', task.summary)
        self.assertIs(p, task.parent)

    def test_user_adds_task_to_authorized_parent_succeeds(self):
        # given
        p = Task('p')
        p.order_num = 1
        p.users.append(self.user)

        self.pl.add(p)
        self.pl.commit()

        # when
        task = self.ll.create_new_task(summary='c', parent_id=p.id,
                                       current_user=self.user)

        # then
        self.assertIsNotNone(task)
        self.assertIsInstance(task, Task)
        self.assertEqual('c', task.summary)
        self.assertIs(p, task.parent)

    def test_user_adds_task_to_non_authorized_parent_raises_403(self):
        # given
        p = Task('p')
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
