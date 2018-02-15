from datetime import datetime
from decimal import Decimal

from tests.persistence_t.persistence_layer.util import \
    PersistenceLayerTestBase


class DbTaskFromDictTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_empty_yields_empty_dbtask(self):
        # when
        result = self.pl.DbTask.from_dict({})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
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
        result = self.pl.DbTask.from_dict({'id': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.id)

    def test_valid_id_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'id': 123})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual(123, result.id)

    def test_summary_none_is_ignored(self):
        # when
        result = self.pl.DbTask.from_dict({'summary': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.summary)

    def test_valid_summary_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'summary': 'abc'})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual('abc', result.summary)

    def test_description_none_becomes_none(self):
        # when
        result = self.pl.DbTask.from_dict({'description': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.description)

    def test_valid_description_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'description': 'abc'})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual('abc', result.description)

    def test_is_done_none_is_becomes_false(self):
        # when
        result = self.pl.DbTask.from_dict({'is_done': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertFalse(result.is_done)

    def test_valid_is_done_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'is_done': True})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertTrue(result.is_done)

    def test_is_deleted_none_becomes_false(self):
        # when
        result = self.pl.DbTask.from_dict({'is_deleted': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertFalse(result.is_deleted)

    def test_valid_is_deleted_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'is_deleted': True})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertTrue(result.is_deleted)

    def test_order_num_none_becomes_none(self):
        # when
        result = self.pl.DbTask.from_dict({'order_num': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.order_num)

    def test_valid_order_num_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'order_num': 123})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual(123, result.order_num)

    def test_deadline_none_is_ignored(self):
        # when
        result = self.pl.DbTask.from_dict({'deadline': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.deadline)

    def test_valid_deadline_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'deadline': datetime(2017, 01, 01)})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual(datetime(2017, 01, 01), result.deadline)

    def test_string_deadline_becomes_datetime(self):
        # when
        result = self.pl.DbTask.from_dict({'deadline': '2017-01-01'})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual(datetime(2017, 01, 01), result.deadline)

    def test_expected_duration_minutes_none_is_ignored(self):
        # when
        result = self.pl.DbTask.from_dict({'expected_duration_minutes': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.expected_duration_minutes)

    def test_valid_expected_duration_minutes_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'expected_duration_minutes': 123})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual(123, result.expected_duration_minutes)

    def test_expected_cost_none_is_ignored(self):
        # when
        result = self.pl.DbTask.from_dict({'expected_cost': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.expected_cost)

    def test_valid_expected_cost_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'expected_cost': Decimal(123.45)})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsInstance(result.expected_cost, Decimal)
        self.assertEqual(Decimal('123.45'), result.expected_cost)

    def test_float_expected_cost_gets_set_as_float(self):
        # when
        result = self.pl.DbTask.from_dict({'expected_cost': 123.45})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsInstance(result.expected_cost, Decimal)
        self.assertEqual(Decimal('123.45'), result.expected_cost)

    def test_string_expected_cost_gets_set_as_decimal(self):
        # when
        result = self.pl.DbTask.from_dict({'expected_cost': '123.45'})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsInstance(result.expected_cost, Decimal)
        self.assertEqual(Decimal('123.45'), result.expected_cost)

    def test_parent_none_is_ignored(self):
        # when
        result = self.pl.DbTask.from_dict({'parent': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.parent)

    def test_valid_parent_gets_set(self):
        # given
        parent = self.pl.DbTask('parent')
        self.pl.db.session.add(parent)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'parent': parent})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIs(parent, result.parent)
        # and parent_id is not yet set
        self.assertIsNone(result.parent_id)

    def test_int_parent_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl.DbTask.from_dict,
            {'parent': 1})

    def test_parent_id_none_is_ignored(self):
        # when
        result = self.pl.DbTask.from_dict({'parent_id': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.parent_id)
        # and parent is not yet set
        self.assertIsNone(result.parent)

    def test_valid_parent_id_is_ignored(self):
        # given
        parent = self.pl.DbTask('parent')
        self.pl.db.session.add(parent)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'parent_id': parent.id})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.parent_id)
        # and parent is not yet set
        self.assertIsNone(result.parent)

    def test_non_int_parent_id_is_ignored(self):
        # given
        parent = self.pl.DbTask('parent')
        self.pl.db.session.add(parent)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'parent_id': parent})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.parent_id)
        self.assertIsNone(result.parent)

    def test_children_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'children': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.children))

    def test_children_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'children': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.children))

    def test_children_non_empty_yields_same(self):
        # given
        c1 = self.pl.DbTask('c1')
        self.pl.db.session.add(c1)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'children': [c1]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([c1], list(result.children))

    def test_tags_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'tags': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.tags))

    def test_tags_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'tags': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.tags))

    def test_tags_non_empty_yields_same(self):
        # given
        tag = self.pl.DbTag('tag')
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'tags': [tag]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([tag], list(result.tags))

    def test_users_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'users': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.users))

    def test_users_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'users': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.users))

    def test_users_non_empty_yields_same(self):
        # given
        user = self.pl.DbUser('user')
        self.pl.db.session.add(user)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'users': [user]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([user], list(result.users))

    def test_dependees_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'dependees': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.dependees))

    def test_dependees_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'dependees': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.dependees))

    def test_dependees_non_empty_yields_same(self):
        # given
        task = self.pl.DbTask('task')
        self.pl.db.session.add(task)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'dependees': [task]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([task], list(result.dependees))

    def test_dependants_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'dependants': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.dependants))

    def test_dependants_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'dependants': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.dependants))

    def test_dependants_non_empty_yields_same(self):
        # given
        task = self.pl.DbTask('task')
        self.pl.db.session.add(task)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'dependants': [task]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([task], list(result.dependants))

    def test_prioritize_before_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'prioritize_before': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.prioritize_before))

    def test_prioritize_before_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'prioritize_before': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.prioritize_before))

    def test_prioritize_before_non_empty_yields_same(self):
        # given
        task = self.pl.DbTask('task')
        self.pl.db.session.add(task)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'prioritize_before': [task]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([task], list(result.prioritize_before))

    def test_prioritize_after_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'prioritize_after': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.prioritize_after))

    def test_prioritize_after_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'prioritize_after': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.prioritize_after))

    def test_prioritize_after_non_empty_yields_same(self):
        # given
        task = self.pl.DbTask('task')
        self.pl.db.session.add(task)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'prioritize_after': [task]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([task], list(result.prioritize_after))

    def test_notes_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'notes': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.notes))

    def test_notes_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'notes': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.notes))

    def test_notes_non_empty_yields_same(self):
        # given
        note = self.pl.DbNote('note')
        self.pl.db.session.add(note)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'notes': [note]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([note], list(result.notes))

    def test_attachments_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'attachments': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.attachments))

    def test_attachments_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'attachments': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.attachments))

    def test_attachments_non_empty_yields_same(self):
        # given
        attachment = self.pl.DbAttachment('attachment')
        self.pl.db.session.add(attachment)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'attachments': [attachment]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([attachment], list(result.attachments))

    def test_none_lazy_does_not_raise(self):
        # when
        result = self.pl.DbTask.from_dict({}, lazy=None)
        # then
        self.assertIsInstance(result, self.pl.DbTask)
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

    def test_empty_lazy_does_not_raise(self):
        # when
        result = self.pl.DbTask.from_dict({}, lazy={})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
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

    def test_non_none_lazy_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl.DbTask.from_dict,
            {},
            lazy={'attachments': None})
