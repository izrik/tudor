#!/usr/bin/env python

import unittest

from werkzeug.exceptions import BadRequest, NotFound, Forbidden

from tudor import generate_app


class TaskPrioritizeTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.db = self.app.ds.db
        self.db.create_all()
        self.Task = self.app.Task

    def test_setting_task_as_before_sets_other_task_as_after(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')

        # precondition
        self.assertEqual(0, len(t1.prioritize_before))
        self.assertEqual(0, len(t1.prioritize_after))
        self.assertEqual(0, len(t2.prioritize_before))
        self.assertEqual(0, len(t2.prioritize_after))

        # when
        t1.prioritize_before.append(t2)

        # then
        self.assertEqual(1, len(t1.prioritize_before))
        self.assertEqual(0, len(t1.prioritize_after))
        self.assertEqual(0, len(t2.prioritize_before))
        self.assertEqual(1, len(t2.prioritize_after))
        self.assertTrue(t2 in t1.prioritize_before)
        self.assertTrue(t1 in t2.prioritize_after)

    def test_setting_task_as_after_sets_other_task_as_before(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')

        # precondition
        self.assertEqual(0, len(t1.prioritize_before))
        self.assertEqual(0, len(t1.prioritize_after))
        self.assertEqual(0, len(t2.prioritize_before))
        self.assertEqual(0, len(t2.prioritize_after))

        # when
        t1.prioritize_after.append(t2)

        # then
        self.assertEqual(0, len(t1.prioritize_before))
        self.assertEqual(1, len(t1.prioritize_after))
        self.assertEqual(1, len(t2.prioritize_before))
        self.assertEqual(0, len(t2.prioritize_after))
        self.assertTrue(t2 in t1.prioritize_after)
        self.assertTrue(t1 in t2.prioritize_before)
