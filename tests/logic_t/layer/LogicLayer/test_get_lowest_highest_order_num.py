#!/usr/bin/env python

import unittest

from persistence.in_memory.models.task import Task
from tests.logic_t.layer.LogicLayer.util import generate_ll


class GetLowestHighestOrderNumTest(unittest.TestCase):

    def setUp(self):
        self.ll = generate_ll(db_uri='sqlite://')
        self.pl = self.ll.pl

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
        self.pl.commit()

        # when
        order_num = self.ll.get_lowest_order_num()

        # then
        self.assertEqual(10, order_num)

    def test_single_task_highest_returns_order_num(self):
        # given
        task = Task('task')
        task.order_num = 10
        self.pl.add(task)
        self.pl.commit()

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
        self.pl.commit()

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
        self.pl.commit()

        # when
        order_num = self.ll.get_highest_order_num()

        # then
        self.assertEqual(30, order_num)
