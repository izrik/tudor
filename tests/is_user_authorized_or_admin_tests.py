#!/usr/bin/env python

import unittest

from tudor import generate_app


class IsUserAuthorizedOrAdminTest(unittest.TestCase):

    task_ids = None

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.db = app.ds.db
        self.db.create_all()
        self.app = app
        self.ll = app.ll
        self.User = app.ds.User
        self.Task = app.ds.Task
        self.TaskUserLink = app.ds.TaskUserLink

    def test_unauthorized_nonadmin_cannot_access_task(self):

        # given
        task = self.Task('task')
        user = self.User('name@example.org')
        self.db.session.add(task)
        self.db.session.add(user)
        self.db.session.commit()

        # when
        result = self.ll.is_user_authorized_or_admin(task, user)

        # then
        self.assertFalse(result)

    def test_authorized_nonadmin_can_access_task(self):

        # given
        task = self.Task('task')
        user = self.User('name@example.org')
        self.db.session.add(task)
        self.db.session.add(user)
        self.db.session.commit()
        tul = self.TaskUserLink(task.id, user.id)
        self.db.session.add(tul)
        self.db.session.commit()

        # when
        result = self.ll.is_user_authorized_or_admin(task, user)

        # then
        self.assertTrue(result)

    def test_unauthorized_admin_can_access_task(self):

        # given
        task = self.Task('task')
        user = self.User('name@example.org', None, True)
        self.db.session.add(task)
        self.db.session.add(user)
        self.db.session.commit()

        # when
        result = self.ll.is_user_authorized_or_admin(task, user)

        # then
        self.assertTrue(result)

    def test_authorized_admin_can_access_task(self):

        # given
        task = self.Task('task')
        user = self.User('name@example.org', None, True)
        self.db.session.add(task)
        self.db.session.add(user)
        self.db.session.commit()
        tul = self.TaskUserLink(task.id, user.id)
        self.db.session.add(tul)
        self.db.session.commit()

        # when
        result = self.ll.is_user_authorized_or_admin(task, user)

        # then
        self.assertTrue(result)