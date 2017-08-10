#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound, Forbidden

from tudor import generate_app
from models.task import Task
from models.tag import Tag


class GetLowestHighestOrderNumTest(unittest.TestCase):

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.pl = app.pl
        self.pl.create_all()
        self.ll = app.ll

    def test_no_tasks_lowest_returns_none(self):
        # precondition
        self.assertEqual(0, self.pl.count_tasks())

        # when
        order_num = self.ll.get_lowest_order_num()

        # then
        self.assertIsNone(order_num)

    def test_no_tasks_highest_returns_none(self):
        # precondition
        self.assertEqual(0, self.pl.count_tasks())

        # when
        order_num = self.ll.get_highest_order_num()

        # then
        self.assertIsNone(order_num)

    def test_single_task_lowest_returns_order_num(self):
        # given
        task = Task('task')
        task.order_num = 10
        self.pl.add(task)

        # when
        order_num = self.ll.get_lowest_order_num()

        # then
        self.assertEqual(10, order_num)

    def test_single_task_highest_returns_order_num(self):
        # given
        task = Task('task')
        task.order_num = 10
        self.pl.add(task)

        # when
        order_num = self.ll.get_highest_order_num()

        # then
        self.assertEqual(10, order_num)

    def test_many_tasks_lowest_returns_lowest(self):
        # given
        t1 = Task('t1')
        t1.order_num = 10
        t2 = Task('t2')
        t2.order_num = 20
        t3 = Task('t3')
        t3.order_num = 30
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)

        # when
        order_num = self.ll.get_lowest_order_num()

        # then
        self.assertEqual(10, order_num)

    def test_many_tasks_highest_returns_highest(self):
        # given
        t1 = Task('t1')
        t1.order_num = 10
        t2 = Task('t2')
        t2.order_num = 20
        t3 = Task('t3')
        t3.order_num = 30
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)

        # when
        order_num = self.ll.get_highest_order_num()

        # then
        self.assertEqual(30, order_num)
