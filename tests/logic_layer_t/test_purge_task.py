#!/usr/bin/env python

import unittest

from werkzeug.exceptions import Forbidden

from models.task import Task
from models.user import User
from util import generate_ll


class PurgeTaskTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_purges_task(self):
        # given
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        task = Task('task')
        self.pl.add(task)
        task.is_deleted = True
        self.pl.commit()
        # precondition
        self.assertTrue(task.is_deleted)
        self.assertEqual(1, self.pl.count_tasks())
        self.assertTrue(admin.is_admin)
        # when
        self.ll.purge_task(task, admin)
        # then
        self.assertEqual(0, self.pl.count_tasks())

    def test_non_admin_raises(self):
        # given
        user = User('user@example.com', is_admin=False)
        self.pl.add(user)
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        # precondition
        self.assertFalse(user.is_admin)
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.purge_task,
            task, user)

    def test_task_none_raises(self):
        # given
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # expect
        self.assertRaises(
            ValueError,
            self.ll.purge_task,
            None, admin)

    def test_task_not_deleted_raises(self):
        # given
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        # precondition
        self.assertFalse(task.is_deleted)
        self.assertEqual(1, self.pl.count_tasks())
        self.assertTrue(admin.is_admin)
        # expect
        self.assertRaises(
            Exception,
            self.ll.purge_task,
            task, admin)
