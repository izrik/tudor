#!/usr/bin/env python

import unittest

from werkzeug.exceptions import Forbidden

from tests.logic_t.layer.LogicLayer.util import generate_ll


class AuthorizeUserForTaskTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_null_task_raises(self):
        # given
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # expect
        self.assertRaises(
            ValueError,
            self.ll.do_authorize_user_for_task,
            None, user, admin)

    def test_null_user_to_authorize_raises(self):
        # given
        task = self.pl.create_task('task')
        self.pl.add(task)
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # expect
        self.assertRaises(
            ValueError,
            self.ll.do_authorize_user_for_task,
            task, None, admin)

    def test_null_current_user_raises(self):
        # given
        task = self.pl.create_task('task')
        self.pl.add(task)
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        self.pl.commit()
        # expect
        self.assertRaises(
            ValueError,
            self.ll.do_authorize_user_for_task,
            task, user, None)

    def test_authorizes_user_for_task(self):
        # given
        task = self.pl.create_task('task')
        self.pl.add(task)
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        admin = self.pl.create_user('admin@example.com', is_admin=True)
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
        task = self.pl.create_task('task')
        self.pl.add(task)
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        task.users.append(user)
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
        task = self.pl.create_task('task')
        self.pl.add(task)
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        user2 = self.pl.create_user('user2@example.com')
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
        task = self.pl.create_task('task')
        self.pl.add(task)
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        user2 = self.pl.create_user('user2@example.com')
        self.pl.add(user2)
        task.users.append(user2)
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
        self.assertEqual({user, user2}, set(task.users))
