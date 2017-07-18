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
        self.assertIn(Task.FIELD_SUMMARY, result)
        self.assertEqual('summary', result[Task.FIELD_SUMMARY])
        self.assertIn(Task.FIELD_DESCRIPTION, result)
        self.assertEqual('description',
                         result[Task.FIELD_DESCRIPTION])
        self.assertIn(Task.FIELD_IS_DONE, result)
        self.assertTrue(result[Task.FIELD_IS_DONE])
        self.assertIn(Task.FIELD_IS_DELETED, result)
        self.assertTrue(result[Task.FIELD_IS_DELETED])
        self.assertIn(Task.FIELD_DEADLINE, result)
        self.assertEqual('2038-01-19 00:00:00', result[Task.FIELD_DEADLINE])
        self.assertIn(Task.FIELD_EXPECTED_DURATION_MINUTES, result)
        self.assertEqual(5, result[Task.FIELD_EXPECTED_DURATION_MINUTES])
        self.assertIn(Task.FIELD_EXPECTED_COST, result)
        self.assertEqual('7.00', result[Task.FIELD_EXPECTED_COST])

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
        self.assertIn(Task.FIELD_ID, result)
        self.assertIsNone(result[Task.FIELD_ID])
        self.assertIn(Task.FIELD_ORDER_NUM, result)
        self.assertEqual(0, result[Task.FIELD_ORDER_NUM])
        self.assertIn(Task.FIELD_TAGS, result)
        self.assertEqual([], result[Task.FIELD_TAGS])
        self.assertIn(Task.FIELD_USERS, result)
        self.assertEqual([], result[Task.FIELD_USERS])
