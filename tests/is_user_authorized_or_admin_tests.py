#!/usr/bin/env python

import unittest

from tudor import generate_app
from models.task import Task
from models.user import User


class IsUserAuthorizedOrAdminTest(unittest.TestCase):

    task_ids = None

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.pl = app.pl
        self.pl.create_all()
        self.app = app
        self.ll = app.ll

    def test_unauthorized_nonadmin_cannot_access_task(self):

        # given
        task = Task('task')
        user = User('name@example.org')
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()

        # when
        result = self.ll.is_user_authorized_or_admin(task, user)

        # then
        self.assertFalse(result)

    def test_authorized_nonadmin_can_access_task(self):

        # given
        task = Task('task')
        user = User('name@example.org')
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
        task = Task('task')
        user = User('name@example.org', None, True)
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()

        # when
        result = self.ll.is_user_authorized_or_admin(task, user)

        # then
        self.assertTrue(result)

    def test_authorized_admin_can_access_task(self):

        # given
        task = Task('task')
        user = User('name@example.org', None, True)
        self.pl.add(task)
        self.pl.add(user)
        task.users.append(user)
        self.pl.commit()

        # when
        result = self.ll.is_user_authorized_or_admin(task, user)

        # then
        self.assertTrue(result)
