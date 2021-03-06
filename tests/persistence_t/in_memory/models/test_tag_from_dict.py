
import unittest

from models.object_types import ObjectTypes
from persistence.in_memory.models.tag import Tag
from persistence.in_memory.models.task import Task


class TagFromDictTest(unittest.TestCase):
    def test_empty_yields_empty_dbtag(self):
        # when
        result = Tag.from_dict({})
        # then
        self.assertEqual(result.object_type, ObjectTypes.Tag)
        self.assertIsNone(result.id)
        self.assertIsNone(result.value)
        self.assertIsNone(result.description)
        self.assertEqual([], list(result.tasks))

    def test_id_none_is_ignored(self):
        # when
        result = Tag.from_dict({'id': None})
        # then
        self.assertEqual(result.object_type, ObjectTypes.Tag)
        self.assertIsNone(result.id)

    def test_valid_id_gets_set(self):
        # when
        result = Tag.from_dict({'id': 123})
        # then
        self.assertEqual(result.object_type, ObjectTypes.Tag)
        self.assertEqual(123, result.id)

    def test_value_none_is_ignored(self):
        # when
        result = Tag.from_dict({'value': None})
        # then
        self.assertEqual(result.object_type, ObjectTypes.Tag)
        self.assertIsNone(result.value)

    def test_valid_value_gets_set(self):
        # when
        result = Tag.from_dict({'value': 'abc'})
        # then
        self.assertEqual(result.object_type, ObjectTypes.Tag)
        self.assertEqual('abc', result.value)

    def test_description_none_becomes_none(self):
        # when
        result = Tag.from_dict({'description': None})
        # then
        self.assertEqual(result.object_type, ObjectTypes.Tag)
        self.assertIsNone(result.description)

    def test_valid_description_gets_set(self):
        # when
        result = Tag.from_dict({'description': 'abc'})
        # then
        self.assertEqual(result.object_type, ObjectTypes.Tag)
        self.assertEqual('abc', result.description)

    def test_tasks_none_yields_empty(self):
        # when
        result = Tag.from_dict({'tasks': None})
        # then
        self.assertEqual(result.object_type, ObjectTypes.Tag)
        self.assertEqual([], list(result.tasks))

    def test_tasks_empty_yields_empty(self):
        # when
        result = Tag.from_dict({'tasks': []})
        # then
        self.assertEqual(result.object_type, ObjectTypes.Tag)
        self.assertEqual([], list(result.tasks))

    def test_tasks_non_empty_yields_same(self):
        # given
        task = Task('task')
        # when
        result = Tag.from_dict({'tasks': [task]})
        # then
        self.assertEqual(result.object_type, ObjectTypes.Tag)
        self.assertEqual([task], list(result.tasks))

    def test_lazy_overrides_non_lazy_tasks(self):
        # given
        task = Task('task')
        task2 = Task('task2')
        # when
        result = Tag.from_dict({'tasks': [task]},
                               lazy={'tasks': [task2]})
        # then
        self.assertEqual(result.object_type, ObjectTypes.Tag)
        self.assertEqual([task2], list(result.tasks))

    def test_any_lazy_overrides_all_non_lazy_properties(self):
        # given
        task = Task('task')
        # when
        result = Tag.from_dict({'tasks': [task]},
                               lazy={'x': 123})
        # then
        self.assertEqual(result.object_type, ObjectTypes.Tag)
        self.assertEqual([], list(result.tasks))
