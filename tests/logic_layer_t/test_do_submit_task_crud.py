#!/usr/bin/env python

import unittest

from datetime import datetime

from models.task import Task
from models.user import User, GuestUser
from tests.logic_layer_t.util import generate_ll


class SubmitTaskCrudTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_do_data_does_not_modify_tasks(self):
        # given
        task = Task('task')
        self.pl.add(task)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        attrs = task.to_dict()
        # when
        self.ll.do_submit_task_crud({}, admin)
        self.pl.commit()
        # then
        attrs2 = task.to_dict()
        self.assertEqual(attrs, attrs2)

    def test_modifies_summary(self):
        # given
        task = Task(summary='task')
        self.pl.add(task)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        key = 'task_{}_summary'.format(task.id)
        crud_data = {key: 'something else'}
        # precondition
        self.assertEqual('task', task.summary)
        # when
        self.ll.do_submit_task_crud(crud_data, admin)
        self.pl.commit()
        # then
        self.assertEqual('something else', task.summary)

    def test_modifies_deadline(self):
        # given
        task = Task('task', deadline='2017-01-01')
        self.pl.add(task)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        key = 'task_{}_deadline'.format(task.id)
        crud_data = {key: '2017-01-02'}
        # precondition
        self.assertEqual(datetime(2017, 1, 1), task.deadline)
        # when
        self.ll.do_submit_task_crud(crud_data, admin)
        self.pl.commit()
        # then
        self.assertEqual(datetime(2017, 1, 2), task.deadline)

    def test_modifies_is_done(self):
        # given
        task = Task('task', is_done=True)
        self.pl.add(task)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        key = 'task_{}_is_done'.format(task.id)
        crud_data = {key: False}
        # precondition
        self.assertEqual(True, task.is_done)
        # when
        self.ll.do_submit_task_crud(crud_data, admin)
        self.pl.commit()
        # then
        self.assertEqual(False, task.is_done)

    def test_modifies_is_deleted(self):
        # given
        task = Task('task', is_deleted=True)
        self.pl.add(task)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        key = 'task_{}_is_deleted'.format(task.id)
        crud_data = {key: False}
        # precondition
        self.assertEqual(True, task.is_deleted)
        # when
        self.ll.do_submit_task_crud(crud_data, admin)
        self.pl.commit()
        # then
        self.assertEqual(False, task.is_deleted)

    def test_modifies_order_num(self):
        # given
        task = Task('task')
        task.order_num = 123
        self.pl.add(task)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        key = 'task_{}_order_num'.format(task.id)
        crud_data = {key: 456}
        # precondition
        self.assertEqual(123, task.order_num)
        # when
        self.ll.do_submit_task_crud(crud_data, admin)
        self.pl.commit()
        # then
        self.assertEqual(456, task.order_num)

    def test_modifies_duration(self):
        # given
        task = Task('task', expected_duration_minutes=123)
        self.pl.add(task)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        key = 'task_{}_duration'.format(task.id)
        crud_data = {key: 456}
        # precondition
        self.assertEqual(123, task.expected_duration_minutes)
        # when
        self.ll.do_submit_task_crud(crud_data, admin)
        self.pl.commit()
        # then
        self.assertEqual(456, task.expected_duration_minutes)

    def test_modifies_cost(self):
        # given
        task = Task('task', expected_cost=123)
        self.pl.add(task)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        key = 'task_{}_cost'.format(task.id)
        crud_data = {key: 456}
        # precondition
        self.assertEqual(123, task.expected_cost)
        # when
        self.ll.do_submit_task_crud(crud_data, admin)
        self.pl.commit()
        # then
        self.assertEqual(456, task.expected_cost)

    def test_modifies_parent_id(self):
        # given
        task = Task('task')
        self.pl.add(task)
        p1 = Task('p1')
        self.pl.add(p1)
        task.parent = p1
        p2 = Task('p2')
        self.pl.add(p2)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        key = 'task_{}_parent_id'.format(task.id)
        crud_data = {key: p2.id}
        # precondition
        self.assertEqual(p1.id, task.parent_id)
        # when
        self.ll.do_submit_task_crud(crud_data, admin)
        self.pl.commit()
        # then
        self.assertEqual(p2.id, task.parent_id)

    def test_modifies_multiple_tasks(self):
        # given
        t1 = Task('t1')
        self.pl.add(t1)
        t2 = Task('t2')
        self.pl.add(t2)
        t3 = Task('t3')
        self.pl.add(t3)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        crud_data = {'task_{}_summary'.format(t1.id): 't4',
                     'task_{}_summary'.format(t2.id): 't5',
                     'task_{}_summary'.format(t3.id): 't6'}
        # precondition
        self.assertEqual('t1', t1.summary)
        self.assertEqual('t2', t2.summary)
        self.assertEqual('t3', t3.summary)
        # when
        self.ll.do_submit_task_crud(crud_data, admin)
        self.pl.commit()
        # then
        self.assertEqual('t4', t1.summary)
        self.assertEqual('t5', t2.summary)
        self.assertEqual('t6', t3.summary)

    def test_authorized_user_can_modify_task(self):
        # given
        task = Task(summary='task')
        self.pl.add(task)
        user = User('user@example.com')
        self.pl.add(user)
        task.users.add(user)
        self.pl.commit()
        key = 'task_{}_summary'.format(task.id)
        crud_data = {key: 'something else'}
        # precondition
        self.assertEqual('task', task.summary)
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # when
        self.ll.do_submit_task_crud(crud_data, user)
        self.pl.commit()
        # then
        self.assertEqual('something else', task.summary)

    def test_non_authorized_user_cannot_modify_task(self):
        # given
        task = Task(summary='task')
        self.pl.add(task)
        user = User('user@example.com')
        self.pl.add(user)
        self.pl.commit()
        key = 'task_{}_summary'.format(task.id)
        crud_data = {key: 'something else'}
        # precondition
        self.assertEqual('task', task.summary)
        self.assertNotIn(user, task.users)
        self.assertNotIn(task, user.tasks)
        # when
        self.ll.do_submit_task_crud(crud_data, user)
        self.pl.commit()
        # then
        self.assertEqual('task', task.summary)

    def test_only_modifies_tasks_user_can_see(self):
        # given
        t1 = Task('t1')
        self.pl.add(t1)
        t2 = Task('t2')
        self.pl.add(t2)
        t3 = Task('t3')
        self.pl.add(t3)
        user = User('user@example.com')
        self.pl.add(user)
        t1.users.add(user)
        t3.users.add(user)
        self.pl.commit()
        crud_data = {'task_{}_summary'.format(t1.id): 't4',
                     'task_{}_summary'.format(t2.id): 't5',
                     'task_{}_summary'.format(t3.id): 't6'}
        # precondition
        self.assertEqual('t1', t1.summary)
        self.assertEqual('t2', t2.summary)
        self.assertEqual('t3', t3.summary)
        self.assertIn(user, t1.users)
        self.assertIn(t1, user.tasks)
        self.assertNotIn(user, t2.users)
        self.assertNotIn(t2, user.tasks)
        self.assertIn(user, t3.users)
        self.assertIn(t3, user.tasks)
        # when
        self.ll.do_submit_task_crud(crud_data, user)
        self.pl.commit()
        # then
        self.assertEqual('t4', t1.summary)
        self.assertEqual('t2', t2.summary)
        self.assertEqual('t6', t3.summary)

    def test_non_authorized_user_can_modify_public_tasks(self):
        # given
        task = Task(summary='task', is_public=True)
        self.pl.add(task)
        user = User('user@example.com')
        self.pl.add(user)
        self.pl.commit()
        key = 'task_{}_summary'.format(task.id)
        crud_data = {key: 'something else'}
        # precondition
        self.assertEqual('task', task.summary)
        self.assertNotIn(user, task.users)
        self.assertNotIn(task, user.tasks)
        # when
        self.ll.do_submit_task_crud(crud_data, user)
        self.pl.commit()
        # then
        self.assertEqual('something else', task.summary)

    def test_guest_user_raises(self):
        # given
        user = GuestUser()
        crud_data = {}
        # expect
        self.assertRaises(
            TypeError,
            self.ll.do_submit_task_crud,
            crud_data, user)

    def test_current_user_none_raises(self):
        # given
        crud_data = {}
        # expect
        self.assertRaises(
            ValueError,
            self.ll.do_submit_task_crud,
            crud_data, None)
