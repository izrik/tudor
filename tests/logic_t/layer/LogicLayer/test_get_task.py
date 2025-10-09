#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound

from tests.logic_t.layer.LogicLayer.util import generate_ll


class GetTaskDataTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_admin_user_gets_single_task(self):
        # given a task
        task = self.pl.create_task('task')
        self.pl.add(task)
        # and an admin user to attempt the retrieval
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition
        self.assertEqual(1, self.pl.count_tasks())
        self.assertNotIn(admin, task.users)
        self.assertNotIn(task, admin.tasks)
        # when
        result = self.ll.get_task(task.id, admin)
        # then
        self.assertEqual(task.id, result.id)

    def test_authorized_user_gets_single_task(self):
        # given a task
        task = self.pl.create_task('task')
        self.pl.add(task)
        # and an admin user to attempt the retrieval
        user = self.pl.create_user('user@example.com', is_admin=False)
        self.pl.add(user)
        task.users.append(user)
        self.pl.commit()
        # precondition
        self.assertEqual(1, self.pl.count_tasks())
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # when
        result = self.ll.get_task(task.id, user)
        # then
        self.assertEqual(task.id, result.id)

    def test_non_admin_user_not_authorized_returns_none(self):
        # given a task
        task = self.pl.create_task('task')
        self.pl.add(task)
        # and an admin user to attempt the retrieval
        user = self.pl.create_user('user@example.com', is_admin=False)
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertEqual(1, self.pl.count_tasks())
        self.assertNotIn(user, task.users)
        self.assertNotIn(task, user.tasks)
        self.assertIsNotNone(self.pl.get_task(task.id))
        # when
        result = self.ll.get_task(task.id, user)
        # then
        self.assertIsNone(result)

    def test_non_admin_user_public_task_returns_task(self):
        # given a task
        task = self.pl.create_task('task', is_public=True)
        self.pl.add(task)
        # and an admin user to attempt the retrieval
        user = self.pl.create_user('user@example.com', is_admin=False)
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertEqual(1, self.pl.count_tasks())
        self.assertNotIn(user, task.users)
        self.assertNotIn(task, user.tasks)
        self.assertIsNotNone(self.pl.get_task(task.id))
        # when
        result = self.ll.get_task(task.id, user)
        # then
        self.assertEqual(task.id, result.id)

    def test_task_not_found_raises(self):
        # given a user to attempt the retrieval
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertIsNone(self.pl.get_task(123))
        # expect
        self.assertRaises(
            NotFound,
            self.ll.get_task,
            123, user)
