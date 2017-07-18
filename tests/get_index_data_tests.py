#!/usr/bin/env python

import unittest

from tudor import generate_app
from models.task import Task
from models.user import User
from models.tag import Tag


class GetIndexDataTest(unittest.TestCase):

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.pl = app.pl
        self.pl.create_all()
        self.app = app
        self.ll = app.ll
        self.admin = User('name@example.org', None, True)
        self.pl.add(self.admin)
        self.user = User('name2@example.org', None, False)
        self.pl.add(self.user)

    def test_get_index_data_returns_tasks_and_tags(self):

        # given
        t1 = Task('t1')
        t1.order_num = 1
        t2 = Task('t2')
        t2.order_num = 2
        t3 = Task('t3')
        t3.parent = t2
        t3.order_num = 3
        t4 = Task('t4')
        t4.order_num = 4

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.add(t4)

        tag1 = Tag('tag1')

        self.pl.add(tag1)

        self.pl.commit()

        # when
        data = self.ll.get_index_data(True, True, self.admin)

        # then
        self.assertEqual([t4, t2, t1], list(data['tasks']))
        self.assertEqual([tag1], data['all_tags'])

    def test_show_deleted_returns_as_is(self):
        # when
        data = self.ll.get_index_data(True, True, self.admin)

        # then
        self.assertTrue(data['show_deleted'])
        # when
        data = self.ll.get_index_data(False, True, self.admin)

        # then
        self.assertFalse(data['show_deleted'])

    def test_show_done_returns_as_is(self):
        # when
        data = self.ll.get_index_data(True, True, self.admin)

        # then
        self.assertTrue(data['show_done'])
        # when
        data = self.ll.get_index_data(True, False, self.admin)

        # then
        self.assertFalse(data['show_done'])

    def test_get_index_data_only_yields_tasks_the_user_is_authorized_for(self):

        # given
        t1 = Task('t1')
        t1.order_num = 1
        t2 = Task('t2')
        t2.order_num = 2

        self.pl.add(t1)
        self.pl.add(t2)

        t2.users.append(self.user)

        self.pl.commit()

        # when
        data = self.ll.get_index_data(True, True, self.user)

        # then
        self.assertEqual([t2], list(data['tasks']))

    def test_get_index_hierarchy_data_returns_tasks_and_tags(self):

        # given
        t1 = Task('t1')
        t1.order_num = 1
        t2 = Task('t2')
        t2.order_num = 2
        t3 = Task('t3')
        t3.parent = t2
        t3.order_num = 3
        t4 = Task('t4')
        t4.order_num = 4

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.add(t4)

        tag1 = Tag('tag1')

        self.pl.add(tag1)

        self.pl.commit()

        # when
        data = self.ll.get_index_hierarchy_data(True, True, self.admin)

        # then
        self.assertEqual([None, t4, t2, t3, t1], data['tasks_h'])
        self.assertEqual([tag1], data['all_tags'])

    def test_hierarchy_show_deleted_returns_as_is(self):
        # when
        data = self.ll.get_index_hierarchy_data(True, True, self.admin)

        # then
        self.assertTrue(data['show_deleted'])
        # when
        data = self.ll.get_index_hierarchy_data(False, True, self.admin)

        # then
        self.assertFalse(data['show_deleted'])

    def test_hierarchy_show_done_returns_as_is(self):
        # when
        data = self.ll.get_index_hierarchy_data(True, True, self.admin)

        # then
        self.assertTrue(data['show_done'])
        # when
        data = self.ll.get_index_hierarchy_data(True, False, self.admin)

        # then
        self.assertFalse(data['show_done'])

    def test_hierarchy_only_yields_tasks_user_is_authorized_for(self):

        # given
        t1 = Task('t1')
        t1.order_num = 1
        t2 = Task('t2')
        t2.order_num = 2

        self.pl.add(t1)
        self.pl.add(t2)

        t2.users.append(self.user)

        self.pl.commit()

        # when
        data = self.ll.get_index_hierarchy_data(True, True, self.user)

        # then
        self.assertEqual([None, t2], data['tasks_h'])

    def test_hierarchy_returns_descendants(self):

        # given
        t1 = Task('t1')
        t1.order_num = 1
        t2 = Task('t2')
        t2.order_num = 2
        t3 = Task('t3')
        t3.parent = t2
        t3.order_num = 3
        t4 = Task('t4')
        t4.order_num = 4

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.add(t4)

        self.pl.commit()

        # when
        data = self.ll.get_index_hierarchy_data(True, True, self.admin)

        # then
        self.assertEqual([None, t4, t2, t3, t1], data['tasks_h'])
        tasks = data['tasks_h']
        self.assertEqual(0, tasks[1].depth)
        self.assertEqual(0, tasks[2].depth)
        self.assertEqual(1, tasks[3].depth)
        self.assertEqual(0, tasks[4].depth)
        self.assertEqual(0, t1.depth)
        self.assertEqual(0, t2.depth)
        self.assertEqual(1, t3.depth)
        self.assertEqual(0, t4.depth)

    def test_non_hierarchy_returns_only_top_level_tasks(self):

        # given
        t1 = Task('t1')
        t1.order_num = 1
        t2 = Task('t2')
        t2.order_num = 2
        t3 = Task('t3')
        t3.parent = t2
        t3.order_num = 3
        t4 = Task('t4')
        t4.order_num = 4

        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.add(t4)

        self.pl.commit()

        # when
        data = self.ll.get_index_data(True, True, self.admin)

        # then
        tasks = list(data['tasks'])
        self.assertEqual([t4, t2, t1], tasks)
        self.assertEqual(0, tasks[0].depth)
        self.assertEqual(0, tasks[1].depth)
        self.assertEqual(0, tasks[2].depth)
        self.assertEqual(0, t1.depth)
        self.assertEqual(0, t2.depth)
        self.assertEqual(0, t4.depth)

        # depth on the child remains at 0
        self.assertEqual(0, t3.depth)
