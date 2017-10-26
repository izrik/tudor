import unittest
from datetime import datetime

from models.changeable import Changeable
from models.note import Note
from models.task import Task
from tests.persistence_layer_t.util import generate_pl


class DbNoteMakeChangeTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()
        self.Note = self.pl.DbNote('Note', datetime(2017, 1, 1))

    def test_setting_id_sets_id(self):
        # precondition
        self.assertIsNone(self.Note.id)
        # when
        self.Note.make_change(Note.FIELD_ID, Changeable.OP_SET, 1)
        # then
        self.assertEqual(1, self.Note.id)

    def test_adding_id_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.Note.make_change,
            Note.FIELD_ID, Changeable.OP_ADD, 1)

    def test_removing_id_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.Note.make_change,
            Note.FIELD_ID, Changeable.OP_REMOVE, 1)

    def test_changing_id_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.Note.make_change,
            Note.FIELD_ID, Changeable.OP_CHANGING, 1)

    def test_setting_content_sets_content(self):
        # precondition
        self.assertEqual('Note', self.Note.content)
        # when
        self.Note.make_change(Note.FIELD_CONTENT, Changeable.OP_SET, 'a')
        # then
        self.assertEqual('a', self.Note.content)

    def test_adding_content_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.Note.make_change,
            Note.FIELD_CONTENT, Changeable.OP_ADD, 'a')

    def test_removing_content_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.Note.make_change,
            Note.FIELD_CONTENT, Changeable.OP_REMOVE, 'a')

    def test_changing_content_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.Note.make_change,
            Note.FIELD_CONTENT, Changeable.OP_CHANGING, 'a')

    def test_setting_timestamp_sets_timestamp(self):
        # precondition
        self.assertEqual(datetime(2017, 1, 1), self.Note.timestamp)
        # when
        self.Note.make_change(Note.FIELD_TIMESTAMP, Changeable.OP_SET,
                              datetime(2017, 1, 2))
        # then
        self.assertEqual(datetime(2017, 1, 2), self.Note.timestamp)

    def test_adding_timestamp_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.Note.make_change,
            Note.FIELD_TIMESTAMP, Changeable.OP_ADD, 'b')

    def test_removing_timestamp_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.Note.make_change,
            Note.FIELD_TIMESTAMP, Changeable.OP_REMOVE, 'b')

    def test_changing_timestamp_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.Note.make_change,
            Note.FIELD_TIMESTAMP, Changeable.OP_CHANGING, 'b')

    def test_setting_task_sets_task(self):
        # given
        task = self.pl.DbTask('task')
        # precondition
        self.assertIsNone(self.Note.task)
        # when
        self.Note.make_change(Note.FIELD_TASK, Changeable.OP_SET, task)
        # then
        self.assertEqual(task, self.Note.task)

    def test_adding_task_raises(self):
        # given
        task = self.pl.DbTask('task')
        # precondition
        self.assertIsNone(self.Note.task)
        # expect
        self.assertRaises(
            ValueError,
            self.Note.make_change,
            Note.FIELD_TASK, Changeable.OP_ADD, task)

    def test_removing_task_raises(self):
        # given
        task = self.pl.DbTask('task')
        # precondition
        self.assertIsNone(self.Note.task)
        # expect
        self.assertRaises(
            ValueError,
            self.Note.make_change,
            Note.FIELD_TASK, Changeable.OP_REMOVE, task)

    def test_changing_task_raises(self):
        # given
        task = self.pl.DbTask('task')
        # precondition
        self.assertIsNone(self.Note.task)
        # expect
        self.assertRaises(
            ValueError,
            self.Note.make_change,
            Note.FIELD_TASK, Changeable.OP_CHANGING, task)

    def test_non_note_field_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.Note.make_change,
            Task.FIELD_SUMMARY, Changeable.OP_SET, 'value')

    def test_invalid_field_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.Note.make_change,
            'SOME_OTHER_FIELD', Changeable.OP_SET, 'value')
