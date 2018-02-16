
import unittest

from datetime import datetime

from persistence.in_memory.models.attachment import Attachment
from persistence.in_memory.models.task import Task


class AttachmentFromDictTest(unittest.TestCase):
    def test_empty_yields_empty_dbattachment(self):
        # when
        result = Attachment.from_dict({})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertIsNone(result.id)
        self.assertIsNone(result.path)
        self.assertIsNone(result.description)
        self.assertIsNone(result.timestamp)
        self.assertIsNone(result.filename)
        self.assertIsNone(result.task)

    def test_id_none_is_ignored(self):
        # when
        result = Attachment.from_dict({'id': None})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertIsNone(result.id)

    def test_valid_id_gets_set(self):
        # when
        result = Attachment.from_dict({'id': 123})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertEqual(123, result.id)

    def test_path_none_is_ignored(self):
        # when
        result = Attachment.from_dict({'path': None})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertIsNone(result.path)

    def test_valid_path_gets_set(self):
        # when
        result = Attachment.from_dict({'path': 'abc'})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertEqual('abc', result.path)

    def test_description_none_is_ignored(self):
        # when
        result = Attachment.from_dict({'description': None})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertIsNone(result.description)

    def test_valid_description_gets_set(self):
        # when
        result = Attachment.from_dict({'description': 'abc'})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertEqual('abc', result.description)

    def test_timestamp_none_becomes_none(self):
        # when
        result = Attachment.from_dict({'timestamp': None})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertIsNone(result.timestamp)

    def test_valid_timestamp_gets_set(self):
        # when
        result = Attachment.from_dict({'timestamp': datetime(2017, 1, 1)})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertEqual(datetime(2017, 1, 1), result.timestamp)

    def test_filename_none_is_ignored(self):
        # when
        result = Attachment.from_dict({'filename': None})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertIsNone(result.filename)

    def test_valid_filename_gets_set(self):
        # when
        result = Attachment.from_dict({'filename': 'abc'})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertEqual('abc', result.filename)

    def test_task_none_is_ignored(self):
        # when
        result = Attachment.from_dict({'task': None})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertIsNone(result.task)

    def test_valid_task_gets_set(self):
        # given
        task = Task('task')
        # when
        result = Attachment.from_dict({'task': task})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertIs(task, result.task)

    def test_int_task_raises(self):
        # expect
        self.assertRaises(
            Exception,
            Attachment.from_dict,
            {'task': 1})

    def test_lazy_overrides_non_lazy_task(self):
        # given
        task = Task('task')
        task2 = Task('task2')
        # when
        result = Attachment.from_dict({'task': task},
                                      lazy={'task': lambda: task2})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertIs(task2, result.task)

    def test_task_id_none_is_ignored(self):
        # when
        result = Attachment.from_dict({'task_id': None})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertIsNone(result.task_id)

    def test_valid_task_id_is_ignored(self):
        # given
        task = Task('task')
        # when
        result = Attachment.from_dict({'task_id': task.id})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertIsNone(result.task_id)

    def test_non_int_task_id_is_ignored(self):
        # given
        task = Task('task')
        # when
        result = Attachment.from_dict({'task_id': task})
        # then
        self.assertIsInstance(result, Attachment)
        self.assertIsNone(result.task_id)
        self.assertIsNone(result.task)
