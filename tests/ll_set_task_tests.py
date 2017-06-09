#!/usr/bin/env python

import unittest
from datetime import datetime

from flask import json
from werkzeug.exceptions import Conflict, NotFound, Forbidden

from tudor import generate_app


class LogicLayerSetTaskTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.ll = self.app.ll
        self.pl = self.app.pl
        self.pl.create_all()
        self.admin = self.pl.User('admin@example.com', is_admin=True)
        self.user = self.pl.User('user@example.com', is_admin=False)
        self.task = self.pl.Task('summary')
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
            expected_cost=789.1)

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
        self.assertEqual(789.1, task.expected_cost)
        self.assertIsNone(task.parent_id)
        self.assertIsNone(task.parent)
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