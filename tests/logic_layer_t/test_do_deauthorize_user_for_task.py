#!/usr/bin/env python

import unittest

from werkzeug.exceptions import Forbidden, NotFound, Conflict

from models.task import Task
from models.user import User
from tests.logic_layer_t.util import generate_ll


class DeauthorizeUserForTaskTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_null_task_id_raises(self):
        # given
        user = User('user@example.com')
        self.pl.add(user)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # expect
        self.assertRaises(
            ValueError,
            self.ll.do_deauthorize_user_for_task,
            None, user.id, admin)

    def test_null_user_id_to_authorize_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # expect
        self.assertRaises(
            ValueError,
            self.ll.do_deauthorize_user_for_task,
            task.id, None, admin)

    def test_null_current_user_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        user = User('user@example.com')
        self.pl.add(user)
        self.pl.commit()
        # expect
        self.assertRaises(
            ValueError,
            self.ll.do_deauthorize_user_for_task,
            task.id, user.id, None)

    def test_deauthorizes_user_for_task(self):
        # given
        task = Task('task')
        self.pl.add(task)
        user = User('user@example.com')
        self.pl.add(user)
        task.users.add(user)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        task.users.add(admin)
        self.pl.commit()
        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # when
        result = self.ll.do_deauthorize_user_for_task(task.id, user.id, admin)
        self.pl.commit()
        # then
        self.assertIs(result, task)
        self.assertNotIn(user, task.users)
        self.assertNotIn(task, user.tasks)

    def test_task_not_found_raises(self):
        # given
        user = User('user@example.com')
        self.pl.add(user)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition
        self.assertIsNone(self.pl.get_task(1))
        # expect
        self.assertRaises(
            NotFound,
            self.ll.do_deauthorize_user_for_task,
            1, user.id, admin)

    def test_user_not_found_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition
        self.assertIsNone(self.pl.get_task(admin.id + 1))
        # expect
        self.assertRaises(
            NotFound,
            self.ll.do_deauthorize_user_for_task,
            1, admin.id + 1, admin)

    def test_authorized_non_admin_current_user_deauthorizes_user(self):
        # given
        task = Task('task')
        self.pl.add(task)
        user = User('user@example.com')
        self.pl.add(user)
        task.users.add(user)
        user2 = User('user2@example.com')
        self.pl.add(user2)
        task.users.add(user2)
        self.pl.commit()
        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # when
        result = self.ll.do_deauthorize_user_for_task(task.id, user.id, user2)
        self.pl.commit()
        # then
        self.assertIs(result, task)
        self.assertNotIn(user, task.users)
        self.assertNotIn(task, user.tasks)

    def test_non_authorized_non_admin_current_user_deauthorizes_user(self):
        # given
        task = Task('task')
        self.pl.add(task)
        user = User('user@example.com')
        self.pl.add(user)
        task.users.add(user)
        user2 = User('user2@example.com')
        self.pl.add(user2)
        self.pl.commit()
        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # when
        self.assertRaises(
            Forbidden,
            self.ll.do_deauthorize_user_for_task,
            task.id, user.id, user2)

    def test_last_authorized_user_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        user = User('user@example.com')
        self.pl.add(user)
        task.users.add(user)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # when
        self.assertRaises(
            Conflict,
            self.ll.do_deauthorize_user_for_task,
            task.id, user.id, admin)

    def test_user_not_already_authorized_silently_ignores(self):
        # given
        task = Task('task')
        self.pl.add(task)
        user = User('user@example.com')
        self.pl.add(user)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        task.users.add(admin)
        self.pl.commit()
        # precondition
        self.assertNotIn(user, task.users)
        self.assertNotIn(task, user.tasks)
        # when
        result = self.ll.do_deauthorize_user_for_task(task.id, user.id, admin)
        self.pl.commit()
        # then
        self.assertIs(result, task)
        self.assertNotIn(user, task.users)
        self.assertNotIn(task, user.tasks)

    def test_neither_user_nor_current_user_authorized_silently_ignores(self):
        # given
        task = Task('task')
        self.pl.add(task)
        user = User('user@example.com')
        self.pl.add(user)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition
        self.assertNotIn(user, task.users)
        self.assertNotIn(task, user.tasks)
        self.assertEqual(0, len(task.users))
        # when
        result = self.ll.do_deauthorize_user_for_task(task.id, user.id, admin)
        self.pl.commit()
        # then
        self.assertIs(result, task)
        self.assertNotIn(user, task.users)
        self.assertNotIn(task, user.tasks)
        self.assertEqual(0, len(task.users))
