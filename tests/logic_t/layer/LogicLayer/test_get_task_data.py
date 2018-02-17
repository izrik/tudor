#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound, Forbidden, Unauthorized

from persistence.in_memory.models.user import User, GuestUser
from persistence.sqlalchemy.layer import Pager
from util import generate_ll


class GetTaskDataTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.user = User('name@example.com')
        self.guest = GuestUser()
        self.task = self.pl.create_task('task')
        self.task.id = 1
        self.pl.add(self.task)
        self.pl.commit()

    def test_id_none_raises(self):
        self.assertRaises(
            NotFound,
            self.ll.get_task_data,
            None, self.user)

    def test_non_existent_task(self):
        # given
        self.pl.add(self.user)
        self.pl.commit()
        # expect
        self.assertRaises(
            NotFound,
            self.ll.get_task_data,
            self.task.id + 1, self.user)

    def test_user_none_raises(self):
        # given
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Unauthorized,
            self.ll.get_task_data,
            self.task.id, None)

    def test_user_guest_raises(self):
        # given
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Unauthorized,
            self.ll.get_task_data,
            self.task.id,
            self.guest)

    def test_not_authorized_user_raises(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.get_task_data,
            self.task.id, self.user)

    def test_authorized_user_does_not_raise(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.add(self.user)
        self.pl.commit()
        # when
        result = self.ll.get_task_data(self.task.id, self.user)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(3, len(result))
        self.assertIn('task', result)
        self.assertIsNotNone(result['task'])
        self.assertIs(self.task, result['task'])
        self.assertIn('descendants', result)
        self.assertEqual([self.task], result['descendants'])
        self.assertIn('pager', result)
        self.assertIsNotNone(result['pager'])
        self.assertIsInstance(result['pager'], Pager)

    def test_guest_user_can_see_public_tasks(self):
        # given
        self.task.is_public = True
        self.pl.commit()
        # when
        result = self.ll.get_task_data(self.task.id, self.user)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(3, len(result))

    def test_not_authorized_admin_can_see_tasks(self):
        # given
        admin = User('admin@example.com', '', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition
        self.assertNotIn(admin, self.task.users)
        self.assertNotIn(self.task, admin.tasks)
        # when
        result = self.ll.get_task_data(self.task.id, admin)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(3, len(result))

    # TODO: is_done and is_deleted

    def create_and_add_task(self, summary, order_num=None, parent=None,
                            user=None):
        task = self.pl.create_task(summary)
        if order_num:
            task.order_num = order_num
        if parent:
            task.parent = parent
        if user:
            task.users.add(user)
        self.pl.add(task)
        return task

    def test_no_paging_info_specified_yields_page_one_with_twenty_items(self):
        # given
        self.pl.add(self.user)
        t1 = self.create_and_add_task('t1', 1, self.task, self.user)
        t2 = self.create_and_add_task('t2', 2, self.task, self.user)
        t3 = self.create_and_add_task('t3', 3, self.task, self.user)
        t4 = self.create_and_add_task('t4', 4, self.task, self.user)
        t5 = self.create_and_add_task('t5', 5, self.task, self.user)
        t6 = self.create_and_add_task('t6', 6, self.task, self.user)
        t7 = self.create_and_add_task('t7', 7, self.task, self.user)
        t8 = self.create_and_add_task('t8', 8, self.task, self.user)
        t9 = self.create_and_add_task('t9', 9, self.task, self.user)
        t10 = self.create_and_add_task('t10', 10, self.task, self.user)
        t11 = self.create_and_add_task('t11', 11, self.task, self.user)
        t12 = self.create_and_add_task('t12', 12, self.task, self.user)
        t13 = self.create_and_add_task('t13', 13, self.task, self.user)
        t14 = self.create_and_add_task('t14', 14, self.task, self.user)
        t15 = self.create_and_add_task('t15', 15, self.task, self.user)
        t16 = self.create_and_add_task('t16', 16, self.task, self.user)
        t17 = self.create_and_add_task('t17', 17, self.task, self.user)
        t18 = self.create_and_add_task('t18', 18, self.task, self.user)
        t19 = self.create_and_add_task('t19', 19, self.task, self.user)
        t20 = self.create_and_add_task('t20', 20, self.task, self.user)
        t21 = self.create_and_add_task('t21', 21, self.task, self.user)
        self.task.users.add(self.user)
        self.pl.commit()
        # when
        result = self.ll.get_task_data(self.task.id, self.user)
        # then
        pager = result['pager']
        self.assertEqual(1, pager.page)
        self.assertEqual(2, pager.pages)
        self.assertEqual(20, pager.per_page)

    def test_page_num_one_yields_page_one(self):
        # given
        self.pl.add(self.user)
        t1 = self.create_and_add_task('t1', 1, self.task, self.user)
        t2 = self.create_and_add_task('t2', 2, self.task, self.user)
        t3 = self.create_and_add_task('t3', 3, self.task, self.user)
        t4 = self.create_and_add_task('t4', 4, self.task, self.user)
        t5 = self.create_and_add_task('t5', 5, self.task, self.user)
        t6 = self.create_and_add_task('t6', 6, self.task, self.user)
        t7 = self.create_and_add_task('t7', 7, self.task, self.user)
        t8 = self.create_and_add_task('t8', 8, self.task, self.user)
        t9 = self.create_and_add_task('t9', 9, self.task, self.user)
        t10 = self.create_and_add_task('t10', 10, self.task, self.user)
        t11 = self.create_and_add_task('t11', 11, self.task, self.user)
        t12 = self.create_and_add_task('t12', 12, self.task, self.user)
        t13 = self.create_and_add_task('t13', 13, self.task, self.user)
        t14 = self.create_and_add_task('t14', 14, self.task, self.user)
        t15 = self.create_and_add_task('t15', 15, self.task, self.user)
        t16 = self.create_and_add_task('t16', 16, self.task, self.user)
        t17 = self.create_and_add_task('t17', 17, self.task, self.user)
        t18 = self.create_and_add_task('t18', 18, self.task, self.user)
        t19 = self.create_and_add_task('t19', 19, self.task, self.user)
        t20 = self.create_and_add_task('t20', 20, self.task, self.user)
        t21 = self.create_and_add_task('t21', 21, self.task, self.user)
        self.task.users.add(self.user)
        self.pl.commit()
        # when
        result = self.ll.get_task_data(self.task.id, self.user, page_num=1)
        # then
        pager = result['pager']
        self.assertEqual(1, pager.page)
        self.assertEqual(2, pager.pages)
        self.assertEqual(20, pager.per_page)
        self.assertEqual([t21, t20, t19, t18, t17, t16, t15, t14, t13, t12,
                          t11, t10, t9, t8, t7, t6, t5, t4, t3, t2],
                         pager.items)

    def test_page_num_two_yields_page_two(self):
        # given
        self.pl.add(self.user)
        t1 = self.create_and_add_task('t1', 1, self.task, self.user)
        t2 = self.create_and_add_task('t2', 2, self.task, self.user)
        t3 = self.create_and_add_task('t3', 3, self.task, self.user)
        t4 = self.create_and_add_task('t4', 4, self.task, self.user)
        t5 = self.create_and_add_task('t5', 5, self.task, self.user)
        t6 = self.create_and_add_task('t6', 6, self.task, self.user)
        t7 = self.create_and_add_task('t7', 7, self.task, self.user)
        t8 = self.create_and_add_task('t8', 8, self.task, self.user)
        t9 = self.create_and_add_task('t9', 9, self.task, self.user)
        t10 = self.create_and_add_task('t10', 10, self.task, self.user)
        t11 = self.create_and_add_task('t11', 11, self.task, self.user)
        t12 = self.create_and_add_task('t12', 12, self.task, self.user)
        t13 = self.create_and_add_task('t13', 13, self.task, self.user)
        t14 = self.create_and_add_task('t14', 14, self.task, self.user)
        t15 = self.create_and_add_task('t15', 15, self.task, self.user)
        t16 = self.create_and_add_task('t16', 16, self.task, self.user)
        t17 = self.create_and_add_task('t17', 17, self.task, self.user)
        t18 = self.create_and_add_task('t18', 18, self.task, self.user)
        t19 = self.create_and_add_task('t19', 19, self.task, self.user)
        t20 = self.create_and_add_task('t20', 20, self.task, self.user)
        t21 = self.create_and_add_task('t21', 21, self.task, self.user)
        self.task.users.add(self.user)
        self.pl.commit()
        # when
        result = self.ll.get_task_data(self.task.id, self.user, page_num=2)
        # then
        pager = result['pager']
        self.assertEqual(2, pager.page)
        self.assertEqual(2, pager.pages)
        self.assertEqual(20, pager.per_page)
        self.assertEqual([t1], pager.items)

    def test_page_num_zero_raises(self):
        # given
        self.pl.add(self.user)
        t1 = self.create_and_add_task('t1', 1, self.task, self.user)
        t2 = self.create_and_add_task('t2', 2, self.task, self.user)
        t3 = self.create_and_add_task('t3', 3, self.task, self.user)
        t4 = self.create_and_add_task('t4', 4, self.task, self.user)
        t5 = self.create_and_add_task('t5', 5, self.task, self.user)
        t6 = self.create_and_add_task('t6', 6, self.task, self.user)
        t7 = self.create_and_add_task('t7', 7, self.task, self.user)
        t8 = self.create_and_add_task('t8', 8, self.task, self.user)
        t9 = self.create_and_add_task('t9', 9, self.task, self.user)
        t10 = self.create_and_add_task('t10', 10, self.task, self.user)
        t11 = self.create_and_add_task('t11', 11, self.task, self.user)
        t12 = self.create_and_add_task('t12', 12, self.task, self.user)
        t13 = self.create_and_add_task('t13', 13, self.task, self.user)
        t14 = self.create_and_add_task('t14', 14, self.task, self.user)
        t15 = self.create_and_add_task('t15', 15, self.task, self.user)
        t16 = self.create_and_add_task('t16', 16, self.task, self.user)
        t17 = self.create_and_add_task('t17', 17, self.task, self.user)
        t18 = self.create_and_add_task('t18', 18, self.task, self.user)
        t19 = self.create_and_add_task('t19', 19, self.task, self.user)
        t20 = self.create_and_add_task('t20', 20, self.task, self.user)
        t21 = self.create_and_add_task('t21', 21, self.task, self.user)
        self.task.users.add(self.user)
        self.pl.commit()
        result = None
        # expect
        self.assertRaises(
            ValueError,
            self.ll.get_task_data,
            self.task.id, self.user, page_num=0)

    def test_page_num_not_integer_raises(self):
        # given
        self.pl.add(self.user)
        t1 = self.create_and_add_task('t1', 1, self.task, self.user)
        t2 = self.create_and_add_task('t2', 2, self.task, self.user)
        t3 = self.create_and_add_task('t3', 3, self.task, self.user)
        t4 = self.create_and_add_task('t4', 4, self.task, self.user)
        t5 = self.create_and_add_task('t5', 5, self.task, self.user)
        t6 = self.create_and_add_task('t6', 6, self.task, self.user)
        t7 = self.create_and_add_task('t7', 7, self.task, self.user)
        t8 = self.create_and_add_task('t8', 8, self.task, self.user)
        t9 = self.create_and_add_task('t9', 9, self.task, self.user)
        t10 = self.create_and_add_task('t10', 10, self.task, self.user)
        t11 = self.create_and_add_task('t11', 11, self.task, self.user)
        t12 = self.create_and_add_task('t12', 12, self.task, self.user)
        t13 = self.create_and_add_task('t13', 13, self.task, self.user)
        t14 = self.create_and_add_task('t14', 14, self.task, self.user)
        t15 = self.create_and_add_task('t15', 15, self.task, self.user)
        t16 = self.create_and_add_task('t16', 16, self.task, self.user)
        t17 = self.create_and_add_task('t17', 17, self.task, self.user)
        t18 = self.create_and_add_task('t18', 18, self.task, self.user)
        t19 = self.create_and_add_task('t19', 19, self.task, self.user)
        t20 = self.create_and_add_task('t20', 20, self.task, self.user)
        t21 = self.create_and_add_task('t21', 21, self.task, self.user)
        self.task.users.add(self.user)
        self.pl.commit()
        result = None
        # expect
        self.assertRaises(
            TypeError,
            self.ll.get_task_data,
            self.task.id, self.user, page_num='1')

    def test_tasks_per_page_yields_that_many_per_page(self):
        # given
        self.pl.add(self.user)
        t1 = self.create_and_add_task('t1', 1, self.task, self.user)
        t2 = self.create_and_add_task('t2', 2, self.task, self.user)
        t3 = self.create_and_add_task('t3', 3, self.task, self.user)
        t4 = self.create_and_add_task('t4', 4, self.task, self.user)
        t5 = self.create_and_add_task('t5', 5, self.task, self.user)
        t6 = self.create_and_add_task('t6', 6, self.task, self.user)
        self.task.users.add(self.user)
        self.pl.commit()
        # when
        result = self.ll.get_task_data(self.task.id, self.user,
                                       tasks_per_page=5)
        # then
        pager = result['pager']
        self.assertEqual(1, pager.page)
        self.assertEqual(2, pager.pages)
        self.assertEqual(5, pager.per_page)
        self.assertEqual([t6, t5, t4, t3, t2], pager.items)

    def test_tasks_per_page_one_yields_one(self):
        # given
        self.pl.add(self.user)
        t1 = self.create_and_add_task('t1', 1, self.task, self.user)
        t2 = self.create_and_add_task('t2', 2, self.task, self.user)
        t3 = self.create_and_add_task('t3', 3, self.task, self.user)
        t4 = self.create_and_add_task('t4', 4, self.task, self.user)
        t5 = self.create_and_add_task('t5', 5, self.task, self.user)
        t6 = self.create_and_add_task('t6', 6, self.task, self.user)
        self.task.users.add(self.user)
        self.pl.commit()
        # when
        result = self.ll.get_task_data(self.task.id, self.user,
                                       tasks_per_page=1)
        # then
        pager = result['pager']
        self.assertEqual(1, pager.page)
        self.assertEqual(6, pager.pages)
        self.assertEqual(1, pager.per_page)
        self.assertEqual([t6], pager.items)

    def test_tasks_per_page_zero_raises(self):
        # given
        self.pl.add(self.user)
        t1 = self.create_and_add_task('t1', 1, self.task, self.user)
        t2 = self.create_and_add_task('t2', 2, self.task, self.user)
        t3 = self.create_and_add_task('t3', 3, self.task, self.user)
        t4 = self.create_and_add_task('t4', 4, self.task, self.user)
        t5 = self.create_and_add_task('t5', 5, self.task, self.user)
        t6 = self.create_and_add_task('t6', 6, self.task, self.user)
        self.task.users.add(self.user)
        self.pl.commit()
        # expect
        self.assertRaises(
            ValueError,
            self.ll.get_task_data,
            self.task.id, self.user, tasks_per_page=0)

    def test_tasks_per_page_not_integer_raises(self):
        # given
        self.pl.add(self.user)
        t1 = self.create_and_add_task('t1', 1, self.task, self.user)
        t2 = self.create_and_add_task('t2', 2, self.task, self.user)
        t3 = self.create_and_add_task('t3', 3, self.task, self.user)
        t4 = self.create_and_add_task('t4', 4, self.task, self.user)
        t5 = self.create_and_add_task('t5', 5, self.task, self.user)
        t6 = self.create_and_add_task('t6', 6, self.task, self.user)
        self.task.users.add(self.user)
        self.pl.commit()
        # expect
        self.assertRaises(
            TypeError,
            self.ll.get_task_data,
            self.task.id, self.user, tasks_per_page='20')
