#!/usr/bin/env python

import unittest

from werkzeug.exceptions import Forbidden

from models.task import Task
from models.user import User
from tests.logic_layer_t.util import generate_ll


class AuthorizeUserForTaskTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll(db_uri='sqlite://')
        self.pl = self.ll.pl
        self.pl.create_all()

    def test_null_task_raises(self):
        # given
        user = User('user@example.com')
        self.pl.add(user)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # expect
        self.assertRaises(
            ValueError,
            self.ll.do_authorize_user_for_task,
            None, user, admin)

    def test_null_user_to_authorize_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # expect
        self.assertRaises(
            ValueError,
            self.ll.do_authorize_user_for_task,
            task, None, admin)

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
            self.ll.do_authorize_user_for_task,
            task, user, None)

    def test_authorizes_user_for_task(self):
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
        # when
        result = self.ll.do_authorize_user_for_task(task, user, admin)
        # then
        self.assertIs(result, task)
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

    def test_user_already_authorized_silently_ignored(self):
        # given
        task = Task('task')
        self.pl.add(task)
        user = User('user@example.com')
        self.pl.add(user)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        task.users.add(user)
        self.pl.commit()
        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # when
        result = self.ll.do_authorize_user_for_task(task, user, admin)
        # then
        self.assertIs(result, task)
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

    def test_current_user_not_authorized_not_admin_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        user = User('user@example.com')
        self.pl.add(user)
        user2 = User('user2@example.com')
        self.pl.add(user2)
        self.pl.commit()
        # precondition
        self.assertNotIn(user2, task.users)
        self.assertNotIn(task, user2.tasks)
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.do_authorize_user_for_task,
            task, user, user2)

    def test_current_user_authorized_not_admin_authorizes_user(self):
        # given
        task = Task('task')
        self.pl.add(task)
        user = User('user@example.com')
        self.pl.add(user)
        user2 = User('user2@example.com')
        self.pl.add(user2)
        task.users.add(user2)
        self.pl.commit()
        # precondition
        self.assertIn(user2, task.users)
        self.assertIn(task, user2.tasks)
        # when
        result = self.ll.do_authorize_user_for_task(task, user, user2)
        # then
        self.assertIs(result, task)
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        self.assertEqual({user, user2}, task.users)
