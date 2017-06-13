#!/usr/bin/env python

import unittest

import werkzeug.exceptions

from tudor import generate_app


class TaskSetDeletedTest(unittest.TestCase):

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.pl = app.pl
        self.pl.create_all()
        self.app = app
        self.ll = app.ll
        self.Task = app.pl.Task
        self.admin = app.pl.User('name@example.org', None, True)
        self.pl.add(self.admin)
        self.user = app.pl.User('name2@example.org', None, False)
        self.pl.add(self.user)

    def test_task_set_deleted_sets_is_deleted(self):
        # given
        t1 = self.Task('t1')

        self.pl.add(t1)
        self.pl.commit()

        # precondition
        self.assertFalse(t1.is_deleted)

        # when
        result = self.ll.task_set_deleted(t1.id, self.admin)

        # then
        self.assertIs(t1, result)
        self.assertTrue(t1.is_deleted)

    def test_unauthorized_user_raises(self):
        # given
        t1 = self.Task('t1')

        self.pl.add(t1)
        self.pl.commit()

        # precondition
        self.assertFalse(t1.is_deleted)

        # expect
        self.assertRaises(werkzeug.exceptions.Forbidden,
                          self.ll.task_set_deleted, t1.id, self.user)

    def test_non_existent_id_raises(self):
        # expect
        self.assertRaises(werkzeug.exceptions.NotFound,
                          self.ll.task_set_deleted, 101, self.admin)

    def test_idempotent(self):
        # given
        t1 = self.Task('t1')
        t1.is_deleted = True

        self.pl.add(t1)
        self.pl.commit()

        # precondition
        self.assertTrue(t1.is_deleted)

        # when
        result = self.ll.task_set_deleted(t1.id, self.admin)

        # then
        self.assertIs(t1, result)
        self.assertTrue(t1.is_deleted)
