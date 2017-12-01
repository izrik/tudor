#!/usr/bin/env python

import unittest

from models.task import Task
from models.user import User
from tests.logic_layer_t.util import generate_ll


class ResetOrderNumsTest(unittest.TestCase):

    def setUp(self):
        self.ll = generate_ll(db_uri='sqlite://')
        self.pl = self.ll.pl
        self.admin = User('name@example.org', None, True)
        self.pl.add(self.admin)
        self.user = User('name2@example.org', None, False)
        self.pl.add(self.user)

    def test_no_tasks_does_nothing(self):

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual([None], results)

    def test_errant_leading_none(self):
        # TODO: Fix this. The None should not be there. Only return tasks.

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual([None], results)

    def test_tasks_in_order_stay_in_order(self):

        # given
        t1 = Task('t1')
        t1.order_num = 1
        t2 = Task('t2')
        t2.order_num = 2
        t3 = Task('t3')
        t3.order_num = 3

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual([None, t3, t2, t1], results)

    def test_order_nums_get_changed(self):

        # given
        t1 = Task('t1')
        t1.order_num = 1
        t2 = Task('t2')
        t2.order_num = 2
        t3 = Task('t3')
        t3.order_num = 3

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual(6, t1.order_num)
        self.assertEqual(8, t2.order_num)
        self.assertEqual(10, t3.order_num)

    def test_tasks_with_same_order_num_get_reordered_arbitrarily(self):

        # given
        t1 = Task('t1')
        t1.order_num = 0
        t2 = Task('t2')
        t2.order_num = 0
        t3 = Task('t3')
        t3.order_num = 0

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertNotEqual(t1.order_num, t2.order_num)
        self.assertNotEqual(t1.order_num, t3.order_num)
        self.assertNotEqual(t2.order_num, t3.order_num)

    def test_only_tasks_user_is_authorized_for_are_changed(self):

        # given
        t1 = Task('t1')
        t1.order_num = 1
        t2 = Task('t2')
        t2.order_num = 2
        t3 = Task('t3')
        t3.order_num = 3
        t4 = Task('t4')
        t4.order_num = 4
        t5 = Task('t5')
        t5.order_num = 5

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.add(t4)
        self.pl.add(t5)

        t2.users.append(self.user)
        t3.users.append(self.user)
        t4.users.append(self.user)

        self.pl.commit()

        # when
        results = self.ll.do_reset_order_nums(self.user)

        # then
        self.assertEqual([None, t4, t3, t2], results)
        self.assertEqual(6, t2.order_num)
        self.assertEqual(8, t3.order_num)
        self.assertEqual(10, t4.order_num)
        self.assertEqual(1, t1.order_num)
        self.assertEqual(5, t5.order_num)
        self.assertNotEqual(t1.order_num, t2.order_num)
        self.assertNotEqual(t1.order_num, t3.order_num)
        self.assertNotEqual(t2.order_num, t3.order_num)
