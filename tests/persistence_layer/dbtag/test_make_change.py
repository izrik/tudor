import unittest

from models.changeable import Changeable
from models.tag import Tag
from models.task import Task
from tests.persistence_layer.util import generate_pl


class DbTagMakeChangeTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()
        self.tag = self.pl.DbTag('tag')

    def test_setting_id_sets_id(self):
        # precondition
        self.assertIsNone(self.tag.id)
        # when
        self.tag.make_change(Tag.FIELD_ID, Changeable.OP_SET, 1)
        # then
        self.assertEqual(1, self.tag.id)

    def test_adding_id_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.tag.make_change,
            Tag.FIELD_ID, Changeable.OP_ADD, 1)

    def test_removing_id_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.tag.make_change,
            Tag.FIELD_ID, Changeable.OP_REMOVE, 1)

    def test_changing_id_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.tag.make_change,
            Tag.FIELD_ID, Changeable.OP_CHANGING, 1)

    def test_setting_value_sets_value(self):
        # precondition
        self.assertEqual('tag', self.tag.value)
        # when
        self.tag.make_change(Tag.FIELD_VALUE, Changeable.OP_SET, 'a')
        # then
        self.assertEqual('a', self.tag.value)

    def test_adding_value_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.tag.make_change,
            Tag.FIELD_VALUE, Changeable.OP_ADD, 'a')

    def test_removing_value_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.tag.make_change,
            Tag.FIELD_VALUE, Changeable.OP_REMOVE, 'a')

    def test_changing_value_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.tag.make_change,
            Tag.FIELD_VALUE, Changeable.OP_CHANGING, 'a')

    def test_setting_description_sets_description(self):
        # precondition
        self.assertIsNone(self.tag.description)
        # when
        self.tag.make_change(Tag.FIELD_DESCRIPTION, Changeable.OP_SET, 'b')
        # then
        self.assertEqual('b', self.tag.description)

    def test_adding_description_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.tag.make_change,
            Tag.FIELD_DESCRIPTION, Changeable.OP_ADD, 'b')

    def test_removing_description_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.tag.make_change,
            Tag.FIELD_DESCRIPTION, Changeable.OP_REMOVE, 'b')

    def test_changing_description_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.tag.make_change,
            Tag.FIELD_DESCRIPTION, Changeable.OP_CHANGING, 'b')

    def test_adding_tasks_adds(self):
        # given
        task = self.pl.DbTask('task')
        # precondition
        self.assertEqual([], list(self.tag.tasks))
        # when
        self.tag.make_change(Tag.FIELD_TASKS, Changeable.OP_ADD, task)
        # then
        self.assertEqual([task], list(self.tag.tasks))

    def test_removing_tasks_removes(self):
        # given
        task = self.pl.DbTask('task')
        self.tag.tasks.append(task)
        # precondition
        self.assertEqual([task], list(self.tag.tasks))
        # when
        self.tag.make_change(Tag.FIELD_TASKS, Changeable.OP_REMOVE, task)
        # then
        self.assertEqual([], list(self.tag.tasks))

    def test_setting_tasks_raises(self):
        # given
        task = self.pl.DbTask('task')
        # expect
        self.assertRaises(
            ValueError,
            self.tag.make_change,
            Tag.FIELD_TASKS, Changeable.OP_SET, task)

    def test_changing_tasks_raises(self):
        # given
        task = self.pl.DbTask('task')
        # expect
        self.assertRaises(
            ValueError,
            self.tag.make_change,
            Tag.FIELD_TASKS, Changeable.OP_CHANGING, task)

    def test_non_tag_field_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.tag.make_change,
            Task.FIELD_SUMMARY, Changeable.OP_SET, 'value')

    def test_invalid_field_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.tag.make_change,
            'SOME_OTHER_FIELD', Changeable.OP_SET, 'value')

    def test_adding_task_already_in_silently_ignored(self):
        # given
        task = self.pl.DbTask('task')
        self.tag.tasks.append(task)
        # precondition
        self.assertEqual([task], list(self.tag.tasks))
        # when
        self.tag.make_change(Tag.FIELD_TASKS, Changeable.OP_ADD, task)
        # then
        self.assertEqual([task], list(self.tag.tasks))

    def test_removing_task_not_in_silently_ignored(self):
        # given
        task = self.pl.DbTask('task')
        # precondition
        self.assertEqual([], list(self.tag.tasks))
        # when
        self.tag.make_change(Tag.FIELD_TASKS, Changeable.OP_REMOVE, task)
        # then
        self.assertEqual([], list(self.tag.tasks))
