#!/usr/bin/env python

import unittest

from werkzeug.exceptions import Forbidden, NotFound

from tests.logic_t.layer.LogicLayer.util import generate_ll


class AuthorizeUserForTaskByIdTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_authorizes_user(self):
        # given a task
        task = self.pl.create_task('task')
        self.pl.add(task)
        # and a user to authorize
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        # and an admin user to attempt the authorization
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition: the user is not authorized for the task
        self.assertNotIn(user, task.users)
        self.assertNotIn(task, user.tasks)
        # when
        result = self.ll.do_authorize_user_for_task_by_id(
            task.id, user.id, admin)
        # then the user is now authorized for the task
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # and the task is returned
        self.assertIs(result, task)

    def test_task_id_none_raises(self):
        # given a user to try to authorize
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        # and an admin user to attempt the authorization
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition: there are no tasks
        self.assertEqual(0, self.pl.count_tasks())
        # and the user is not authorized for anything
        self.assertEqual(0, len(user.tasks))
        # expect
        self.assertRaises(
            ValueError,
            self.ll.do_authorize_user_for_task_by_id,
            None, user.id, admin)
        # and the user was not authorized for anything
        self.assertEqual(0, len(user.tasks))

    def test_task_not_found_raises(self):
        # given a user to try to authorize
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        # and an admin user to attempt the authorization
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition: there are no tasks
        self.assertEqual(0, self.pl.count_tasks())
        # and the user is not authorized for anything
        self.assertEqual(0, len(user.tasks))
        # expect
        self.assertRaises(
            NotFound,
            self.ll.do_authorize_user_for_task_by_id,
            1, user.id, admin)
        # and the user was not authorized for anything
        self.assertEqual(0, len(user.tasks))

    def test_id_none_raises(self):
        # given a task
        task = self.pl.create_task('task')
        self.pl.add(task)
        # and an admin user to attempt the authorization
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition no users are authorized for the task
        self.assertEqual(0, len(task.users))
        # expect
        self.assertRaises(
            ValueError,
            self.ll.do_authorize_user_for_task_by_id,
            task.id, None, admin)
        # and no users are authorized for the task
        self.assertEqual(0, len(task.users))

    def test_id_not_found_raises(self):
        # given a task
        task = self.pl.create_task('task')
        self.pl.add(task)
        # and an admin user to attempt the authorization
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition: there are no users with that id
        self.assertIsNone(self.pl.get_user(admin.id + 1))
        # and no users are authorized for the task
        self.assertEqual(0, len(task.users))
        # expect
        self.assertRaises(
            NotFound,
            self.ll.do_authorize_user_for_task_by_id,
            task.id, admin.id + 1, admin)
        # and no users are authorized for the task
        self.assertEqual(0, len(task.users))

    def test_current_user_not_allowed_raises(self):
        # given a task
        task = self.pl.create_task('task')
        self.pl.add(task)
        # and a user to authorize
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        # and a non-admin user to attempt the authorization
        non_admin = self.pl.create_user('user2@example.com', is_admin=False)
        self.pl.add(non_admin)
        self.pl.commit()
        # precondition: the current_user is not authorized or admin
        self.assertNotIn(non_admin, task.users)
        self.assertNotIn(task, non_admin.tasks)
        self.assertFalse(non_admin.is_admin)
        # when
        self.assertRaises(
            Forbidden,
            self.ll.do_authorize_user_for_task_by_id,
            task.id, user.id, non_admin)
        # and no users are authorized for the task
        self.assertEqual(0, len(task.users))

    def test_current_user_is_authorized_non_admin_then_authorizes_user(self):
        # given a task
        task = self.pl.create_task('task')
        self.pl.add(task)
        # and a user to authorize
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        # and a non-admin user to attempt the authorization
        non_admin = self.pl.create_user('user2@example.com', is_admin=False)
        self.pl.add(non_admin)
        task.users.append(non_admin)
        self.pl.commit()
        # precondition: the current_user is authorized for the task
        self.assertIn(non_admin, task.users)
        self.assertIn(task, non_admin.tasks)
        # and the current_user is not an admin
        self.assertFalse(non_admin.is_admin)
        # when
        result = self.ll.do_authorize_user_for_task_by_id(
            task.id, user.id, non_admin)
        # then the user is now authorized for the task
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # and the task is returned
        self.assertIs(result, task)
