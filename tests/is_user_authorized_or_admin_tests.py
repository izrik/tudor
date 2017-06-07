#!/usr/bin/env python

import unittest

from tudor import generate_app


class IsUserAuthorizedOrAdminTest(unittest.TestCase):

    task_ids = None

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.pl = app.pl
        self.db = app.pl.db
        self.pl.create_all()
        self.app = app
        self.ll = app.ll
        self.User = app.pl.User
        self.Task = app.pl.Task

    def test_unauthorized_nonadmin_cannot_access_task(self):

        # given
        task = self.Task('task')
        user = self.User('name@example.org')
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()

        # when
        result = self.ll.is_user_authorized_or_admin(task, user)

        # then
        self.assertFalse(result)

    def test_authorized_nonadmin_can_access_task(self):

        # given
        task = self.Task('task')
        user = self.User('name@example.org')
        self.pl.add(task)
        self.pl.add(user)
        task.users.append(user)
        self.pl.commit()

        # when
        result = self.ll.is_user_authorized_or_admin(task, user)

        # then
        self.assertTrue(result)

    def test_unauthorized_admin_can_access_task(self):

        # given
        task = self.Task('task')
        user = self.User('name@example.org', None, True)
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()

        # when
        result = self.ll.is_user_authorized_or_admin(task, user)

        # then
        self.assertTrue(result)

    def test_authorized_admin_can_access_task(self):

        # given
        task = self.Task('task')
        user = self.User('name@example.org', None, True)
        self.pl.add(task)
        self.pl.add(user)
        task.users.append(user)
        self.pl.commit()

        # when
        result = self.ll.is_user_authorized_or_admin(task, user)

        # then
        self.assertTrue(result)
