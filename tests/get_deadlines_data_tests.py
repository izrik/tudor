#!/usr/bin/env python

import unittest

from tudor import generate_app


class GetDeadlinesDataTest(unittest.TestCase):

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.pl = app.pl
        self.pl.create_all()
        self.app = app
        self.ll = app.ll
        self.Task = app.pl.Task
        self.admin = app.pl.User('name@example.org', None, True)
        self.pl.add(self.admin)
        self.user = app.pl.User('name2@example.org', None, False)
        self.pl.add(self.user)

    def test_only_tasks_with_deadlines_are_returned(self):
        # given
        t1 = self.Task('t1')
        t1.order_num = 1
        t2 = self.Task('t2', deadline='2016-12-01')
        t2.order_num = 2

        self.pl.add(t1)
        self.pl.add(t2)

        # when
        result = self.ll.get_deadlines_data(self.admin)

        # then
        self.assertEqual(1, len(result))
        self.assertIn('deadline_tasks', result)
        self.assertEqual([t2], result['deadline_tasks'])

    def test_tasks_are_sorted_by_deadline_earliest_first(self):
        # given
        t1 = self.Task('t1', deadline='2016-12-01')
        t1.order_num = 1
        t2 = self.Task('t2', deadline='2016-12-02')
        t2.order_num = 2

        self.pl.add(t1)
        self.pl.add(t2)

        # when
        result = self.ll.get_deadlines_data(self.admin)

        # then
        self.assertEqual(1, len(result))
        self.assertIn('deadline_tasks', result)
        self.assertEqual([t1, t2], result['deadline_tasks'])

    def test_only_tasks_for_the_current_non_admin_user_are_returned(self):
        # given
        t1 = self.Task('t1', deadline='2016-12-01')
        t1.order_num = 1
        t2 = self.Task('t2', deadline='2016-12-01')
        t2.order_num = 2

        self.pl.add(t1)
        self.pl.add(t2)

        t2.users.append(self.user)

        self.pl.commit()

        # when
        result = self.ll.get_deadlines_data(self.user)

        # then
        self.assertEqual(1, len(result))
        self.assertIn('deadline_tasks', result)
        self.assertEqual([t2], result['deadline_tasks'])

    def test_all_tasks_are_returned_for_admin_user(self):
        # given
        t1 = self.Task('t1', deadline='2016-12-01')
        t1.order_num = 1
        t2 = self.Task('t2', deadline='2016-12-02')
        t2.order_num = 2

        self.pl.add(t1)
        self.pl.add(t2)

        t2.users.append(self.user)

        self.pl.commit()

        # when
        result = self.ll.get_deadlines_data(self.admin)

        # then
        self.assertEqual(1, len(result))
        self.assertIn('deadline_tasks', result)
        self.assertSetEqual({t1, t2}, set(result['deadline_tasks']))
