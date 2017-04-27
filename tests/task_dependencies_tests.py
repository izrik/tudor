#!/usr/bin/env python

import unittest

from tudor import generate_app


class TaskDependenciesTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.db = self.app.ds.db
        self.db.create_all()
        self.Task = self.app.Task

    def test_setting_task_as_dependee_sets_other_task_as_depender(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')

        # precondition
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))

        # when
        t1.dependees.append(t2)

        # then
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependers)

    def test_setting_task_as_depender_sets_other_task_as_dependee(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')

        # precondition
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))

        # when
        t1.dependers.append(t2)

        # then
        self.assertEqual(1, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(1, len(t2.dependees))
        self.assertTrue(t2 in t1.dependers)
        self.assertTrue(t1 in t2.dependees)
