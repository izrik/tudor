#!/usr/bin/env python

import unittest

import werkzeug.exceptions

from tudor import generate_app


class ResetOrderNumsTest(unittest.TestCase):

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.db = app.pl.db
        self.db.create_all()
        self.app = app
        self.ll = app.ll
        self.Task = app.pl.Task
        self.admin = app.pl.User('name@example.org', None, True)
        self.db.session.add(self.admin)
        self.user = app.pl.User('name2@example.org', None, False)
        self.db.session.add(self.user)

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
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual([None, t3, t2, t1], results)

    def test_order_nums_get_changed(self):

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
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertEqual(6, t1.order_num)
        self.assertEqual(8, t2.order_num)
        self.assertEqual(10, t3.order_num)

    def test_tasks_with_same_order_num_get_reordered_arbitrarily(self):

        # given
        t1 = self.Task('t1')
        t1.order_num = 0
        t2 = self.Task('t2')
        t2.order_num = 0
        t3 = self.Task('t3')
        t3.order_num = 0

        self.db.session.add(t1)
        self.db.session.add(t2)
        self.db.session.add(t3)

        # when
        results = self.ll.do_reset_order_nums(self.admin)

        # then
        self.assertNotEqual(t1.order_num, t2.order_num)
        self.assertNotEqual(t1.order_num, t3.order_num)
        self.assertNotEqual(t2.order_num, t3.order_num)

    def test_only_tasks_user_is_authorized_for_are_changed(self):

        # given
        t1 = self.Task('t1')
        t1.order_num = 1
        t2 = self.Task('t2')
        t2.order_num = 2
        t3 = self.Task('t3')
        t3.order_num = 3
        t4 = self.Task('t4')
        t4.order_num = 4
        t5 = self.Task('t5')
        t5.order_num = 5

        self.db.session.add(t1)
        self.db.session.add(t2)
        self.db.session.add(t3)
        self.db.session.add(t4)
        self.db.session.add(t5)

        t2.users.append(self.user)
        t3.users.append(self.user)
        t4.users.append(self.user)

        self.db.session.commit()

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
