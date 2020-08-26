import unittest

from datetime import datetime

from tests.models_t.task_base.util import GenericTask, Item


class TaskToFlatDictTest(unittest.TestCase):
    def test_fields_none_exports_all(self):
        # given
        parent, c1, c2 = Item(), Item(), Item()
        d1, d2, d3, d4 = Item(), Item(), Item(), Item()
        p1, p2, p3, p4 = Item(), Item(), Item(), Item()
        t1, t2, u1, u2 = Item(), Item(), Item(), Item()
        n1, n2, a1, a2 = Item(), Item(), Item(), Item()
        task = GenericTask(
            summary='summary', description='desc', is_done=False,
            is_deleted=False, deadline=datetime(2020, 1, 1),
            expected_duration_minutes=30, expected_cost=123, is_public=False,
            id=456, parent=parent, children=[c1, c2], dependees=[d1, d2],
            dependants=[d3, d4], prioritize_before=[p1, p2],
            prioritize_after=[p3, p4], tags=[t1, t2], users=[u1, u2],
            notes=[n1, n2], attachments=[a1, a2])
        # precondition
        self.assertEqual(456, task.id)
        self.assertEqual('summary', task.summary)
        self.assertEqual('desc', task.description)
        self.assertIs(False, task.is_done)
        self.assertIs(False, task.is_deleted)
        self.assertEqual(datetime(2020, 1, 1), task.deadline)
        self.assertEqual(30, task.expected_duration_minutes)
        self.assertEqual(123, task.expected_cost)
        self.assertIs(False, task.is_public)
        self.assertIs(parent, task.parent)
        self.assertEqual([c1, c2], task.children)
        self.assertEqual([d1, d2], task.dependees)
        self.assertEqual([d3, d4], task.dependants)
        self.assertEqual([p1, p2], task.prioritize_before)
        self.assertEqual([p3, p4], task.prioritize_after)
        self.assertEqual([t1, t2], task.tags)
        self.assertEqual([u1, u2], task.users)
        self.assertEqual([n1, n2], task.notes)
        self.assertEqual([a1, a2], task.attachments)
        # when
        d = task.to_flat_dict(fields=None)
        # then
        self.assertEqual(20, len(d))
        self.assertIn('id', d)
        self.assertEqual(456, d['id'])
        self.assertIn('summary', d)
        self.assertEqual('summary', d['summary'])
        self.assertIn('description', d)
        self.assertEqual('desc', d['description'])
        self.assertIn('is_done', d)
        self.assertIs(False, d['is_done'])
        self.assertIn('is_deleted', d)
        self.assertIs(False, d['is_deleted'])
        self.assertIn('deadline', d)
        self.assertEqual('2020-01-01 00:00:00', d['deadline'])
        self.assertIn('expected_duration_minutes', d)
        self.assertEqual(30, d['expected_duration_minutes'])
        self.assertIn('expected_cost', d)
        self.assertEqual('123.00', d['expected_cost'])
        self.assertIn('is_public', d)
        self.assertIs(False, d['is_public'])
        self.assertIn('parent_id', d)
        self.assertIs(parent.id, d['parent_id'])
        self.assertIn('children_ids', d)
        self.assertEqual([c1.id, c2.id], d['children_ids'])
        self.assertIn('dependee_ids', d)
        self.assertEqual([d1.id, d2.id], d['dependee_ids'])
        self.assertIn('dependant_ids', d)
        self.assertEqual([d3.id, d4.id], d['dependant_ids'])
        self.assertIn('prioritize_before_ids', d)
        self.assertEqual([p1.id, p2.id], d['prioritize_before_ids'])
        self.assertIn('prioritize_after_ids', d)
        self.assertEqual([p3.id, p4.id], d['prioritize_after_ids'])
        self.assertIn('tag_ids', d)
        self.assertEqual([t1.id, t2.id], d['tag_ids'])
        self.assertIn('user_ids', d)
        self.assertEqual([u1.id, u2.id], d['user_ids'])
        self.assertIn('note_ids', d)
        self.assertEqual([n1.id, n2.id], d['note_ids'])
        self.assertIn('attachment_ids', d)
        self.assertEqual([a1.id, a2.id], d['attachment_ids'])

    def test_fields_id_exports_only_id(self):
        # given
        # given
        parent, c1, c2 = Item(), Item(), Item()
        d1, d2, d3, d4 = Item(), Item(), Item(), Item()
        p1, p2, p3, p4 = Item(), Item(), Item(), Item()
        t1, t2, u1, u2 = Item(), Item(), Item(), Item()
        n1, n2, a1, a2 = Item(), Item(), Item(), Item()
        task = GenericTask(
            summary='summary', description='desc', is_done=False,
            is_deleted=False, deadline=datetime(2020, 1, 1),
            expected_duration_minutes=30, expected_cost=123, is_public=False,
            id=456, parent=parent, children=[c1, c2], dependees=[d1, d2],
            dependants=[d3, d4], prioritize_before=[p1, p2],
            prioritize_after=[p3, p4], tags=[t1, t2], users=[u1, u2],
            notes=[n1, n2], attachments=[a1, a2])
        # precondition
        self.assertEqual(456, task.id)
        self.assertEqual('summary', task.summary)
        self.assertEqual('desc', task.description)
        self.assertIs(False, task.is_done)
        self.assertIs(False, task.is_deleted)
        self.assertEqual(datetime(2020, 1, 1), task.deadline)
        self.assertEqual(30, task.expected_duration_minutes)
        self.assertEqual(123, task.expected_cost)
        self.assertIs(False, task.is_public)
        self.assertIs(parent, task.parent)
        self.assertEqual([c1, c2], task.children)
        self.assertEqual([d1, d2], task.dependees)
        self.assertEqual([d3, d4], task.dependants)
        self.assertEqual([p1, p2], task.prioritize_before)
        self.assertEqual([p3, p4], task.prioritize_after)
        self.assertEqual([t1, t2], task.tags)
        self.assertEqual([u1, u2], task.users)
        self.assertEqual([n1, n2], task.notes)
        self.assertEqual([a1, a2], task.attachments)
        # when
        d = task.to_flat_dict(fields=[task.FIELD_ID])
        # then
        self.assertEqual(1, len(d))
        self.assertIn('id', d)
        self.assertEqual(456, d['id'])
        self.assertNotIn('summary', d)
        self.assertNotIn('description', d)
        self.assertNotIn('is_done', d)
        self.assertNotIn('is_deleted', d)
        self.assertNotIn('deadline', d)
        self.assertNotIn('expected_duration_minutes', d)
        self.assertNotIn('expected_cost', d)
        self.assertNotIn('is_public', d)
        self.assertNotIn('parent', d)
        self.assertNotIn('children_ids', d)
        self.assertNotIn('dependee_ids', d)
        self.assertNotIn('dependant_ids', d)
        self.assertNotIn('prioritize_before_ids', d)
        self.assertNotIn('prioritize_after_ids', d)
        self.assertNotIn('tag_ids', d)
        self.assertNotIn('user_ids', d)
        self.assertNotIn('note_ids', d)
        self.assertNotIn('attachments', d)

    def test_fields_children_exports_only_children_ids(self):
        # given
        # given
        parent, c1, c2 = Item(), Item(), Item()
        d1, d2, d3, d4 = Item(), Item(), Item(), Item()
        p1, p2, p3, p4 = Item(), Item(), Item(), Item()
        t1, t2, u1, u2 = Item(), Item(), Item(), Item()
        n1, n2, a1, a2 = Item(), Item(), Item(), Item()
        task = GenericTask(
            summary='summary', description='desc', is_done=False,
            is_deleted=False, deadline=datetime(2020, 1, 1),
            expected_duration_minutes=30, expected_cost=123, is_public=False,
            id=456, parent=parent, children=[c1, c2], dependees=[d1, d2],
            dependants=[d3, d4], prioritize_before=[p1, p2],
            prioritize_after=[p3, p4], tags=[t1, t2], users=[u1, u2],
            notes=[n1, n2], attachments=[a1, a2])
        # precondition
        self.assertEqual(456, task.id)
        self.assertEqual('summary', task.summary)
        self.assertEqual('desc', task.description)
        self.assertIs(False, task.is_done)
        self.assertIs(False, task.is_deleted)
        self.assertEqual(datetime(2020, 1, 1), task.deadline)
        self.assertEqual(30, task.expected_duration_minutes)
        self.assertEqual(123, task.expected_cost)
        self.assertIs(False, task.is_public)
        self.assertIs(parent, task.parent)
        self.assertEqual([c1, c2], task.children)
        self.assertEqual([d1, d2], task.dependees)
        self.assertEqual([d3, d4], task.dependants)
        self.assertEqual([p1, p2], task.prioritize_before)
        self.assertEqual([p3, p4], task.prioritize_after)
        self.assertEqual([t1, t2], task.tags)
        self.assertEqual([u1, u2], task.users)
        self.assertEqual([n1, n2], task.notes)
        self.assertEqual([a1, a2], task.attachments)
        # when
        d = task.to_flat_dict(fields=[task.FIELD_CHILDREN])
        # then
        self.assertEqual(1, len(d))
        self.assertNotIn('id', d)
        self.assertNotIn('summary', d)
        self.assertNotIn('description', d)
        self.assertNotIn('is_done', d)
        self.assertNotIn('is_deleted', d)
        self.assertNotIn('deadline', d)
        self.assertNotIn('expected_duration_minutes', d)
        self.assertNotIn('expected_cost', d)
        self.assertNotIn('is_public', d)
        self.assertNotIn('parent', d)
        self.assertIn('children_ids', d)
        self.assertEqual([c1.id, c2.id], d['children_ids'])
        self.assertNotIn('dependee_ids', d)
        self.assertNotIn('dependant_ids', d)
        self.assertNotIn('prioritize_before_ids', d)
        self.assertNotIn('prioritize_after_ids', d)
        self.assertNotIn('tag_ids', d)
        self.assertNotIn('user_ids', d)
        self.assertNotIn('note_ids', d)
        self.assertNotIn('attachments', d)

    def test_multiple_fields_exports_those_indicated(self):
        # given
        parent, c1, c2 = Item(), Item(), Item()
        d1, d2, d3, d4 = Item(), Item(), Item(), Item()
        p1, p2, p3, p4 = Item(), Item(), Item(), Item()
        t1, t2, u1, u2 = Item(), Item(), Item(), Item()
        n1, n2, a1, a2 = Item(), Item(), Item(), Item()
        task = GenericTask(
            summary='summary', description='desc', is_done=False,
            is_deleted=False, deadline=datetime(2020, 1, 1),
            expected_duration_minutes=30, expected_cost=123, is_public=False,
            id=456, parent=parent, children=[c1, c2], dependees=[d1, d2],
            dependants=[d3, d4], prioritize_before=[p1, p2],
            prioritize_after=[p3, p4], tags=[t1, t2], users=[u1, u2],
            notes=[n1, n2], attachments=[a1, a2])
        # precondition
        self.assertEqual(456, task.id)
        self.assertEqual('summary', task.summary)
        self.assertEqual('desc', task.description)
        self.assertIs(False, task.is_done)
        self.assertIs(False, task.is_deleted)
        self.assertEqual(datetime(2020, 1, 1), task.deadline)
        self.assertEqual(30, task.expected_duration_minutes)
        self.assertEqual(123, task.expected_cost)
        self.assertIs(False, task.is_public)
        self.assertIs(parent, task.parent)
        self.assertEqual([c1, c2], task.children)
        self.assertEqual([d1, d2], task.dependees)
        self.assertEqual([d3, d4], task.dependants)
        self.assertEqual([p1, p2], task.prioritize_before)
        self.assertEqual([p3, p4], task.prioritize_after)
        self.assertEqual([t1, t2], task.tags)
        self.assertEqual([u1, u2], task.users)
        self.assertEqual([n1, n2], task.notes)
        self.assertEqual([a1, a2], task.attachments)
        # when
        d = task.to_flat_dict(fields=[task.FIELD_CHILDREN, task.FIELD_SUMMARY,
                                      task.FIELD_USERS])
        # then
        self.assertEqual(3, len(d))
        self.assertNotIn('id', d)
        self.assertIn('summary', d)
        self.assertEqual('summary', d['summary'])
        self.assertNotIn('description', d)
        self.assertNotIn('is_done', d)
        self.assertNotIn('is_deleted', d)
        self.assertNotIn('deadline', d)
        self.assertNotIn('expected_duration_minutes', d)
        self.assertNotIn('expected_cost', d)
        self.assertNotIn('is_public', d)
        self.assertNotIn('parent', d)
        self.assertIn('children_ids', d)
        self.assertEqual([c1.id, c2.id], d['children_ids'])
        self.assertNotIn('dependee_ids', d)
        self.assertNotIn('dependant_ids', d)
        self.assertNotIn('prioritize_before_ids', d)
        self.assertNotIn('prioritize_after_ids', d)
        self.assertNotIn('tag_ids', d)
        self.assertIn('user_ids', d)
        self.assertEqual([u1.id, u2.id], d['user_ids'])
        self.assertNotIn('note_ids', d)
        self.assertNotIn('attachments', d)

    def test_all_fields_exports_all(self):
        # given
        parent, c1, c2 = Item(), Item(), Item()
        d1, d2, d3, d4 = Item(), Item(), Item(), Item()
        p1, p2, p3, p4 = Item(), Item(), Item(), Item()
        t1, t2, u1, u2 = Item(), Item(), Item(), Item()
        n1, n2, a1, a2 = Item(), Item(), Item(), Item()
        task = GenericTask(
            summary='summary', description='desc', is_done=False,
            is_deleted=False, deadline=datetime(2020, 1, 1),
            expected_duration_minutes=30, expected_cost=123, is_public=False,
            id=456, parent=parent, children=[c1, c2], dependees=[d1, d2],
            dependants=[d3, d4], prioritize_before=[p1, p2],
            prioritize_after=[p3, p4], tags=[t1, t2], users=[u1, u2],
            notes=[n1, n2], attachments=[a1, a2])
        # precondition
        self.assertEqual(456, task.id)
        self.assertEqual('summary', task.summary)
        self.assertEqual('desc', task.description)
        self.assertIs(False, task.is_done)
        self.assertIs(False, task.is_deleted)
        self.assertEqual(datetime(2020, 1, 1), task.deadline)
        self.assertEqual(30, task.expected_duration_minutes)
        self.assertEqual(123, task.expected_cost)
        self.assertIs(False, task.is_public)
        self.assertIs(parent, task.parent)
        self.assertEqual([c1, c2], task.children)
        self.assertEqual([d1, d2], task.dependees)
        self.assertEqual([d3, d4], task.dependants)
        self.assertEqual([p1, p2], task.prioritize_before)
        self.assertEqual([p3, p4], task.prioritize_after)
        self.assertEqual([t1, t2], task.tags)
        self.assertEqual([u1, u2], task.users)
        self.assertEqual([n1, n2], task.notes)
        self.assertEqual([a1, a2], task.attachments)
        # when
        d = task.to_flat_dict(
            fields=[
                task.FIELD_ID, task.FIELD_SUMMARY, task.FIELD_DESCRIPTION,
                task.FIELD_IS_DONE, task.FIELD_IS_DELETED,
                task.FIELD_DEADLINE, task.FIELD_EXPECTED_DURATION_MINUTES,
                task.FIELD_EXPECTED_COST, task.FIELD_ORDER_NUM,
                task.FIELD_PARENT, task.FIELD_CHILDREN, task.FIELD_DEPENDEES,
                task.FIELD_DEPENDANTS, task.FIELD_PRIORITIZE_BEFORE,
                task.FIELD_PRIORITIZE_AFTER, task.FIELD_TAGS,
                task.FIELD_USERS, task.FIELD_NOTES, task.FIELD_ATTACHMENTS,
                task.FIELD_IS_PUBLIC])
        # then
        self.assertEqual(20, len(d))
        self.assertIn('id', d)
        self.assertEqual(456, d['id'])
        self.assertIn('summary', d)
        self.assertEqual('summary', d['summary'])
        self.assertIn('description', d)
        self.assertEqual('desc', d['description'])
        self.assertIn('is_done', d)
        self.assertIs(False, d['is_done'])
        self.assertIn('is_deleted', d)
        self.assertIs(False, d['is_deleted'])
        self.assertIn('deadline', d)
        self.assertEqual('2020-01-01 00:00:00', d['deadline'])
        self.assertIn('expected_duration_minutes', d)
        self.assertEqual(30, d['expected_duration_minutes'])
        self.assertIn('expected_cost', d)
        self.assertEqual('123.00', d['expected_cost'])
        self.assertIn('is_public', d)
        self.assertIs(False, d['is_public'])
        self.assertIn('parent_id', d)
        self.assertIs(parent.id, d['parent_id'])
        self.assertIn('children_ids', d)
        self.assertEqual([c1.id, c2.id], d['children_ids'])
        self.assertIn('dependee_ids', d)
        self.assertEqual([d1.id, d2.id], d['dependee_ids'])
        self.assertIn('dependant_ids', d)
        self.assertEqual([d3.id, d4.id], d['dependant_ids'])
        self.assertIn('prioritize_before_ids', d)
        self.assertEqual([p1.id, p2.id], d['prioritize_before_ids'])
        self.assertIn('prioritize_after_ids', d)
        self.assertEqual([p3.id, p4.id], d['prioritize_after_ids'])
        self.assertIn('tag_ids', d)
        self.assertEqual([t1.id, t2.id], d['tag_ids'])
        self.assertIn('user_ids', d)
        self.assertEqual([u1.id, u2.id], d['user_ids'])
        self.assertIn('note_ids', d)
        self.assertEqual([n1.id, n2.id], d['note_ids'])
        self.assertIn('attachment_ids', d)
        self.assertEqual([a1.id, a2.id], d['attachment_ids'])

    def test_list_empty_exports_none(self):
        # given
        parent, c1, c2 = Item(), Item(), Item()
        d1, d2, d3, d4 = Item(), Item(), Item(), Item()
        p1, p2, p3, p4 = Item(), Item(), Item(), Item()
        t1, t2, u1, u2 = Item(), Item(), Item(), Item()
        n1, n2, a1, a2 = Item(), Item(), Item(), Item()
        task = GenericTask(
            summary='summary', description='desc', is_done=False,
            is_deleted=False, deadline=datetime(2020, 1, 1),
            expected_duration_minutes=30, expected_cost=123, is_public=False,
            id=456, parent=parent, children=[c1, c2], dependees=[d1, d2],
            dependants=[d3, d4], prioritize_before=[p1, p2],
            prioritize_after=[p3, p4], tags=[t1, t2], users=[u1, u2],
            notes=[n1, n2], attachments=[a1, a2])
        # precondition
        self.assertEqual(456, task.id)
        self.assertEqual('summary', task.summary)
        self.assertEqual('desc', task.description)
        self.assertIs(False, task.is_done)
        self.assertIs(False, task.is_deleted)
        self.assertEqual(datetime(2020, 1, 1), task.deadline)
        self.assertEqual(30, task.expected_duration_minutes)
        self.assertEqual(123, task.expected_cost)
        self.assertIs(False, task.is_public)
        self.assertIs(parent, task.parent)
        self.assertEqual([c1, c2], task.children)
        self.assertEqual([d1, d2], task.dependees)
        self.assertEqual([d3, d4], task.dependants)
        self.assertEqual([p1, p2], task.prioritize_before)
        self.assertEqual([p3, p4], task.prioritize_after)
        self.assertEqual([t1, t2], task.tags)
        self.assertEqual([u1, u2], task.users)
        self.assertEqual([n1, n2], task.notes)
        self.assertEqual([a1, a2], task.attachments)
        # when
        d = task.to_flat_dict(fields=[])
        # then
        self.assertEqual({}, d)
