#!/usr/bin/env python

import unittest
from decimal import Decimal

from tests.logic_t.layer.LogicLayer.util import generate_ll


class GetTaskOrderByTest(unittest.TestCase):

    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_id_has_no_tie_breaker(self):
        # when
        result = self.ll.get_task_order_by('id', 'desc')
        # then
        self.assertEqual([[self.pl.TASK_ID, self.pl.DESCENDING]], result)

    def test_other_fields_break_ties_by_id(self):
        # when
        result = self.ll.get_task_order_by('summary', 'asc')
        # then
        self.assertEqual([[self.pl.SUMMARY, self.pl.ASCENDING],
                          [self.pl.TASK_ID, self.pl.ASCENDING]], result)

    def test_all_fields_are_handled(self):
        for field in self.ll.TASK_SORT_FIELDS:
            for order in self.ll.TASK_SORT_ORDERS:
                self.assertTrue(self.ll.get_task_order_by(field, order))

    def test_unknown_field_raises(self):
        self.assertRaises(ValueError, self.ll.get_task_order_by,
                          'bogus', 'asc')

    def test_unknown_order_raises(self):
        self.assertRaises(ValueError, self.ll.get_task_order_by,
                          'id', 'sideways')


class TaskSortingTest(unittest.TestCase):

    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.admin = self.pl.create_user('name@example.org', None, True)
        self.pl.add(self.admin)
        self.parent = self.pl.create_task('parent')
        self.pl.add(self.parent)
        self.tag = self.pl.create_tag('tag')
        self.pl.add(self.tag)
        self.pl.commit()

    def create_task(self, summary, order_num, deadline, cost, parent=None):
        task = self.pl.create_task(summary, deadline=deadline,
                                   expected_cost=cost)
        task.order_num = order_num
        if parent is not None:
            task.parent = parent
        task.tags.append(self.tag)
        self.pl.add(task)
        return task

    def create_tasks(self, parent=None):
        b = self.create_task('b', 1, '2016-12-03', Decimal('2.00'), parent)
        c = self.create_task('c', 2, '2016-12-01', Decimal('3.00'), parent)
        a = self.create_task('a', 3, '2016-12-02', Decimal('1.00'), parent)
        self.pl.commit()
        return a, b, c

    def test_index_defaults_to_order_num_descending(self):
        # given
        a, b, c = self.create_tasks()
        # when
        data = self.ll.get_index_data(True, True, self.admin)
        # then
        self.assertEqual([a, c, b, self.parent], data['tasks'])
        self.assertEqual('order_num', data['sort'])
        self.assertEqual('desc', data['order'])

    def test_index_sorts_by_summary(self):
        # given
        a, b, c = self.create_tasks()
        # when
        asc = self.ll.get_index_data(True, True, self.admin,
                                     sort='summary', order='asc')
        desc = self.ll.get_index_data(True, True, self.admin,
                                      sort='summary', order='desc')
        # then
        self.assertEqual([a, b, c, self.parent], asc['tasks'])
        self.assertEqual([self.parent, c, b, a], desc['tasks'])
        self.assertEqual('summary', desc['sort'])
        self.assertEqual('desc', desc['order'])

    def test_task_children_sort_by_expected_cost(self):
        # given
        a, b, c = self.create_tasks(parent=self.parent)
        # when
        data = self.ll.get_task_data(self.parent.id, self.admin,
                                     sort='expected_cost', order='asc')
        # then
        self.assertEqual([a, b, c], data['descendants'])

    def test_task_children_sort_by_order_num_ascending(self):
        # given
        a, b, c = self.create_tasks(parent=self.parent)
        # when
        data = self.ll.get_task_data(self.parent.id, self.admin,
                                     sort='order_num', order='asc')
        # then
        self.assertEqual([b, c, a], data['descendants'])

    def test_tag_tasks_sort_by_id(self):
        # given
        a, b, c = self.create_tasks()
        # when
        data = self.ll.get_tag_data(self.tag.id, self.admin, sort='id',
                                    order='desc')
        # then
        self.assertEqual([a, c, b], data['tasks'])

    def test_deadlines_sort_by_deadline_descending(self):
        # given
        a, b, c = self.create_tasks()
        # when
        data = self.ll.get_deadlines_data(self.admin, sort='deadline',
                                          order='desc')
        # then
        self.assertEqual([b, a, c], data['deadline_tasks'])
