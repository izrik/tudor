
import unittest

from datetime import datetime

from persistence.in_memory.models.note import IMNote
from persistence.in_memory.models.task import IMTask


class NoteFromDictTest(unittest.TestCase):
    def test_empty_yields_empty_dbnote(self):
        # when
        result = IMNote.from_dict({})
        # then
        self.assertIsInstance(result, IMNote)
        self.assertIsNone(result.id)
        self.assertIsNone(result.content)
        self.assertIsNone(result.timestamp)
        self.assertIsNone(result.task)

    def test_id_none_is_ignored(self):
        # when
        result = IMNote.from_dict({'id': None})
        # then
        self.assertIsInstance(result, IMNote)
        self.assertIsNone(result.id)

    def test_valid_id_gets_set(self):
        # when
        result = IMNote.from_dict({'id': 123})
        # then
        self.assertIsInstance(result, IMNote)
        self.assertEqual(123, result.id)

    def test_content_none_is_ignored(self):
        # when
        result = IMNote.from_dict({'content': None})
        # then
        self.assertIsInstance(result, IMNote)
        self.assertIsNone(result.content)

    def test_valid_content_gets_set(self):
        # when
        result = IMNote.from_dict({'content': 'abc'})
        # then
        self.assertIsInstance(result, IMNote)
        self.assertEqual('abc', result.content)

    def test_timestamp_none_becomes_none(self):
        # when
        result = IMNote.from_dict({'timestamp': None})
        # then
        self.assertIsInstance(result, IMNote)
        self.assertIsNone(result.timestamp)

    def test_valid_timestamp_gets_set(self):
        # when
        result = IMNote.from_dict({'timestamp': datetime(2017, 1, 1)})
        # then
        self.assertIsInstance(result, IMNote)
        self.assertEqual(datetime(2017, 1, 1), result.timestamp)

    def test_task_none_is_ignored(self):
        # when
        result = IMNote.from_dict({'task': None})
        # then
        self.assertIsInstance(result, IMNote)
        self.assertIsNone(result.task)

    def test_valid_task_gets_set(self):
        # given
        task = IMTask('task')
        # when
        result = IMNote.from_dict({'task': task})
        # then
        self.assertIsInstance(result, IMNote)
        self.assertIs(task, result.task)

    def test_int_task_raises(self):
        # expect
        self.assertRaises(
            Exception,
            IMNote.from_dict,
            {'task': 1})

    def test_task_id_none_is_ignored(self):
        # when
        result = IMNote.from_dict({'task_id': None})
        # then
        self.assertIsInstance(result, IMNote)
        self.assertIsNone(result.task_id)

    def test_valid_task_id_is_ignored(self):
        # given
        task = IMTask('task')
        # when
        result = IMNote.from_dict({'task_id': task.id})
        # then
        self.assertIsInstance(result, IMNote)
        self.assertIsNone(result.task_id)

    def test_non_int_task_id_is_ignored(self):
        # given
        task = IMTask('task')
        # when
        result = IMNote.from_dict({'task_id': task})
        # then
        self.assertIsInstance(result, IMNote)
        self.assertIsNone(result.task_id)
        self.assertIsNone(result.task)
