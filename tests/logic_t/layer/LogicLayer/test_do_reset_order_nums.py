#!/usr/bin/env python

import unittest

from tests.logic_t.layer.LogicLayer.util import generate_ll


class ResetOrderNumsTest(unittest.TestCase):

    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.admin = self.pl.create_user('name@example.org', None, True)
        self.pl.add(self.admin)
        self.user = self.pl.create_user('name2@example.org', None, False)
        self.pl.add(self.user)

    def test_no_tasks_does_nothing(self):

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual([], results)

    def test_errant_leading_none(self):
        # TODO: Fix this. The None should not be there. Only return tasks.

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual([], results)

    def test_tasks_in_order_stay_in_order(self):

        # given
        t1 = self.pl.create_task('t1')
        t1.order_num = 1
        t2 = self.pl.create_task('t2')
        t2.order_num = 2
        t3 = self.pl.create_task('t3')
        t3.order_num = 3

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual([t3, t2, t1], results)

    def test_order_nums_get_changed(self):

        # given
        t1 = self.pl.create_task('t1')
        t1.order_num = 1
        t2 = self.pl.create_task('t2')
        t2.order_num = 2
        t3 = self.pl.create_task('t3')
        t3.order_num = 3

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual(4, t1.order_num)
        self.assertEqual(6, t2.order_num)
        self.assertEqual(8, t3.order_num)

    def test_tasks_with_same_order_num_get_reordered_arbitrarily(self):

        # given
        t1 = self.pl.create_task('t1')
        t1.order_num = 0
        t2 = self.pl.create_task('t2')
        t2.order_num = 0
        t3 = self.pl.create_task('t3')
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
        t1 = self.pl.create_task('t1')
        t1.order_num = 1
        t2 = self.pl.create_task('t2')
        t2.order_num = 2
        t3 = self.pl.create_task('t3')
        t3.order_num = 3
        t4 = self.pl.create_task('t4')
        t4.order_num = 4
        t5 = self.pl.create_task('t5')
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
        self.assertEqual([t4, t3, t2], results)
        self.assertEqual(4, t2.order_num)
        self.assertEqual(6, t3.order_num)
        self.assertEqual(8, t4.order_num)
        self.assertEqual(1, t1.order_num)
        self.assertEqual(5, t5.order_num)
        self.assertNotEqual(t1.order_num, t2.order_num)
        self.assertNotEqual(t1.order_num, t3.order_num)
        self.assertNotEqual(t2.order_num, t3.order_num)
