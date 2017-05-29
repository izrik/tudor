#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound, Forbidden

from tudor import generate_app


class LogicLayerTaskTagsTest(unittest.TestCase):

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.db = app.ds.db
        self.db.create_all()
        self.Task = app.ds.Task
        self.Tag = app.ds.Tag
        self.ll = app.ll

    def test_no_tasks_lowest_returns_none(self):
        # precondition
        self.assertEqual(0, self.Task.query.count())

        # when
        order_num = self.ll.get_lowest_order_num()

        # then
        self.assertIsNone(order_num)

    def test_no_tasks_highest_returns_none(self):
        # precondition
        self.assertEqual(0, self.Task.query.count())

        # when
        order_num = self.ll.get_highest_order_num()

        # then
        self.assertIsNone(order_num)

    def test_single_task_lowest_returns_order_num(self):
        # given
        task = self.Task('task')
        task.order_num = 1
        self.db.session.add(task)

        # when
        order_num = self.ll.get_lowest_order_num()

        # then
        self.assertEqual(1, order_num)

    def test_single_task_highest_returns_order_num(self):
        # given
        task = self.Task('task')
        task.order_num = 1
        self.db.session.add(task)

        # when
        order_num = self.ll.get_highest_order_num()

        # then
        self.assertEqual(1, order_num)

    def test_many_tasks_lowest_returns_lowest(self):
        # given
        t1 = self.Task('t1')
        t1.order_num = 1
        t2 = self.Task('t2')
        t2.order_num = 2
        t3 = self.Task('t3')
        t3.order_num = 3
        self.db.session.add(t1)
        self.db.session.add(t2)
        self.db.session.add(t3)

        # when
        order_num = self.ll.get_lowest_order_num()

        # then
        self.assertEqual(1, order_num)

    def test_many_tasks_highest_returns_highest(self):
        # given
        t1 = self.Task('t1')
        t1.order_num = 1
        t2 = self.Task('t2')
        t2.order_num = 2
        t3 = self.Task('t3')
        t3.order_num = 3
        self.db.session.add(t1)
        self.db.session.add(t2)
        self.db.session.add(t3)

        # when
        order_num = self.ll.get_highest_order_num()

        # then
        self.assertEqual(3, order_num)
