#!/usr/bin/env python

import unittest

from tests.util import generate_test_app

from models.task_user_ops import TaskUserOps


class IsUserAuthorizedOrAdminTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_test_app().pl

    def test_unauthorized_nonadmin_cannot_access_task(self):
        # given
        task = self.pl.DbTask('task')
        user = self.pl.DbUser('name@example.org')
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()
        # when
        result = TaskUserOps.is_user_authorized_or_admin(task, user)
        # then
        self.assertFalse(result)

    def test_authorized_nonadmin_can_access_task(self):
        # given
        task = self.pl.DbTask('task')
        user = self.pl.DbUser('name@example.org')
        self.pl.add(task)
        self.pl.add(user)
        task.users.append(user)
        self.pl.commit()
        # when
        result = TaskUserOps.is_user_authorized_or_admin(task, user)
        # then
        self.assertTrue(result)

    def test_unauthorized_admin_can_access_task(self):
        # given
        task = self.pl.DbTask('task')
        user = self.pl.DbUser('name@example.org', None, True)
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()
        # when
        result = TaskUserOps.is_user_authorized_or_admin(task, user)
        # then
        self.assertTrue(result)

    def test_authorized_admin_can_access_task(self):
        # given
        task = self.pl.DbTask('task')
        user = self.pl.DbUser('name@example.org', None, True)
        self.pl.add(task)
        self.pl.add(user)
        task.users.append(user)
        self.pl.commit()
        # when
        result = TaskUserOps.is_user_authorized_or_admin(task, user)
        # then
        self.assertTrue(result)
