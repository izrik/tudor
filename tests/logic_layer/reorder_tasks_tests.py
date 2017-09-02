#!/usr/bin/env python

import unittest

from tudor import generate_app
from models.task import Task


def generate_ll(db_uri='sqlite://'):
    app = generate_app(db_uri=db_uri)
    return app.ll


class ReorderTasksTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_tasks_in_order_order_nums_change(self):
        # given
        t1 = Task('t1')
        t1.order_num = 1
        t2 = Task('t2')
        t2.order_num = 2
        t3 = Task('t3')
        t3.order_num = 3
        # when
        self.ll.reorder_tasks([t1, t2, t3])
        # then
        self.assertEqual(6, t1.order_num)
        self.assertEqual(4, t2.order_num)
        self.assertEqual(2, t3.order_num)

    def test_tasks_in_different_order_order_nums_change(self):
        # given
        t1 = Task('t1')
        t1.order_num = 1
        t2 = Task('t2')
        t2.order_num = 2
        t3 = Task('t3')
        t3.order_num = 3
        # when
        self.ll.reorder_tasks([t2, t3, t1])
        # then
        self.assertEqual(2, t1.order_num)
        self.assertEqual(6, t2.order_num)
        self.assertEqual(4, t3.order_num)
