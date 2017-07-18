#!/usr/bin/env python

import unittest
from datetime import datetime

from models.task import Task


class TaskTest(unittest.TestCase):

    def test_constructor_sets_summary(self):
        # when
        task = Task('summary')
        # then
        self.assertEqual('summary', task.summary)

    def test_constructor_has_sensible_defaults(self):
        # when
        task = Task('summary')
        # then
        self.assertEqual('', task.description)
        self.assertFalse(task.is_done)
        self.assertFalse(task.is_deleted)
        self.assertIsNone(task.deadline)
        self.assertIsNone(task.expected_duration_minutes)
        self.assertIsNone(task.expected_cost)

    def test_constructor_sets_fields(self):
        # when
        task = Task(
            summary='summary',
            description='description',
            is_done=True,
            is_deleted=True,
            deadline='2038-01-19',
            expected_duration_minutes=5,
            expected_cost=7)
        # then
        self.assertEqual('description', task.description)
        self.assertTrue(task.is_done)
        self.assertTrue(task.is_deleted)
        self.assertEqual(datetime(2038, 1, 19), task.deadline)
        self.assertEqual(5, task.expected_duration_minutes)
        self.assertEqual(7, task.expected_cost)

    def test_to_dict_returns_correct_values(self):
        # given
        task = Task(
            summary='summary',
            description='description',
            is_done=True,
            is_deleted=True,
            deadline='2038-01-19',
            expected_duration_minutes=5,
            expected_cost=7)
        # when
        result = task.to_dict()
        # then
        self.assertIn('summary', result)
        self.assertEqual('summary', result['summary'])
        self.assertIn('description', result)
        self.assertEqual('description', result['description'])
        self.assertIn('is_done', result)
        self.assertTrue(result['is_done'])
        self.assertIn('is_deleted', result)
        self.assertTrue(result['is_deleted'])
        self.assertIn('deadline', result)
        self.assertEqual('2038-01-19 00:00:00', result['deadline'])
        self.assertIn('expected_duration_minutes', result)
        self.assertEqual(5, result['expected_duration_minutes'])
        self.assertIn('expected_cost', result)
        self.assertEqual('7.00', result['expected_cost'])

    def test_to_dict_returns_other_values_not_in_the_constructor(self):
        # given
        task = Task(
            summary='summary',
            description='description',
            is_done=True,
            is_deleted=True,
            deadline='2038-01-19',
            expected_duration_minutes=5,
            expected_cost=7)
        # when
        result = task.to_dict()
        # then
        self.assertEqual(19, len(result))
        self.assertIn('id', result)
        self.assertIsNone(result['id'])
        self.assertIn('order_num', result)
        self.assertEqual(0, result['order_num'])
        self.assertIn('tags', result)
        self.assertEqual([], result['tags'])
        self.assertIn('users', result)
        self.assertEqual([], result['users'])
