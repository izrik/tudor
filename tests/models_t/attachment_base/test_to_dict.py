import unittest

from datetime import datetime

from tests.models_t.attachment_base.util import GenericAttachment


class AttachmentToDictTest(unittest.TestCase):
    def test_fields_none_exports_all(self):
        # given
        task = object()
        att = GenericAttachment('/path/to/file', 'desc', datetime(2018, 1, 1),
                                'file.ext', 123, task)
        # precondition
        self.assertEqual(123, att.id)
        self.assertEqual(datetime(2018, 1, 1),att.timestamp)
        self.assertEqual('/path/to/file',att.path)
        self.assertEqual('file.ext', att.filename)
        self.assertEqual('desc', att.description)
        self.assertIs(task, att.task)
        # when
        d = att.to_dict(fields=None)
        # then
        self.assertEqual(6, len(d))
        self.assertIn('id', d)
        self.assertEqual(123, d['id'])
        self.assertIn('timestamp', d)
        self.assertEqual('2018-01-01 00:00:00', d['timestamp'])
        self.assertIn('path', d)
        self.assertEqual('/path/to/file', d['path'])
        self.assertIn('filename', d)
        self.assertEqual('file.ext', d['filename'])
        self.assertIn('description', d)
        self.assertEqual('desc', d['description'])
        self.assertIn('task', d)
        self.assertIs(task, d['task'])

    def test_fields_id_exports_only_id(self):
        # given
        task = object()
        att = GenericAttachment('/path/to/file', 'desc', datetime(2018, 1, 1),
                                'file.ext', 123, task)
        # precondition
        self.assertEqual(123, att.id)
        self.assertEqual(datetime(2018, 1, 1),att.timestamp)
        self.assertEqual('/path/to/file',att.path)
        self.assertEqual('file.ext', att.filename)
        self.assertEqual('desc', att.description)
        self.assertIs(task, att.task)
        # when
        d = att.to_dict(fields=[att.FIELD_ID])
        # then
        self.assertEqual(1, len(d))
        self.assertIn('id', d)
        self.assertNotIn('timestamp', d)
        self.assertNotIn('path', d)
        self.assertNotIn('filename', d)
        self.assertNotIn('description', d)
        self.assertNotIn('task', d)

    def test_fields_path_exports_only_path(self):
        # given
        task = object()
        att = GenericAttachment('/path/to/file', 'desc', datetime(2018, 1, 1),
                                'file.ext', 123, task)
        # precondition
        self.assertEqual(123, att.id)
        self.assertEqual(datetime(2018, 1, 1), att.timestamp)
        self.assertEqual('/path/to/file',att.path)
        self.assertEqual('file.ext', att.filename)
        self.assertEqual('desc', att.description)
        self.assertIs(task, att.task)
        # when
        d = att.to_dict(fields=[att.FIELD_PATH])
        # then
        self.assertEqual(1, len(d))
        self.assertNotIn('id', d)
        self.assertNotIn('timestamp', d)
        self.assertIn('path', d)
        self.assertEqual('/path/to/file', d['path'])
        self.assertNotIn('filename', d)
        self.assertNotIn('description', d)
        self.assertNotIn('task', d)

    def test_fields_description_exports_only_description(self):
        # given
        task = object()
        att = GenericAttachment('/path/to/file', 'desc', datetime(2018, 1, 1),
                                'file.ext', 123, task)
        # precondition
        self.assertEqual(123, att.id)
        self.assertEqual(datetime(2018, 1, 1), att.timestamp)
        self.assertEqual('/path/to/file',att.path)
        self.assertEqual('file.ext', att.filename)
        self.assertEqual('desc', att.description)
        self.assertIs(task, att.task)
        # when
        d = att.to_dict(fields=[att.FIELD_DESCRIPTION])
        # then
        self.assertEqual(1, len(d))
        self.assertNotIn('id', d)
        self.assertNotIn('timestamp', d)
        self.assertNotIn('path', d)
        self.assertNotIn('filename', d)
        self.assertIn('description', d)
        self.assertEqual('desc', d['description'])
        self.assertNotIn('task', d)

    def test_fields_timestamp_exports_only_timestamp(self):
        # given
        task = object()
        att = GenericAttachment('/path/to/file', 'desc', datetime(2018, 1, 1),
                                'file.ext', 123, task)
        # precondition
        self.assertEqual(123, att.id)
        self.assertEqual(datetime(2018, 1, 1), att.timestamp)
        self.assertEqual('/path/to/file',att.path)
        self.assertEqual('file.ext', att.filename)
        self.assertEqual('desc', att.description)
        self.assertIs(task, att.task)
        # when
        d = att.to_dict(fields=[att.FIELD_TIMESTAMP])
        # then
        self.assertEqual(1, len(d))
        self.assertNotIn('id', d)
        self.assertIn('timestamp', d)
        self.assertEqual('2018-01-01 00:00:00', d['timestamp'])
        self.assertNotIn('path', d)
        self.assertNotIn('filename', d)
        self.assertNotIn('description', d)
        self.assertNotIn('task', d)

    def test_fields_filename_exports_only_filename(self):
        # given
        task = object()
        att = GenericAttachment('/path/to/file', 'desc', datetime(2018, 1, 1),
                                'file.ext', 123, task)
        # precondition
        self.assertEqual(123, att.id)
        self.assertEqual(datetime(2018, 1, 1), att.timestamp)
        self.assertEqual('/path/to/file',att.path)
        self.assertEqual('file.ext', att.filename)
        self.assertEqual('desc', att.description)
        self.assertIs(task, att.task)
        # when
        d = att.to_dict(fields=[att.FIELD_FILENAME])
        # then
        self.assertEqual(1, len(d))
        self.assertNotIn('id', d)
        self.assertNotIn('timestamp', d)
        self.assertNotIn('path', d)
        self.assertIn('filename', d)
        self.assertEqual('file.ext', d['filename'])
        self.assertNotIn('description', d)
        self.assertNotIn('task', d)

    def test_fields_task_exports_only_task(self):
        # given
        task = object()
        att = GenericAttachment('/path/to/file', 'desc', datetime(2018, 1, 1),
                                'file.ext', 123, task)
        # precondition
        self.assertEqual(123, att.id)
        self.assertEqual(datetime(2018, 1, 1), att.timestamp)
        self.assertEqual('/path/to/file',att.path)
        self.assertEqual('file.ext', att.filename)
        self.assertEqual('desc', att.description)
        self.assertIs(task, att.task)
        # when
        d = att.to_dict(fields=[att.FIELD_TASK])
        # then
        self.assertEqual(1, len(d))
        self.assertNotIn('id', d)
        self.assertNotIn('timestamp', d)
        self.assertNotIn('path', d)
        self.assertNotIn('filename', d)
        self.assertNotIn('description', d)
        self.assertIn('task', d)
        self.assertIs(task, d['task'])

    def test_multiple_fields_exports_those_indicated(self):
        # given
        task = object()
        att = GenericAttachment('/path/to/file', 'desc', datetime(2018, 1, 1),
                                'file.ext', 123, task)
        # precondition
        self.assertEqual(123, att.id)
        self.assertEqual(datetime(2018, 1, 1), att.timestamp)
        self.assertEqual('/path/to/file',att.path)
        self.assertEqual('file.ext', att.filename)
        self.assertEqual('desc', att.description)
        self.assertIs(task, att.task)
        # when
        d = att.to_dict(
            fields=[att.FIELD_ID, att.FIELD_TIMESTAMP, att.FIELD_PATH])
        # then
        self.assertEqual(3, len(d))
        self.assertIn('id', d)
        self.assertEqual(123, d['id'])
        self.assertIn('timestamp', d)
        self.assertEqual('2018-01-01 00:00:00', d['timestamp'])
        self.assertIn('path', d)
        self.assertEqual('/path/to/file', d['path'])
        self.assertNotIn('filename', d)
        self.assertNotIn('description', d)
        self.assertNotIn('task', d)

    def test_all_fields_exports_all(self):
        # given
        task = object()
        att = GenericAttachment('/path/to/file', 'desc', datetime(2018, 1, 1),
                                'file.ext', 123, task)
        # precondition
        self.assertEqual(123, att.id)
        self.assertEqual(datetime(2018, 1, 1), att.timestamp)
        self.assertEqual('/path/to/file',att.path)
        self.assertEqual('file.ext', att.filename)
        self.assertEqual('desc', att.description)
        self.assertIs(task, att.task)
        # when
        d = att.to_dict(
            fields=[att.FIELD_ID, att.FIELD_PATH, att.FIELD_DESCRIPTION,
                    att.FIELD_TIMESTAMP, att.FIELD_FILENAME, att.FIELD_TASK])
        # then
        self.assertEqual(6, len(d))
        self.assertIn('id', d)
        self.assertEqual(123, d['id'])
        self.assertIn('timestamp', d)
        self.assertEqual('2018-01-01 00:00:00', d['timestamp'])
        self.assertIn('path', d)
        self.assertEqual('/path/to/file', d['path'])
        self.assertIn('filename', d)
        self.assertEqual('file.ext', d['filename'])
        self.assertIn('description', d)
        self.assertEqual('desc', d['description'])
        self.assertIn('task', d)
        self.assertIs(task, d['task'])