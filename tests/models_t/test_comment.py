import unittest
from datetime import datetime

from models.comment import Comment


class CommentTest(unittest.TestCase):
    def test_minimal_construction(self):
        c = Comment(content='hi')
        self.assertEqual(c.content, 'hi')
        self.assertIsNone(c.id)
        self.assertIsNone(c.task_id)
        self.assertIsNone(c.timestamp)
        self.assertIsNone(c.date_last_updated)

    def test_full_construction(self):
        c = Comment(id=1, content='hi', timestamp='2025-01-02T03:04:05',
                    date_last_updated='2025-01-03T03:04:05', task_id=7)
        self.assertEqual(c.id, 1)
        self.assertEqual(c.content, 'hi')
        self.assertEqual(c.timestamp, datetime(2025, 1, 2, 3, 4, 5))
        self.assertEqual(c.date_last_updated, datetime(2025, 1, 3, 3, 4, 5))
        self.assertEqual(c.task_id, 7)

    def test_to_dict_uses_task_id_not_task(self):
        c = Comment(content='hi', task_id=7)
        d = c.to_dict()
        self.assertIn('task_id', d)
        self.assertEqual(d['task_id'], 7)
        self.assertNotIn('task', d)

    def test_round_trip(self):
        c = Comment(id=1, content='hi', task_id=7)
        c2 = Comment.from_dict(c.to_dict())
        self.assertEqual(c2.id, 1)
        self.assertEqual(c2.content, 'hi')
        self.assertEqual(c2.task_id, 7)
