import unittest
from datetime import datetime

from models.attachment import Attachment


class AttachmentTest(unittest.TestCase):
    def test_minimal_construction(self):
        a = Attachment(path='/p')
        self.assertEqual(a.path, '/p')
        self.assertIsNone(a.id)
        self.assertIsNone(a.task_id)
        self.assertEqual(a.description, '')

    def test_full_construction(self):
        a = Attachment(id=1, path='/p', description='d',
                       timestamp='2025-01-02T03:04:05', filename='f.txt',
                       task_id=7)
        self.assertEqual(a.id, 1)
        self.assertEqual(a.path, '/p')
        self.assertEqual(a.description, 'd')
        self.assertEqual(a.timestamp, datetime(2025, 1, 2, 3, 4, 5))
        self.assertEqual(a.filename, 'f.txt')
        self.assertEqual(a.task_id, 7)

    def test_to_dict_uses_task_id_not_task(self):
        a = Attachment(path='/p', task_id=7)
        d = a.to_dict()
        self.assertIn('task_id', d)
        self.assertEqual(d['task_id'], 7)
        self.assertNotIn('task', d)

    def test_round_trip(self):
        a = Attachment(id=1, path='/p', task_id=7)
        a2 = Attachment.from_dict(a.to_dict())
        self.assertEqual(a2.id, 1)
        self.assertEqual(a2.path, '/p')
        self.assertEqual(a2.task_id, 7)
