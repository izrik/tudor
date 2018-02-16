#!/usr/bin/env python

import unittest

import werkzeug.exceptions

from persistence.in_memory.models.task import Task
from persistence.in_memory.models.user import User
from tests.logic_t.layer.LogicLayer.util import generate_ll


class TaskSetDoneTest(unittest.TestCase):

    def setUp(self):
        self.ll = generate_ll(db_uri='sqlite://')
        self.pl = self.ll.pl

        self.admin = User('name@example.org', None, True)
        self.pl.add(self.admin)
        self.user = User('name2@example.org', None, False)
        self.pl.add(self.user)

    def test_task_set_done_sets_is_done(self):
        # given
        t1 = Task('t1')

        self.pl.add(t1)
        self.pl.commit()

        # precondition
        self.assertFalse(t1.is_done)

        # when
        result = self.ll.task_set_done(t1.id, self.admin)

        # then
        self.assertIs(t1, result)
        self.assertTrue(t1.is_done)

    def test_unauthorized_user_raises(self):
        # given
        t1 = Task('t1')

        self.pl.add(t1)
        self.pl.commit()

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
        t1 = Task('t1')
        t1.is_done = True

        self.pl.add(t1)
        self.pl.commit()

        # precondition
        self.assertTrue(t1.is_done)

        # when
        result = self.ll.task_set_done(t1.id, self.admin)

        # then
        self.assertIs(t1, result)
        self.assertTrue(t1.is_done)