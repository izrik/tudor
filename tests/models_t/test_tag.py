import unittest

from models.tag import Tag


class TagTest(unittest.TestCase):
    def test_minimal_construction(self):
        t = Tag(value='foo')
        self.assertEqual(t.value, 'foo')
        self.assertIsNone(t.id)
        self.assertIsNone(t.description)

    def test_full_construction(self):
        t = Tag(id=2, value='foo', description='bar')
        self.assertEqual(t.id, 2)
        self.assertEqual(t.value, 'foo')
        self.assertEqual(t.description, 'bar')

    def test_to_dict_omits_tasks(self):
        t = Tag(id=2, value='foo')
        d = t.to_dict()
        self.assertNotIn('tasks', d)
        self.assertNotIn('task_ids', d)

    def test_round_trip(self):
        t = Tag(id=2, value='foo', description='bar')
        t2 = Tag.from_dict(t.to_dict())
        self.assertEqual(t2.id, 2)
        self.assertEqual(t2.value, 'foo')
        self.assertEqual(t2.description, 'bar')
