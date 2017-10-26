import unittest
from datetime import datetime
from decimal import Decimal

from models.changeable import Changeable
from models.tag import Tag
from models.task import Task
from tests.persistence_layer_t.util import generate_pl


class DbTaskMakeChangeTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()
        self.task = self.pl.DbTask('task')

    def test_setting_id_sets_id(self):
        # precondition
        self.assertIsNone(self.task.id)
        # when
        self.task.make_change(Task.FIELD_ID, Changeable.OP_SET, 1)
        # then
        self.assertEqual(1, self.task.id)

    def test_adding_id_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_ID, Changeable.OP_ADD, 1)

    def test_removing_id_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_ID, Changeable.OP_REMOVE, 1)

    def test_changing_id_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_ID, Changeable.OP_CHANGING, 1)

    def test_setting_summary_sets_summary(self):
        # precondition
        self.assertEqual('task', self.task.summary)
        # when
        self.task.make_change(Task.FIELD_SUMMARY, Changeable.OP_SET, 'a')
        # then
        self.assertEqual('a', self.task.summary)

    def test_adding_summary_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_SUMMARY, Changeable.OP_ADD, 'a')

    def test_removing_summary_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_SUMMARY, Changeable.OP_REMOVE, 'a')

    def test_changing_summary_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_SUMMARY, Changeable.OP_CHANGING, 'a')

    def test_setting_description_sets_description(self):
        # precondition
        self.assertEqual('', self.task.description)
        # when
        self.task.make_change(Task.FIELD_DESCRIPTION, Changeable.OP_SET, 'b')
        # then
        self.assertEqual('b', self.task.description)

    def test_adding_description_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_DESCRIPTION, Changeable.OP_ADD, 'b')

    def test_removing_description_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_DESCRIPTION, Changeable.OP_REMOVE, 'b')

    def test_changing_description_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_DESCRIPTION, Changeable.OP_CHANGING, 'b')

    def test_setting_is_done_sets_is_done(self):
        # precondition
        self.assertFalse(self.task.is_done)
        # when
        self.task.make_change(Task.FIELD_IS_DONE, Changeable.OP_SET, True)
        # then
        self.assertTrue(self.task.is_done)

    def test_adding_is_done_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_IS_DONE, Changeable.OP_ADD, True)

    def test_removing_is_done_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_IS_DONE, Changeable.OP_REMOVE, True)

    def test_changing_is_done_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_IS_DONE, Changeable.OP_CHANGING, True)

    def test_setting_is_deleted_sets_is_deleted(self):
        # precondition
        self.assertFalse(self.task.is_deleted)
        # when
        self.task.make_change(Task.FIELD_IS_DELETED, Changeable.OP_SET, True)
        # then
        self.assertTrue(self.task.is_deleted)

    def test_adding_is_deleted_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_IS_DELETED, Changeable.OP_ADD, True)

    def test_removing_is_deleted_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_IS_DELETED, Changeable.OP_REMOVE, True)

    def test_changing_is_deleted_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_IS_DELETED, Changeable.OP_CHANGING, True)

    def test_setting_deadline_sets_deadline(self):
        # precondition
        self.assertIsNone(self.task.deadline)
        # when
        self.task.make_change(Task.FIELD_DEADLINE, Changeable.OP_SET,
                              datetime(2017, 1, 1))
        # then
        self.assertEqual(datetime(2017, 1, 1), self.task.deadline)

    def test_adding_deadline_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_DEADLINE, Changeable.OP_ADD, datetime(2017, 1, 1))

    def test_removing_deadline_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_DEADLINE, Changeable.OP_REMOVE, datetime(2017, 1, 1))

    def test_changing_deadline_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_DEADLINE, Changeable.OP_CHANGING, datetime(2017, 1, 1))

    def test_setting_expected_duration_sets_expected_duration(self):
        # precondition
        self.assertIsNone(self.task.expected_duration_minutes)
        # when
        self.task.make_change(Task.FIELD_EXPECTED_DURATION_MINUTES,
                              Changeable.OP_SET, 123)
        # then
        self.assertEqual(123, self.task.expected_duration_minutes)

    def test_adding_expected_duration_minutes_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_EXPECTED_DURATION_MINUTES, Changeable.OP_ADD, 123)

    def test_removing_expected_duration_minutes_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_EXPECTED_DURATION_MINUTES, Changeable.OP_REMOVE, 123)

    def test_changing_expected_duration_minutes_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_EXPECTED_DURATION_MINUTES, Changeable.OP_CHANGING, 123)

    def test_setting_expected_cost_sets_expected_cost(self):
        # precondition
        self.assertIsNone(self.task.expected_cost)
        # when
        self.task.make_change(Task.FIELD_EXPECTED_COST, Changeable.OP_SET,
                              Decimal(123.45))
        # then
        self.assertEqual(Decimal(123.45), self.task.expected_cost)

    def test_adding_expected_cost_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_EXPECTED_COST, Changeable.OP_ADD, Decimal(123.45))

    def test_removing_expected_cost_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_EXPECTED_COST, Changeable.OP_REMOVE, Decimal(123.45))

    def test_changing_expected_cost_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_EXPECTED_COST, Changeable.OP_CHANGING, Decimal(123.45))

    def test_setting_order_num_sets_order_num(self):
        # precondition
        self.assertEqual(0, self.task.order_num)
        # when
        self.task.make_change(Task.FIELD_ORDER_NUM, Changeable.OP_SET, 2)
        # then
        self.assertEqual(2, self.task.order_num)

    def test_adding_order_num_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_ORDER_NUM, Changeable.OP_ADD, 2)

    def test_removing_order_num_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_ORDER_NUM, Changeable.OP_REMOVE, 2)

    def test_changing_order_num_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_ORDER_NUM, Changeable.OP_CHANGING, 2)

    def test_setting_parent_sets_parent(self):
        # given
        parent = self.pl.DbTask('parent')
        # precondition
        self.assertIsNone(self.task.parent)
        # when
        self.task.make_change(Task.FIELD_PARENT, Changeable.OP_SET, parent)
        # then
        self.assertIs(parent, self.task.parent)

    def test_adding_parent_raises(self):
        # given
        parent = self.pl.DbTask('parent')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_PARENT, Changeable.OP_ADD, parent)

    def test_removing_parent_raises(self):
        # given
        parent = self.pl.DbTask('parent')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_PARENT, Changeable.OP_REMOVE, parent)

    def test_changing_parent_raises(self):
        # given
        parent = self.pl.DbTask('parent')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_PARENT, Changeable.OP_CHANGING, parent)

    def test_adding_children_adds(self):
        # given
        child = self.pl.DbTask('child')
        # precondition
        self.assertEqual([], list(self.task.children))
        # when
        self.task.make_change(Task.FIELD_CHILDREN, Changeable.OP_ADD, child)
        # then
        self.assertEqual([child], list(self.task.children))

    def test_removing_children_removes(self):
        # given
        child = self.pl.DbTask('child')
        self.task.children.append(child)
        # precondition
        self.assertEqual([child], list(self.task.children))
        # when
        self.task.make_change(Task.FIELD_CHILDREN, Changeable.OP_REMOVE, child)
        # then
        self.assertEqual([], list(self.task.children))

    def test_setting_children_raises(self):
        # given
        child = self.pl.DbTask('child')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_CHILDREN, Changeable.OP_SET, child)

    def test_changing_children_raises(self):
        # given
        child = self.pl.DbTask('child')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_CHILDREN, Changeable.OP_CHANGING, child)

    def test_adding_dependees_adds(self):
        # given
        dependee = self.pl.DbTask('dependee')
        # precondition
        self.assertEqual([], list(self.task.dependees))
        # when
        self.task.make_change(Task.FIELD_DEPENDEES, Changeable.OP_ADD,
                              dependee)
        # then
        self.assertEqual([dependee], list(self.task.dependees))

    def test_removing_dependees_removes(self):
        # given
        dependee = self.pl.DbTask('dependee')
        self.task.dependees.append(dependee)
        # precondition
        self.assertEqual([dependee], list(self.task.dependees))
        # when
        self.task.make_change(Task.FIELD_DEPENDEES, Changeable.OP_REMOVE,
                              dependee)
        # then
        self.assertEqual([], list(self.task.dependees))

    def test_setting_dependees_raises(self):
        # given
        dependee = self.pl.DbTask('dependee')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_DEPENDEES, Changeable.OP_SET, dependee)

    def test_changing_dependees_raises(self):
        # given
        dependee = self.pl.DbTask('dependee')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_DEPENDEES, Changeable.OP_CHANGING, dependee)

    def test_adding_dependants_adds(self):
        # given
        dependant = self.pl.DbTask('dependant')
        # precondition
        self.assertEqual([], list(self.task.dependants))
        # when
        self.task.make_change(Task.FIELD_DEPENDANTS, Changeable.OP_ADD,
                              dependant)
        # then
        self.assertEqual([dependant], list(self.task.dependants))

    def test_removing_dependants_removes(self):
        # given
        dependant = self.pl.DbTask('dependant')
        self.task.dependants.append(dependant)
        # precondition
        self.assertEqual([dependant], list(self.task.dependants))
        # when
        self.task.make_change(Task.FIELD_DEPENDANTS, Changeable.OP_REMOVE,
                              dependant)
        # then
        self.assertEqual([], list(self.task.dependants))

    def test_setting_dependants_raises(self):
        # given
        dependant = self.pl.DbTask('dependant')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_DEPENDANTS, Changeable.OP_SET, dependant)

    def test_changing_dependants_raises(self):
        # given
        dependant = self.pl.DbTask('dependant')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_DEPENDANTS, Changeable.OP_CHANGING, dependant)

    def test_adding_prioritize_before_adds(self):
        # given
        before = self.pl.DbTask('before')
        # precondition
        self.assertEqual([], list(self.task.prioritize_before))
        # when
        self.task.make_change(Task.FIELD_PRIORITIZE_BEFORE, Changeable.OP_ADD,
                              before)
        # then
        self.assertEqual([before], list(self.task.prioritize_before))

    def test_removing_prioritize_before_removes(self):
        # given
        before = self.pl.DbTask('before')
        self.task.prioritize_before.append(before)
        # precondition
        self.assertEqual([before], list(self.task.prioritize_before))
        # when
        self.task.make_change(Task.FIELD_PRIORITIZE_BEFORE,
                              Changeable.OP_REMOVE, before)
        # then
        self.assertEqual([], list(self.task.prioritize_before))

    def test_setting_prioritize_before_raises(self):
        # given
        before = self.pl.DbTask('before')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_PRIORITIZE_BEFORE, Changeable.OP_SET, before)

    def test_changing_prioritize_before_raises(self):
        # given
        before = self.pl.DbTask('before')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_PRIORITIZE_BEFORE, Changeable.OP_CHANGING, before)

    def test_adding_prioritize_after_adds(self):
        # given
        after = self.pl.DbTask('after')
        # precondition
        self.assertEqual([], list(self.task.prioritize_after))
        # when
        self.task.make_change(Task.FIELD_PRIORITIZE_AFTER, Changeable.OP_ADD,
                              after)
        # then
        self.assertEqual([after], list(self.task.prioritize_after))

    def test_removing_prioritize_after_removes(self):
        # given
        after = self.pl.DbTask('after')
        self.task.prioritize_after.append(after)
        # precondition
        self.assertEqual([after], list(self.task.prioritize_after))
        # when
        self.task.make_change(Task.FIELD_PRIORITIZE_AFTER,
                              Changeable.OP_REMOVE, after)
        # then
        self.assertEqual([], list(self.task.prioritize_after))

    def test_setting_prioritize_after_raises(self):
        # given
        after = self.pl.DbTask('after')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_PRIORITIZE_AFTER, Changeable.OP_SET, after)

    def test_changing_prioritize_after_raises(self):
        # given
        after = self.pl.DbTask('after')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_PRIORITIZE_AFTER, Changeable.OP_CHANGING, after)

    def test_adding_tags_adds(self):
        # given
        tag = self.pl.DbTag('tag')
        # precondition
        self.assertEqual([], list(self.task.tags))
        # when
        self.task.make_change(Task.FIELD_TAGS, Changeable.OP_ADD, tag)
        # then
        self.assertEqual([tag], list(self.task.tags))

    def test_removing_tags_removes(self):
        # given
        tag = self.pl.DbTag('tag')
        self.task.tags.append(tag)
        # precondition
        self.assertEqual([tag], list(self.task.tags))
        # when
        self.task.make_change(Task.FIELD_TAGS, Changeable.OP_REMOVE, tag)
        # then
        self.assertEqual([], list(self.task.tags))

    def test_setting_tags_raises(self):
        # given
        tag = self.pl.DbTag('tag')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_TAGS, Changeable.OP_SET, tag)

    def test_changing_tags_raises(self):
        # given
        tag = self.pl.DbTag('tag')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_TAGS, Changeable.OP_CHANGING, tag)

    def test_adding_users_adds(self):
        # given
        user = self.pl.DbUser('user')
        # precondition
        self.assertEqual([], list(self.task.users))
        # when
        self.task.make_change(Task.FIELD_USERS, Changeable.OP_ADD, user)
        # then
        self.assertEqual([user], list(self.task.users))

    def test_removing_users_removes(self):
        # given
        user = self.pl.DbUser('user')
        self.task.users.append(user)
        # precondition
        self.assertEqual([user], list(self.task.users))
        # when
        self.task.make_change(Task.FIELD_USERS, Changeable.OP_REMOVE, user)
        # then
        self.assertEqual([], list(self.task.users))

    def test_setting_users_raises(self):
        # given
        user = self.pl.DbUser('user')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_USERS, Changeable.OP_SET, user)

    def test_changing_users_raises(self):
        # given
        user = self.pl.DbUser('user')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_USERS, Changeable.OP_CHANGING, user)

    def test_adding_notes_adds(self):
        # given
        note = self.pl.DbNote('note')
        # precondition
        self.assertEqual([], list(self.task.notes))
        # when
        self.task.make_change(Task.FIELD_NOTES, Changeable.OP_ADD, note)
        # then
        self.assertEqual([note], list(self.task.notes))

    def test_removing_notes_removes(self):
        # given
        note = self.pl.DbNote('note')
        self.task.notes.append(note)
        # precondition
        self.assertEqual([note], list(self.task.notes))
        # when
        self.task.make_change(Task.FIELD_NOTES, Changeable.OP_REMOVE, note)
        # then
        self.assertEqual([], list(self.task.notes))

    def test_setting_notes_raises(self):
        # given
        note = self.pl.DbNote('note')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_NOTES, Changeable.OP_SET, note)

    def test_changing_notes_raises(self):
        # given
        note = self.pl.DbNote('note')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_NOTES, Changeable.OP_CHANGING, note)

    def test_adding_attachments_adds(self):
        # given
        attachment = self.pl.DbAttachment('attachment')
        # precondition
        self.assertEqual([], list(self.task.attachments))
        # when
        self.task.make_change(Task.FIELD_ATTACHMENTS, Changeable.OP_ADD,
                              attachment)
        # then
        self.assertEqual([attachment], list(self.task.attachments))

    def test_removing_attachments_removes(self):
        # given
        attachment = self.pl.DbAttachment('attachment')
        self.task.attachments.append(attachment)
        # precondition
        self.assertEqual([attachment], list(self.task.attachments))
        # when
        self.task.make_change(Task.FIELD_ATTACHMENTS, Changeable.OP_REMOVE,
                              attachment)
        # then
        self.assertEqual([], list(self.task.attachments))

    def test_setting_attachments_raises(self):
        # given
        attachment = self.pl.DbAttachment('attachment')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_ATTACHMENTS, Changeable.OP_SET, attachment)

    def test_changing_attachments_raises(self):
        # given
        attachment = self.pl.DbAttachment('attachment')
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_ATTACHMENTS, Changeable.OP_CHANGING, attachment)

    def test_non_task_field_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Tag.FIELD_VALUE, Changeable.OP_SET, 'value')

    def test_invalid_field_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            'SOME_OTHER_FIELD', Changeable.OP_SET, 'value')

    def test_adding_child_already_in_silently_ignored(self):
        # given
        child = self.pl.DbTask('child')
        self.task.children.append(child)
        # precondition
        self.assertEqual([child], list(self.task.children))
        # when
        self.task.make_change(Task.FIELD_CHILDREN, Changeable.OP_ADD, child)
        # then
        self.assertEqual([child], list(self.task.children))

    def test_removing_child_not_in_silently_ignored(self):
        # given
        child = self.pl.DbTask('child')
        # precondition
        self.assertEqual([], list(self.task.children))
        # when
        self.task.make_change(Task.FIELD_CHILDREN, Changeable.OP_REMOVE, child)
        # then
        self.assertEqual([], list(self.task.children))

    def test_setting_is_public_sets_is_public(self):
        # precondition
        self.assertFalse(self.task.is_public)
        # when
        self.task.make_change(Task.FIELD_IS_PUBLIC, Changeable.OP_SET, True)
        # then
        self.assertTrue(self.task.is_public)

    def test_adding_is_public_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_IS_PUBLIC, Changeable.OP_ADD, True)

    def test_removing_is_public_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_IS_PUBLIC, Changeable.OP_REMOVE, True)

    def test_changing_is_public_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.task.make_change,
            Task.FIELD_IS_PUBLIC, Changeable.OP_CHANGING, True)
