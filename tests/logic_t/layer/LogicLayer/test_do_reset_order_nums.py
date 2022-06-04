#!/usr/bin/env python

import unittest

from datetime import datetime

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

    def test_children_are_ordered_before_parents(self):
        # given
        p = self.pl.create_task('p')
        c1 = self.pl.create_task('c1')
        c1.parent = p
        c1.order_num = 1
        c2 = self.pl.create_task('c2')
        c2.parent = p
        c2.order_num = 2
        c3 = self.pl.create_task('c3')
        c3.parent = p
        c3.order_num = 3

        self.pl.add(p)
        self.pl.add(c1)
        self.pl.add(c2)
        self.pl.add(c3)

        self.pl.commit()

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual([c3, c2, c1, p], results)
        self.assertEqual(10, c3.order_num)
        self.assertEqual(8, c2.order_num)
        self.assertEqual(6, c1.order_num)
        self.assertEqual(4, p.order_num)

    def test_a_task_is_ordered_after_its_dependees(self):
        # given
        task = self.pl.create_task('task')
        task.order_num = 100
        d1 = self.pl.create_task('d1')
        task.dependees.append(d1)
        d1.order_num = 1
        d2 = self.pl.create_task('d2')
        task.dependees.append(d2)
        d2.order_num = 2
        d3 = self.pl.create_task('d3')
        task.dependees.append(d3)
        d3.order_num = 3

        self.pl.add(task)
        self.pl.add(d1)
        self.pl.add(d2)
        self.pl.add(d3)

        self.pl.commit()

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual([d3, d2, d1, task], results)
        self.assertEqual(10, d3.order_num)
        self.assertEqual(8, d2.order_num)
        self.assertEqual(6, d1.order_num)
        self.assertEqual(4, task.order_num)

    def test_tasks_with_deadline_are_ordered_earliest_first(self):
        # given
        t1 = self.pl.create_task('t1')
        t1.deadline = datetime(2018, 1, 1)
        t2 = self.pl.create_task('t2')
        t2.deadline = datetime(2018, 1, 2)
        t3 = self.pl.create_task('t3')
        t3.deadline = datetime(2018, 1, 3)

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual([t1, t2, t3], results)
        self.assertEqual(8, t1.order_num)
        self.assertEqual(6, t2.order_num)
        self.assertEqual(4, t3.order_num)

    def test_tasks_with_deadline_are_ordered_ignoring_order_num(self):
        # given
        t1 = self.pl.create_task('t1')
        t1.deadline = datetime(2018, 1, 1)
        t1.order_num = 1
        t2 = self.pl.create_task('t2')
        t2.deadline = datetime(2018, 1, 2)
        t2.order_num = 2
        t3 = self.pl.create_task('t3')
        t3.deadline = datetime(2018, 1, 3)
        t3.order_num = 3

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual([t1, t2, t3], results)
        self.assertEqual(8, t1.order_num)
        self.assertEqual(6, t2.order_num)
        self.assertEqual(4, t3.order_num)

    def test_tasks_with_deadline_are_ordered_before_tasks_without(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2', deadline=datetime(2018, 1, 1))
        t3 = self.pl.create_task('t3', deadline=datetime(2018, 1, 2))

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)

        self.pl.commit()

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual([t2, t3, t1], results)
        self.assertEqual(4, t1.order_num)
        self.assertEqual(8, t2.order_num)
        self.assertEqual(6, t3.order_num)

    def test_a_task_is_ordered_after_its_prioritize_befores(self):
        # given
        task = self.pl.create_task('task')
        task.order_num = 100
        pb1 = self.pl.create_task('pb1')
        task.prioritize_before.append(pb1)
        pb1.order_num = 1
        pb2 = self.pl.create_task('pb2')
        task.prioritize_before.append(pb2)
        pb2.order_num = 2
        pb3 = self.pl.create_task('pb3')
        task.prioritize_before.append(pb3)
        pb3.order_num = 3

        self.pl.add(task)
        self.pl.add(pb1)
        self.pl.add(pb2)
        self.pl.add(pb3)

        self.pl.commit()

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual([pb3, pb2, pb1, task], results)
        self.assertEqual(10, pb3.order_num)
        self.assertEqual(8, pb2.order_num)
        self.assertEqual(6, pb1.order_num)
        self.assertEqual(4, task.order_num)
