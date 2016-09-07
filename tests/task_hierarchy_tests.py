#!/usr/bin/env python

import unittest

from tudor import generate_app


class GetAllDescendantsTest(unittest.TestCase):

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.db = app.ds.db
        self.db.create_all()
        self.app = app
        self.ll = app.ll
        self.Task = app.ds.Task

    def test_no_children_yields_given_tasks(self):

        # given
        task1 = self.Task('1')
        task2 = self.Task('2')
        task3 = self.Task('3')
        tasks = [task1, task2, task3]

        # when
        result = self.ll.get_tasks_and_all_descendants_from_tasks(tasks)

        # then
        self.assertEqual(len(tasks), len(result))
        self.assertSetEqual(set(tasks), set(result))

    def test_no_tasks_yields_empty_list(self):

        # when
        result = self.ll.get_tasks_and_all_descendants_from_tasks([])

        # then
        self.assertEqual(0, len(result))
        self.assertEqual([], result)
