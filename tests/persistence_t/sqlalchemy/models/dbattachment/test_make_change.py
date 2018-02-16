from datetime import datetime

from persistence.in_memory.models.attachment import Attachment
from models.changeable import Changeable
from persistence.in_memory.models.task import Task
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class DbAttachmentMakeChangeTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.attachment = self.pl.DbAttachment('attachment')

    def test_setting_id_sets_id(self):
        # precondition
        self.assertIsNone(self.attachment.id)
        # when
        self.attachment.make_change(Attachment.FIELD_ID, Changeable.OP_SET, 1)
        # then
        self.assertEqual(1, self.attachment.id)

    def test_adding_id_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_ID, Changeable.OP_ADD, 1)

    def test_removing_id_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_ID, Changeable.OP_REMOVE, 1)

    def test_changing_id_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_ID, Changeable.OP_CHANGING, 1)

    def test_setting_path_sets_path(self):
        # precondition
        self.assertEqual('attachment', self.attachment.path)
        # when
        self.attachment.make_change(Attachment.FIELD_PATH, Changeable.OP_SET,
                                    'a')
        # then
        self.assertEqual('a', self.attachment.path)

    def test_adding_path_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_PATH, Changeable.OP_ADD, 'a')

    def test_removing_path_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_PATH, Changeable.OP_REMOVE, 'a')

    def test_changing_path_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_PATH, Changeable.OP_CHANGING, 'a')

    def test_setting_description_sets_description(self):
        # precondition
        self.assertIsNone(self.attachment.description)
        # when
        self.attachment.make_change(Attachment.FIELD_DESCRIPTION,
                                    Changeable.OP_SET, 'a')
        # then
        self.assertEqual('a', self.attachment.description)

    def test_adding_description_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_DESCRIPTION, Changeable.OP_ADD, 'a')

    def test_removing_description_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_DESCRIPTION, Changeable.OP_REMOVE, 'a')

    def test_changing_description_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_DESCRIPTION, Changeable.OP_CHANGING, 'a')

    def test_setting_timestamp_sets_timestamp(self):
        # precondition
        self.assertIsNone(self.attachment.timestamp)
        # when
        self.attachment.make_change(Attachment.FIELD_TIMESTAMP,
                                    Changeable.OP_SET, datetime(2017, 1, 2))
        # then
        self.assertEqual(datetime(2017, 1, 2), self.attachment.timestamp)

    def test_adding_timestamp_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_TIMESTAMP, Changeable.OP_ADD, 'b')

    def test_removing_timestamp_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_TIMESTAMP, Changeable.OP_REMOVE, 'b')

    def test_changing_timestamp_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_TIMESTAMP, Changeable.OP_CHANGING, 'b')

    def test_setting_filename_sets_filename(self):
        # precondition
        self.assertIsNone(self.attachment.filename)
        # when
        self.attachment.make_change(Attachment.FIELD_FILENAME,
                                    Changeable.OP_SET, 'a')
        # then
        self.assertEqual('a', self.attachment.filename)

    def test_adding_filename_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_FILENAME, Changeable.OP_ADD, 'a')

    def test_removing_filename_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_FILENAME, Changeable.OP_REMOVE, 'a')

    def test_changing_filename_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_FILENAME, Changeable.OP_CHANGING, 'a')

    def test_setting_task_sets_task(self):
        # given
        task = self.pl.DbTask('task')
        # precondition
        self.assertIsNone(self.attachment.task)
        # when
        self.attachment.make_change(Attachment.FIELD_TASK,
                                    Changeable.OP_SET, task)
        # then
        self.assertEqual(task, self.attachment.task)

    def test_adding_task_raises(self):
        # given
        task = self.pl.DbTask('task')
        # precondition
        self.assertIsNone(self.attachment.task)
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_TASK, Changeable.OP_ADD, task)

    def test_removing_task_raises(self):
        # given
        task = self.pl.DbTask('task')
        # precondition
        self.assertIsNone(self.attachment.task)
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_TASK, Changeable.OP_REMOVE, task)

    def test_changing_task_raises(self):
        # given
        task = self.pl.DbTask('task')
        # precondition
        self.assertIsNone(self.attachment.task)
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Attachment.FIELD_TASK, Changeable.OP_CHANGING, task)

    def test_non_attachment_field_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            Task.FIELD_SUMMARY, Changeable.OP_SET, 'value')

    def test_invalid_field_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.attachment.make_change,
            'SOME_OTHER_FIELD', Changeable.OP_SET, 'value')
