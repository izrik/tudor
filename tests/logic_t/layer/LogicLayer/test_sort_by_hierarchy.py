#!/usr/bin/env python

import unittest

from tests.logic_t.layer.LogicLayer.util import generate_ll


class SortByHierarchyTest(unittest.TestCase):

    def setUp(self):
        self.ll = generate_ll(db_uri='sqlite://')
        self.pl = self.ll.pl

    def test_errant_leading_none_when_no_root_specified(self):
        # TODO: Fix this. The None should not be there. Only return tasks.

        # given
        t1 = self.pl.create_task('t1')
        t1.order_num = 1

        # when
        result = self.ll.sort_by_hierarchy([])

        # then
        self.assertEqual([None], result)

        # when
        result = self.ll.sort_by_hierarchy([t1])

        # then
        self.assertEqual([None, t1], result)

    def test_toplevel_tasks_get_sorted_by_descending_order_num(self):
        # given
        t1 = self.pl.create_task('t1')
        t1.order_num = 1
        t2 = self.pl.create_task('t2')
        t2.order_num = 2
        t3 = self.pl.create_task('t3')
        t3.order_num = 3

        properly_sorted_tasks = [None, t3, t2, t1]

        # when
        result = self.ll.sort_by_hierarchy([t1, t2, t3])

        # then
        self.assertEqual(properly_sorted_tasks, result)

        # when
        result = self.ll.sort_by_hierarchy([t1, t3, t2])

        # then
        self.assertEqual(properly_sorted_tasks, result)

        # when
        result = self.ll.sort_by_hierarchy([t2, t1, t3])

        # then
        self.assertEqual(properly_sorted_tasks, result)

        # when
        result = self.ll.sort_by_hierarchy([t2, t3, t1])

        # then
        self.assertEqual(properly_sorted_tasks, result)

        # when
        result = self.ll.sort_by_hierarchy([t3, t1, t2])

        # then
        self.assertEqual(properly_sorted_tasks, result)

        # when
        result = self.ll.sort_by_hierarchy([t3, t2, t1])

        # then
        self.assertEqual(properly_sorted_tasks, result)

    def test_child_tasks_only_sort_within_their_own_parent(self):
        # given
        t1 = self.pl.create_task('t1')
        t1.order_num = 1
        t1a = self.pl.create_task('t1a')
        t1a.parent = t1
        t1a.order_num = 2
        t1b = self.pl.create_task('t1b')
        t1b.parent = t1
        t1b.order_num = 3
        t2 = self.pl.create_task('t2')
        t2.order_num = 4
        t2a = self.pl.create_task('t2a')
        t2a.parent = t2
        t2a.order_num = 5
        t2b = self.pl.create_task('t2b')
        t2b.parent = t2
        t2b.order_num = 6

        # when
        result = self.ll.sort_by_hierarchy([t1, t1a, t1b, t2, t2a, t2b])

        # then
        self.assertEqual([None, t2, t2b, t2a, t1, t1b, t1a], result)

    def test_child_tasks_always_follow_their_parent(self):
        # given child task with higher order number than its parent
        t1 = self.pl.create_task('t1')
        t1.order_num = 1
        t2 = self.pl.create_task('t2')
        t2.parent = t1
        t2.order_num = 2

        # when
        result = self.ll.sort_by_hierarchy([t1, t2])

        # then
        self.assertEqual([None, t1, t2], result)

    def test_root_param_yields_only_root_and_its_descendants(self):
        # given a task with a child and other unrelated tasks
        t1 = self.pl.create_task('t1')
        t1.order_num = 1
        t2 = self.pl.create_task('t2')
        t2.order_num = 2
        t3 = self.pl.create_task('t3')
        t3.parent = t2
        t3.order_num = 3
        t4 = self.pl.create_task('t4')
        t4.order_num = 4

        # when
        result = self.ll.sort_by_hierarchy([t1, t2, t3, t4], root=t2)

        # then the other unrelated tasks are not returned
        self.assertEqual([t2, t3], result)
