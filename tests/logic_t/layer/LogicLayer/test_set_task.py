#!/usr/bin/env python

import unittest
from datetime import datetime
from decimal import Decimal

from werkzeug.exceptions import NotFound, Forbidden

from tests.logic_t.layer.LogicLayer.util import generate_ll


class LogicLayerSetTaskTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll(db_uri='sqlite://')
        self.pl = self.ll.pl
        self.admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.user = self.pl.create_user('user@example.com', is_admin=False)
        self.task = self.pl.create_task('summary')
        self.pl.add(self.admin)
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.pl.commit()

    def test_set_task_missing_raises(self):
        # precondition
        self.assertIsNone(self.pl.get_task(self.task.id + 1))

        # expect
        self.assertRaises(NotFound, self.ll.set_task, self.task.id + 1,
                          self.admin, 'asdf', 'zxcv')

    def test_set_task_user_not_authorized_raises(self):
        # precondition
        self.assertNotIn(self.user, self.task.users)
        self.assertFalse(self.user.is_admin)

        # expect
        self.assertRaises(Forbidden, self.ll.set_task, self.task.id, self.user,
                          'asdf', 'zxcv')

    def test_set_task(self):
        # precondition
        self.assertEqual('summary', self.task.summary)
        self.assertEqual('', self.task.description)
        self.assertEqual(False, self.task.is_done)
        self.assertEqual(False, self.task.is_deleted)
        self.assertEqual(0, self.task.order_num)
        self.assertIsNone(self.task.deadline)
        self.assertIsNone(self.task.expected_duration_minutes)
        self.assertIsNone(self.task.expected_cost)
        self.assertIsNone(self.task.parent_id)
        self.assertIsNone(self.task.parent)
        self.assertFalse(self.task.is_public)
        self.assertEqual([], list(self.task.children))
        self.assertEqual([], list(self.task.tags))
        self.assertEqual([], list(self.task.users))
        self.assertEqual([], list(self.task.dependees))
        self.assertEqual([], list(self.task.dependants))
        self.assertEqual([], list(self.task.prioritize_before))
        self.assertEqual([], list(self.task.prioritize_after))

        # when
        task = self.ll.set_task(self.task.id, self.admin, 'asdf', 'zxcv')

        # then
        self.assertIsNotNone(task)
        self.assertIs(self.task, task)
        self.assertEqual('asdf', task.summary)
        self.assertEqual('zxcv', task.description)
        self.assertEqual(False, task.is_done)
        self.assertEqual(False, task.is_deleted)
        self.assertEqual(0, task.order_num)
        self.assertIsNone(task.deadline)
        self.assertIsNone(task.expected_duration_minutes)
        self.assertIsNone(task.expected_cost)
        self.assertIsNone(task.parent_id)
        self.assertIsNone(task.parent)
        self.assertFalse(self.task.is_public)
        self.assertEqual([], list(task.children))
        self.assertEqual([], list(task.tags))
        self.assertEqual([], list(task.users))
        self.assertEqual([], list(task.dependees))
        self.assertEqual([], list(task.dependants))
        self.assertEqual([], list(task.prioritize_before))
        self.assertEqual([], list(task.prioritize_after))

    def test_set_task_set_all_fields(self):
        # precondition
        self.assertEqual('summary', self.task.summary)
        self.assertEqual('', self.task.description)
        self.assertEqual(False, self.task.is_done)
        self.assertEqual(False, self.task.is_deleted)
        self.assertEqual(0, self.task.order_num)
        self.assertIsNone(self.task.deadline)
        self.assertIsNone(self.task.expected_duration_minutes)
        self.assertIsNone(self.task.expected_cost)
        self.assertIsNone(self.task.parent_id)
        self.assertIsNone(self.task.parent)
        self.assertFalse(self.task.is_public)
        self.assertEqual([], list(self.task.children))
        self.assertEqual([], list(self.task.tags))
        self.assertEqual([], list(self.task.users))
        self.assertEqual([], list(self.task.dependees))
        self.assertEqual([], list(self.task.dependants))
        self.assertEqual([], list(self.task.prioritize_before))
        self.assertEqual([], list(self.task.prioritize_after))

        # when
        task = self.ll.set_task(
            self.task.id,
            self.admin,
            summary='asdf',
            description='zxcv',
            deadline='2017-01-01',
            is_done=True,
            is_deleted=True,
            order_num=123,
            duration=456,
            expected_cost=Decimal('789.1'),
            is_public=True)

        # then
        self.assertIsNotNone(task)
        self.assertIs(self.task, task)
        self.assertEqual('asdf', task.summary)
        self.assertEqual('zxcv', task.description)
        self.assertEqual(True, task.is_done)
        self.assertEqual(True, task.is_deleted)
        self.assertEqual(123, task.order_num)
        self.assertEqual(datetime(2017, 1, 1), task.deadline)
        self.assertEqual(456, task.expected_duration_minutes)
        self.assertEqual(Decimal('789.1'), task.expected_cost)
        self.assertIsNone(task.parent_id)
        self.assertIsNone(task.parent)
        self.assertTrue(self.task.is_public)
        self.assertEqual([], list(task.children))
        self.assertEqual([], list(task.tags))
        self.assertEqual([], list(task.users))
        self.assertEqual([], list(task.dependees))
        self.assertEqual([], list(task.dependants))
        self.assertEqual([], list(task.prioritize_before))
        self.assertEqual([], list(task.prioritize_after))

    def test_set_task_deadline_is_falsey(self):
        # precondition
        self.assertIsNone(self.task.deadline)

        # when
        task = self.ll.set_task(
            self.task.id,
            self.admin,
            summary='asdf',
            description='zxcv',
            deadline='')

        # then
        self.assertIsNone(task.deadline)

        # when
        task = self.ll.set_task(
            self.task.id,
            self.admin,
            summary='asdf',
            description='zxcv',
            deadline=0)

        # then
        self.assertIsNone(task.deadline)

        # when
        task = self.ll.set_task(
            self.task.id,
            self.admin,
            summary='asdf',
            description='zxcv',
            deadline=[])

        # then
        self.assertIsNone(task.deadline)

    def test_set_task_deadline_is_datetime(self):
        # precondition
        self.assertIsNone(self.task.deadline)

        # when
        task = self.ll.set_task(
            self.task.id,
            self.admin,
            summary='asdf',
            description='zxcv',
            deadline=datetime(2017, 1, 1))

        # then
        self.assertIsNotNone(task.deadline)
        self.assertEqual(datetime(2017, 1, 1), task.deadline)

    def test_set_task_parent_id(self):
        # given
        ptask = self.pl.create_task('parent')
        self.pl.add(ptask)
        self.pl.commit()

        # precondition
        self.assertIsNone(self.task.parent_id)
        self.assertIsNone(self.task.parent)
        self.assertEqual(2, self.pl.count_tasks())
        self.assertIsNotNone(ptask.id)

        # when
        task = self.ll.set_task(
            self.task.id,
            self.admin,
            summary='asdf',
            description='zxcv',
            parent_id=ptask.id)

        # then
        self.assertEqual(ptask.id, self.task.parent_id)
        self.assertIs(ptask, self.task.parent)

        # when
        self.pl.commit()

        # then
        self.assertIs(ptask, self.task.parent)

    def test_set_task_parent_id_is_empty_string(self):
        # precondition
        self.assertIsNone(self.task.parent_id)
        self.assertIsNone(self.task.parent)

        # when
        task = self.ll.set_task(
            self.task.id,
            self.admin,
            summary='asdf',
            description='zxcv',
            parent_id='')

        # then
        self.assertIsNone(self.task.parent_id)
        self.assertIsNone(self.task.parent)

    def test_set_task_parent_id_invalid_id_silently_ignores(self):
        # given

        # precondition
        self.assertIsNone(self.task.parent_id)
        self.assertIsNone(self.task.parent)
        self.assertEqual(1, self.pl.count_tasks())

        # when
        task = self.ll.set_task(
            self.task.id,
            self.admin,
            summary='asdf',
            description='zxcv',
            parent_id=self.task.id + 1)

        # then
        self.assertIsNone(self.task.parent_id)
        self.assertIsNone(self.task.parent)

        # when
        self.pl.commit()

        # then
        self.assertIsNone(self.task.parent_id)
        self.assertIsNone(self.task.parent)

    def test_set_task_order_num_none_becomes_zero(self):
        # given
        self.task.order_num = None

        # precondition
        self.assertIsNone(self.task.order_num)

        # when
        task = self.ll.set_task(
            self.task.id,
            self.admin,
            summary='asdf',
            description='zxcv',
            order_num=None)

        # then
        self.assertEqual(0, self.task.order_num)
