#!/usr/bin/env python

import unittest

from werkzeug.exceptions import Forbidden

from models.task import Task
from models.user import User
from util import generate_ll


class PurgeAllDeletedTasksTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_purges_all_deleted_tasks(self):
        # given
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        t1 = Task('t1')
        self.pl.add(t1)
        t1.is_deleted = True
        t2 = Task('t2')
        self.pl.add(t2)
        t3 = Task('t3')
        self.pl.add(t3)
        t3.is_deleted = True
        self.pl.commit()
        # precondition
        self.assertTrue(t1.is_deleted)
        self.assertFalse(t2.is_deleted)
        self.assertTrue(t3.is_deleted)
        self.assertEqual(3, self.pl.count_tasks())
        self.assertEqual(2, self.pl.count_tasks(is_deleted=True))
        self.assertEqual(1, self.pl.count_tasks(is_deleted=False))
        self.assertTrue(admin.is_admin)
        # when
        result = self.ll.purge_all_deleted_tasks(admin)
        # then
        self.assertEqual(1, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tasks(is_deleted=True))
        self.assertEqual(1, self.pl.count_tasks(is_deleted=False))
        self.assertIs(t2, list(self.pl.get_tasks())[0])
        # and
        self.assertEqual(2, result)

    def test_non_admin_raises(self):
        # given
        user = User('user@example.com', is_admin=False)
        self.pl.add(user)
        task = Task('task')
        self.pl.add(task)
        task.is_deleted = True
        self.pl.commit()
        # precondition
        self.assertFalse(user.is_admin)
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.purge_all_deleted_tasks,
            user)

    def test_task_not_deleted_then_not_purged(self):
        # given
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        # precondition
        self.assertFalse(task.is_deleted)
        self.assertEqual(1, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tasks(is_deleted=True))
        self.assertEqual(1, self.pl.count_tasks(is_deleted=False))
        self.assertTrue(admin.is_admin)
        # when
        result = self.ll.purge_all_deleted_tasks(admin)
        # then
        self.assertEqual(1, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tasks(is_deleted=True))
        self.assertEqual(1, self.pl.count_tasks(is_deleted=False))
        # and
        self.assertEqual(0, result)