import unittest

from datetime import datetime

from tests.models_t.attachment_base.util import GenericAttachment


class AttachmentUpdateFromDictTest(unittest.TestCase):
    def test_empty_dict_no_changes(self):
        # given
        att = GenericAttachment()
        # precondition
        self.assertIsNone(att.id)
        self.assertIsNone(att.timestamp)
        self.assertIsNone(att.path)
        self.assertIsNone(att.filename)
        self.assertEqual('', att.description)
        self.assertIsNone(att.task)
        # when
        att.update_from_dict({})
        # then
        self.assertIsNone(att.id)
        self.assertIsNone(att.timestamp)
        self.assertIsNone(att.path)
        self.assertIsNone(att.filename)
        self.assertEqual('', att.description)
        self.assertIsNone(att.task)

    def test_id_in_dict_changes_id(self):
        # given
        att = GenericAttachment()
        # precondition
        self.assertIsNone(att.id)
        self.assertIsNone(att.timestamp)
        self.assertIsNone(att.path)
        self.assertIsNone(att.filename)
        self.assertEqual('', att.description)
        self.assertIsNone(att.task)
        # when
        att.update_from_dict({'id': 1})
        # then
        self.assertEqual(1, att.id)
        self.assertIsNone(att.timestamp)
        self.assertIsNone(att.path)
        self.assertIsNone(att.filename)
        self.assertEqual('', att.description)
        self.assertIsNone(att.task)

    def test_timestamp_in_dict_changes_timestamp(self):
        # given
        att = GenericAttachment()
        # precondition
        self.assertIsNone(att.id)
        self.assertIsNone(att.timestamp)
        self.assertIsNone(att.path)
        self.assertIsNone(att.filename)
        self.assertEqual('', att.description)
        self.assertIsNone(att.task)
        # when
        att.update_from_dict({'timestamp': datetime(2018, 1, 1)})
        # then
        self.assertIsNone(att.id)
        self.assertEqual(datetime(2018, 1, 1), att.timestamp)
        self.assertIsNone(att.path)
        self.assertIsNone(att.filename)
        self.assertEqual('', att.description)
        self.assertIsNone(att.task)

    def test_path_in_dict_changes_path(self):
        # given
        att = GenericAttachment()
        # precondition
        self.assertIsNone(att.id)
        self.assertIsNone(att.timestamp)
        self.assertIsNone(att.path)
        self.assertIsNone(att.filename)
        self.assertEqual('', att.description)
        self.assertIsNone(att.task)
        # when
        att.update_from_dict({'path': '/path/to/file'})
        # then
        self.assertIsNone(att.id)
        self.assertIsNone(att.timestamp)
        self.assertEqual('/path/to/file', att.path)
        self.assertIsNone(att.filename)
        self.assertEqual('', att.description)
        self.assertIsNone(att.task)

    def test_filename_in_dict_changes_filename(self):
        # given
        att = GenericAttachment()
        # precondition
        self.assertIsNone(att.id)
        self.assertIsNone(att.timestamp)
        self.assertIsNone(att.path)
        self.assertIsNone(att.filename)
        self.assertEqual('', att.description)
        self.assertIsNone(att.task)
        # when
        att.update_from_dict({'filename': 'file.ext'})
        # then
        self.assertIsNone(att.id)
        self.assertIsNone(att.timestamp)
        self.assertIsNone(att.path)
        self.assertEqual('file.ext', att.filename)
        self.assertEqual('', att.description)
        self.assertIsNone(att.task)

    def test_description_in_dict_changes_description(self):
        # given
        att = GenericAttachment()
        # precondition
        self.assertIsNone(att.id)
        self.assertIsNone(att.timestamp)
        self.assertIsNone(att.path)
        self.assertIsNone(att.filename)
        self.assertEqual('', att.description)
        self.assertIsNone(att.task)
        # when
        att.update_from_dict({'description': 'this is the attachment'})
        # then
        self.assertIsNone(att.id)
        self.assertIsNone(att.timestamp)
        self.assertIsNone(att.path)
        self.assertIsNone(att.filename)
        self.assertEqual('this is the attachment', att.description)
        self.assertIsNone(att.task)

    def test_task_in_dict_changes_task(self):
        # given
        att = GenericAttachment()
        # precondition
        self.assertIsNone(att.id)
        self.assertIsNone(att.timestamp)
        self.assertIsNone(att.path)
        self.assertIsNone(att.filename)
        self.assertEqual('', att.description)
        self.assertIsNone(att.task)
        task = object()
        # when
        att.update_from_dict({'task': task})
        # then
        self.assertIsNone(att.id)
        self.assertIsNone(att.timestamp)
        self.assertIsNone(att.path)
        self.assertIsNone(att.filename)
        self.assertEqual('', att.description)
        self.assertIs(task, att.task)

    def test_other_names_silently_ignored(self):
        # given
        att = GenericAttachment()
        # precondition
        self.assertIsNone(att.id)
        self.assertIsNone(att.timestamp)
        self.assertIsNone(att.path)
        self.assertIsNone(att.filename)
        self.assertEqual('', att.description)
        self.assertIsNone(att.task)
        # when
        att.update_from_dict({'something': 'other thing'})
        # then
        self.assertIsNone(att.id)
        self.assertIsNone(att.timestamp)
        self.assertIsNone(att.path)
        self.assertIsNone(att.filename)
        self.assertEqual('', att.description)
        self.assertIsNone(att.task)
