import unittest
from datetime import datetime
from decimal import Decimal

from models.task import Task


class TaskConstructionTest(unittest.TestCase):
    def test_minimal_construction(self):
        t = Task(summary='foo')
        self.assertEqual(t.summary, 'foo')
        self.assertIsNone(t.id)
        self.assertIsNone(t.parent_id)
        self.assertEqual(t.description, '')
        self.assertFalse(t.is_done)
        self.assertFalse(t.is_deleted)
        self.assertFalse(t.is_public)
        self.assertEqual(t.order_num, 0)

    def test_full_construction(self):
        t = Task(
            id=5,
            summary='foo',
            description='bar',
            is_done=True,
            is_deleted=True,
            deadline='2025-01-02T03:04:05',
            expected_duration_minutes=30,
            expected_cost='12.34',
            is_public=True,
            order_num=7,
            parent_id=3)
        self.assertEqual(t.id, 5)
        self.assertEqual(t.summary, 'foo')
        self.assertEqual(t.description, 'bar')
        self.assertTrue(t.is_done)
        self.assertTrue(t.is_deleted)
        self.assertEqual(t.deadline, datetime(2025, 1, 2, 3, 4, 5))
        self.assertEqual(t.expected_duration_minutes, 30)
        self.assertEqual(t.expected_cost, Decimal('12.34'))
        self.assertTrue(t.is_public)
        self.assertEqual(t.order_num, 7)
        self.assertEqual(t.parent_id, 3)


class TaskSerializationTest(unittest.TestCase):
    def test_to_dict_includes_parent_id_not_parent_object(self):
        t = Task(summary='foo', parent_id=3)
        d = t.to_dict()
        self.assertIn('parent_id', d)
        self.assertEqual(d['parent_id'], 3)
        self.assertNotIn('parent', d)
        self.assertNotIn('children', d)
        self.assertNotIn('tags', d)
        self.assertNotIn('users', d)

    def test_round_trip(self):
        t = Task(
            id=5, summary='foo', description='bar', is_done=True,
            parent_id=3, order_num=7)
        t2 = Task.from_dict(t.to_dict())
        self.assertEqual(t2.id, 5)
        self.assertEqual(t2.summary, 'foo')
        self.assertEqual(t2.description, 'bar')
        self.assertTrue(t2.is_done)
        self.assertEqual(t2.parent_id, 3)
        self.assertEqual(t2.order_num, 7)
