
import unittest

from datetime import datetime

from decimal import Decimal

from models.attachment import Attachment
from models.note import Note
from models.tag import Tag
from models.task import Task
from models.user import User


class TaskFromDictTest(unittest.TestCase):
    # def setUp(self):
    #     self.pl = generate_pl()
    #     self.pl.create_all()

    def test_empty_yields_empty_dbtask(self):
        # when
        result = Task.from_dict({})
        # then
        self.assertIsInstance(result, Task)
        self.assertIsNone(result.id)
        self.assertIsNone(result.summary)
        self.assertEqual('', result.description)
        self.assertFalse(result.is_done)
        self.assertFalse(result.is_deleted)
        self.assertEqual(0, result.order_num)
        self.assertIsNone(result.deadline)
        self.assertIsNone(result.expected_duration_minutes)
        self.assertIsNone(result.expected_cost)
        self.assertEqual([], list(result.tags))
        self.assertEqual([], list(result.users))
        self.assertIsNone(result.parent)
        self.assertIsNone(result.parent_id)
        self.assertEqual([], list(result.dependees))
        self.assertEqual([], list(result.dependants))
        self.assertEqual([], list(result.prioritize_before))
        self.assertEqual([], list(result.prioritize_after))

    def test_id_none_is_ignored(self):
        # when
        result = Task.from_dict({'id': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertIsNone(result.id)

    def test_valid_id_gets_set(self):
        # when
        result = Task.from_dict({'id': 123})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual(123, result.id)

    def test_summary_none_is_ignored(self):
        # when
        result = Task.from_dict({'summary': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertIsNone(result.summary)

    def test_valid_summary_gets_set(self):
        # when
        result = Task.from_dict({'summary': 'abc'})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual('abc', result.summary)

    def test_description_none_becomes_none(self):
        # when
        result = Task.from_dict({'description': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertIsNone(result.description)

    def test_valid_description_gets_set(self):
        # when
        result = Task.from_dict({'description': 'abc'})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual('abc', result.description)

    def test_is_done_none_is_becomes_false(self):
        # when
        result = Task.from_dict({'is_done': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertFalse(result.is_done)

    def test_valid_is_done_gets_set(self):
        # when
        result = Task.from_dict({'is_done': True})
        # then
        self.assertIsInstance(result, Task)
        self.assertTrue(result.is_done)

    def test_is_deleted_none_becomes_false(self):
        # when
        result = Task.from_dict({'is_deleted': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertFalse(result.is_deleted)

    def test_valid_is_deleted_gets_set(self):
        # when
        result = Task.from_dict({'is_deleted': True})
        # then
        self.assertIsInstance(result, Task)
        self.assertTrue(result.is_deleted)

    def test_order_num_none_becomes_none(self):
        # when
        result = Task.from_dict({'order_num': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertIsNone(result.order_num)

    def test_valid_order_num_gets_set(self):
        # when
        result = Task.from_dict({'order_num': 123})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual(123, result.order_num)

    def test_deadline_none_is_ignored(self):
        # when
        result = Task.from_dict({'deadline': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertIsNone(result.deadline)

    def test_valid_deadline_gets_set(self):
        # when
        result = Task.from_dict({'deadline': datetime(2017, 01, 01)})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual(datetime(2017, 01, 01), result.deadline)

    def test_string_deadline_becomes_datetime(self):
        # when
        result = Task.from_dict({'deadline': '2017-01-01'})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual(datetime(2017, 01, 01), result.deadline)

    def test_expected_duration_minutes_none_is_ignored(self):
        # when
        result = Task.from_dict({'expected_duration_minutes': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertIsNone(result.expected_duration_minutes)

    def test_valid_expected_duration_minutes_gets_set(self):
        # when
        result = Task.from_dict({'expected_duration_minutes': 123})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual(123, result.expected_duration_minutes)

    def test_expected_cost_none_is_ignored(self):
        # when
        result = Task.from_dict({'expected_cost': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertIsNone(result.expected_cost)

    def test_valid_expected_cost_gets_set(self):
        # when
        result = Task.from_dict({'expected_cost': Decimal(123.45)})
        # then
        self.assertIsInstance(result, Task)
        self.assertIsInstance(result.expected_cost, Decimal)
        self.assertEqual(Decimal(123.45), result.expected_cost)

    def test_float_expected_cost_gets_set_as_float(self):
        # when
        result = Task.from_dict({'expected_cost': 123.45})
        # then
        self.assertIsInstance(result, Task)
        self.assertIsInstance(result.expected_cost, float)
        self.assertEqual(123.45, result.expected_cost)

    def test_string_expected_cost_gets_set_as_string(self):
        # when
        result = Task.from_dict({'expected_cost': '123.45'})
        # then
        self.assertIsInstance(result, Task)
        self.assertIsInstance(result.expected_cost, basestring)
        self.assertEqual('123.45', result.expected_cost)

    def test_parent_none_is_ignored(self):
        # when
        result = Task.from_dict({'parent': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertIsNone(result.parent)

    def test_valid_parent_gets_set(self):
        # given
        parent = Task('parent')
        # when
        result = Task.from_dict({'parent': parent})
        # then
        self.assertIsInstance(result, Task)
        self.assertIs(parent, result.parent)

    def test_int_parent_raises(self):
        # expect
        self.assertRaises(
            Exception,
            Task.from_dict,
            {'parent': 1})

    def test_lazy_overrides_non_lazy_parent(self):
        # given
        parent = Task('parent')
        parent2 = Task('parent2')
        # when
        result = Task.from_dict({'parent': parent},
                                lazy={'parent': lambda: parent2})
        # then
        self.assertIsInstance(result, Task)
        self.assertIs(parent2, result.parent)

    def test_parent_id_none_is_ignored(self):
        # when
        result = Task.from_dict({'parent_id': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertIsNone(result.parent_id)

    def test_valid_parent_id_is_ignored(self):
        # given
        parent = Task('parent')
        # when
        result = Task.from_dict({'parent_id': parent.id})
        # then
        self.assertIsInstance(result, Task)
        self.assertIsNone(result.parent_id)

    def test_non_int_parent_id_is_ignored(self):
        # given
        parent = Task('parent')
        # when
        result = Task.from_dict({'parent_id': parent})
        # then
        self.assertIsInstance(result, Task)
        self.assertIsNone(result.parent_id)
        self.assertIsNone(result.parent)

    def test_children_none_yields_empty(self):
        # when
        result = Task.from_dict({'children': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.children))

    def test_children_empty_yields_empty(self):
        # when
        result = Task.from_dict({'children': []})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.children))

    def test_children_non_empty_yields_same(self):
        # given
        c1 = Task('c1')
        # when
        result = Task.from_dict({'children': [c1]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([c1], list(result.children))

    def test_lazy_overrides_non_lazy_children(self):
        # given
        child = Task('child')
        child2 = Task('child2')
        # when
        result = Task.from_dict({'children': [child]},
                                lazy={'children': [child2]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([child2], list(result.children))

    def test_tags_none_yields_empty(self):
        # when
        result = Task.from_dict({'tags': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.tags))

    def test_tags_empty_yields_empty(self):
        # when
        result = Task.from_dict({'tags': []})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.tags))

    def test_tags_non_empty_yields_same(self):
        # given
        tag = Tag('tag')
        # when
        result = Task.from_dict({'tags': [tag]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([tag], list(result.tags))

    def test_lazy_overrides_non_lazy_tags(self):
        # given
        tag = Tag('tag')
        tag2 = Tag('tag2')
        # when
        result = Task.from_dict({'tags': [tag]},
                                lazy={'tags': [tag2]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([tag2], list(result.tags))

    def test_users_none_yields_empty(self):
        # when
        result = Task.from_dict({'users': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.users))

    def test_users_empty_yields_empty(self):
        # when
        result = Task.from_dict({'users': []})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.users))

    def test_users_non_empty_yields_same(self):
        # given
        user = User('user')
        # when
        result = Task.from_dict({'users': [user]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([user], list(result.users))

    def test_lazy_overrides_non_lazy_users(self):
        # given
        user = User('user')
        user2 = User('user2')
        # when
        result = Task.from_dict({'users': [user]},
                                lazy={'users': [user2]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([user2], list(result.users))

    def test_dependees_none_yields_empty(self):
        # when
        result = Task.from_dict({'dependees': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.dependees))

    def test_dependees_empty_yields_empty(self):
        # when
        result = Task.from_dict({'dependees': []})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.dependees))

    def test_dependees_non_empty_yields_same(self):
        # given
        task = Task('task')
        # when
        result = Task.from_dict({'dependees': [task]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([task], list(result.dependees))

    def test_lazy_overrides_non_lazy_dependees(self):
        # given
        dependee = Task('dependee')
        dependee2 = Task('dependee2')
        # when
        result = Task.from_dict({'dependees': [dependee]},
                                lazy={'dependees': [dependee2]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([dependee2], list(result.dependees))

    def test_dependants_none_yields_empty(self):
        # when
        result = Task.from_dict({'dependants': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.dependants))

    def test_dependants_empty_yields_empty(self):
        # when
        result = Task.from_dict({'dependants': []})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.dependants))

    def test_dependants_non_empty_yields_same(self):
        # given
        task = Task('task')
        # when
        result = Task.from_dict({'dependants': [task]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([task], list(result.dependants))

    def test_lazy_overrides_non_lazy_dependants(self):
        # given
        dependant = Task('dependant')
        dependant2 = Task('dependant2')
        # when
        result = Task.from_dict({'dependants': [dependant]},
                                lazy={'dependants': [dependant2]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([dependant2], list(result.dependants))

    def test_prioritize_before_none_yields_empty(self):
        # when
        result = Task.from_dict({'prioritize_before': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.prioritize_before))

    def test_prioritize_before_empty_yields_empty(self):
        # when
        result = Task.from_dict({'prioritize_before': []})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.prioritize_before))

    def test_prioritize_before_non_empty_yields_same(self):
        # given
        task = Task('task')
        # when
        result = Task.from_dict({'prioritize_before': [task]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([task], list(result.prioritize_before))

    def test_lazy_overrides_non_lazy_prioritize_befores(self):
        # given
        prioritize_before = Task('prioritize_before')
        prioritize_before2 = Task('prioritize_before2')
        # when
        result = Task.from_dict(
            {'prioritize_before': [prioritize_before]},
            lazy={'prioritize_before': [prioritize_before2]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([prioritize_before2], list(result.prioritize_before))

    def test_prioritize_after_none_yields_empty(self):
        # when
        result = Task.from_dict({'prioritize_after': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.prioritize_after))

    def test_prioritize_after_empty_yields_empty(self):
        # when
        result = Task.from_dict({'prioritize_after': []})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.prioritize_after))

    def test_prioritize_after_non_empty_yields_same(self):
        # given
        task = Task('task')
        # when
        result = Task.from_dict({'prioritize_after': [task]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([task], list(result.prioritize_after))

    def test_lazy_overrides_non_lazy_prioritize_afters(self):
        # given
        prioritize_after = Task('prioritize_after')
        prioritize_after2 = Task('prioritize_after2')
        # when
        result = Task.from_dict({'prioritize_after': [prioritize_after]},
                                lazy={'prioritize_after': [prioritize_after2]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([prioritize_after2], list(result.prioritize_after))

    def test_notes_none_yields_empty(self):
        # when
        result = Task.from_dict({'notes': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.notes))

    def test_notes_empty_yields_empty(self):
        # when
        result = Task.from_dict({'notes': []})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.notes))

    def test_notes_non_empty_yields_same(self):
        # given
        note = Note('note')
        # when
        result = Task.from_dict({'notes': [note]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([note], list(result.notes))

    def test_lazy_overrides_non_lazy_notes(self):
        # given
        note = Note('note')
        note2 = Note('note2')
        # when
        result = Task.from_dict({'notes': [note]},
                                lazy={'notes': [note2]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([note2], list(result.notes))

    def test_attachments_none_yields_empty(self):
        # when
        result = Task.from_dict({'attachments': None})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.attachments))

    def test_attachments_empty_yields_empty(self):
        # when
        result = Task.from_dict({'attachments': []})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([], list(result.attachments))

    def test_attachments_non_empty_yields_same(self):
        # given
        attachment = Attachment('attachment')
        # when
        result = Task.from_dict({'attachments': [attachment]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([attachment], list(result.attachments))

    def test_lazy_overrides_non_lazy_attachments(self):
        # given
        attachment = Attachment('attachment')
        attachment2 = Attachment('attachment2')
        # when
        result = Task.from_dict({'attachments': [attachment]},
                                lazy={'attachments': [attachment2]})
        # then
        self.assertIsInstance(result, Task)
        self.assertEqual([attachment2], list(result.attachments))
