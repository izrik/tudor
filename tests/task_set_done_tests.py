#!/usr/bin/env python

import unittest

import werkzeug.exceptions

from tudor import generate_app


class TaskSetDoneTest(unittest.TestCase):

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.db = app.ds.db
        self.db.create_all()
        self.app = app
        self.ll = app.ll
        self.Task = app.ds.Task
        self.admin = app.ds.User('name@example.org', None, True)
        self.db.session.add(self.admin)
        self.user = app.ds.User('name2@example.org', None, False)
        self.db.session.add(self.user)

    def test_task_set_done_sets_is_done(self):
        # given
        t1 = self.Task('t1')

        self.db.session.add(t1)
        self.db.session.commit()

        # precondition
        self.assertFalse(t1.is_done)

        # when
        result = self.ll.task_set_done(t1.id, self.admin)

        # then
        self.assertIs(t1, result)
        self.assertTrue(t1.is_done)

    def test_unauthorized_user_raises(self):
        # given
        t1 = self.Task('t1')

        self.db.session.add(t1)
        self.db.session.commit()

        # precondition
        self.assertFalse(t1.is_done)

        # expect
        self.assertRaises(werkzeug.exceptions.Forbidden, self.ll.task_set_done,
                          t1.id, self.user)

    def test_non_existent_id_raises(self):
        # expect
        self.assertRaises(werkzeug.exceptions.NotFound, self.ll.task_set_done,
                          101, self.admin)

    def test_idempotent(self):
        # given
        t1 = self.Task('t1')
        t1.is_done = True

        self.db.session.add(t1)
        self.db.session.commit()

        # precondition
        self.assertTrue(t1.is_done)

        # when
        result = self.ll.task_set_done(t1.id, self.admin)

        # then
        self.assertIs(t1, result)
        self.assertTrue(t1.is_done)
