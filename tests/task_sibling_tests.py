#!/usr/bin/env python

import unittest

from tudor import generate_app


class TaskSiblingTest(unittest.TestCase):

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

    def test_gets_tasks_with_same_parent(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')
        t2.parent = t1
        t2.order_num = 2
        t3 = self.Task('t3')
        t3.parent = t1
        t3.order_num = 3

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        result = t2.get_siblings()

        # then
        self.assertIsNotNone(result)
        result2 = list(result)
        self.assertEqual(2, len(result2))
        self.assertIs(t2, result2[0])
        self.assertIs(t3, result2[1])

    def test_gets_done_tasks(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')
        t2.parent = t1
        t2.order_num = 2
        t3 = self.Task('t3')
        t3.parent = t1
        t3.is_done = True
        t3.order_num = 3

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        result = t2.get_siblings()

        # then
        self.assertIsNotNone(result)
        result2 = list(result)
        self.assertEqual(2, len(result2))
        self.assertIs(t2, result2[0])
        self.assertIs(t3, result2[1])

    def test_includes_deleted_by_default(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')
        t2.parent = t1
        t3 = self.Task('t3')
        t3.parent = t1
        t3.is_deleted = True

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        result = t2.get_siblings()

        # then
        self.assertIsNotNone(result)
        result2 = list(result)
        self.assertEqual(2, len(result2))
        self.assertIs(t2, result2[0])
        self.assertIs(t3, result2[1])

    def test_ignores_deleted_tasks_when_indicated(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')
        t2.parent = t1
        t3 = self.Task('t3')
        t3.parent = t1
        t3.is_deleted = True

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        result = t2.get_siblings(include_deleted=False)

        # then
        self.assertIsNotNone(result)
        result2 = list(result)
        self.assertEqual(1, len(result2))
        self.assertIs(t2, result2[0])

    def test_ordered_yields_siblings_sorted_by_order_num(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')
        t2.parent = t1
        t2.order_num = 2
        t3 = self.Task('t3')
        t3.parent = t1
        t3.order_num = 3

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        result = t2.get_siblings(ordered=False)

        # then
        self.assertIsNotNone(result)
        result2 = list(result)
        self.assertEqual(2, len(result2))
        self.assertIs(t2, result2[0])
        self.assertIs(t3, result2[1])

        # when
        result = t2.get_siblings(ordered=True)

        # then
        self.assertIsNotNone(result)
        result2 = list(result)
        self.assertEqual(2, len(result2))
        self.assertIs(t3, result2[0])
        self.assertIs(t2, result2[1])

    def test_gets_toplevel_tasks_with_same_parent(self):
        # given
        t2 = self.Task('t2')
        t2.order_num = 2
        t3 = self.Task('t3')
        t3.order_num = 3

        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        result = t2.get_siblings()

        # then
        self.assertIsNotNone(result)
        result2 = list(result)
        self.assertEqual(2, len(result2))
        self.assertIs(t2, result2[0])
        self.assertIs(t3, result2[1])

    def test_gets_toplevel_done_tasks(self):
        # given
        t2 = self.Task('t2')
        t2.order_num = 2
        t3 = self.Task('t3')
        t3.is_done = True
        t3.order_num = 3

        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        result = t2.get_siblings()

        # then
        self.assertIsNotNone(result)
        result2 = list(result)
        self.assertEqual(2, len(result2))
        self.assertIs(t2, result2[0])
        self.assertIs(t3, result2[1])

    def test_includes_toplevel_deleted_by_default(self):
        # given
        t2 = self.Task('t2')
        t3 = self.Task('t3')
        t3.is_deleted = True

        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        result = t2.get_siblings()

        # then
        self.assertIsNotNone(result)
        result2 = list(result)
        self.assertEqual(2, len(result2))
        self.assertIs(t2, result2[0])
        self.assertIs(t3, result2[1])

    def test_ignores_toplevel_deleted_tasks_when_indicated(self):
        # given
        t2 = self.Task('t2')
        t3 = self.Task('t3')
        t3.is_deleted = True

        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        result = t2.get_siblings(include_deleted=False)

        # then
        self.assertIsNotNone(result)
        result2 = list(result)
        self.assertEqual(1, len(result2))
        self.assertIs(t2, result2[0])

    def test_ordered_yields_toplevel_siblings_sorted_by_order_num(self):
        # given
        t2 = self.Task('t2')
        t2.order_num = 2
        t3 = self.Task('t3')
        t3.order_num = 3

        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.commit()

        # when
        result = t2.get_siblings(ordered=False)

        # then
        self.assertIsNotNone(result)
        result2 = list(result)
        self.assertEqual(2, len(result2))
        self.assertIs(t2, result2[0])
        self.assertIs(t3, result2[1])

        # when
        result = t2.get_siblings(ordered=True)

        # then
        self.assertIsNotNone(result)
        result2 = list(result)
        self.assertEqual(2, len(result2))
        self.assertIs(t3, result2[0])
        self.assertIs(t2, result2[1])
