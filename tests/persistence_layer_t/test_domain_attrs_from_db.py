import types
import unittest

from models.attachment import Attachment
from models.note import Note
from models.tag import Tag
from models.task import Task
from models.user import User
from tests.persistence_layer_t.util import generate_pl


class DomainAttrsFromDbTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_all_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl._domain_attrs_from_db_all, None)

    def test_no_links_none_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl._domain_attrs_from_db_no_links,
            None)

    def test_links_none_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl._domain_attrs_from_db_links,
            None)

    def test_links_lazy_none_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl._domain_attrs_from_db_links_lazy,
            None)

    def test_all_empty_yields_empty(self):
        # expect
        self.assertEqual({}, self.pl._domain_attrs_from_db_all({}))

    def test_no_links_empty_yields_empty(self):
        # expect
        self.assertEqual({}, self.pl._domain_attrs_from_db_no_links({}))

    def test_links_empty_yields_empty(self):
        # expect
        self.assertEqual({}, self.pl._domain_attrs_from_db_links({}))

    def test_links_lazy_empty_yields_empty(self):
        # expect
        self.assertEqual({}, self.pl._domain_attrs_from_db_links_lazy({}))

    def test_no_links_passing_d2_returns_same(self):
        # given
        d2 = {}
        # when
        result = self.pl._domain_attrs_from_db_no_links({}, d2)
        # then
        self.assertIs(d2, result)

    def test_links_passing_d2_returns_same(self):
        # given
        d2 = {}
        # when
        result = self.pl._domain_attrs_from_db_links({}, d2)
        # then
        self.assertIs(d2, result)

    def test_links_lazy_passing_d2_returns_same(self):
        # given
        d2 = {}
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({}, d2)
        # then
        self.assertIs(d2, result)

    def test_no_links_parent_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'parent': 1}))

    def test_no_links_children_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'children': 1}))

    def test_no_links_tags_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'tags': 1}))

    def test_no_links_tasks_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'tasks': 1}))

    def test_no_links_users_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'users': 1}))

    def test_no_links_dependees_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'dependees': 1}))

    def test_no_links_dependants_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'dependants': 1}))

    def test_no_links_prioritize_before_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links(
                {'prioritize_before': 1}))

    def test_no_links_prioritize_after_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links(
                {'prioritize_after': 1}))

    def test_no_links_notes_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'notes': 1}))

    def test_no_links_attachments_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'attachments': 1}))

    def test_no_links_task_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'task': 1}))

    def test_no_links_non_relational_attrs_are_copied(self):
        # given
        d = {
            'timestamp': 123,
            'x': 456,
            0: 789,
            object(): None
        }
        # when
        result = self.pl._domain_attrs_from_db_no_links(d)
        # then
        self.assertIsNot(d, result)
        self.assertEqual(d, result)

    def test_links_non_relational_attrs_are_ignored(self):
        # given
        d = {
            'timestamp': 123,
            'x': 456,
            0: 789,
            object(): None
        }
        # expect
        self.assertEqual({}, self.pl._domain_attrs_from_db_links(d))

    def test_links_parent_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'parent': None}))

    def test_links_children_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'children': None}))

    def test_links_tags_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'tags': None}))

    def test_links_tasks_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'tasks': None}))

    def test_links_users_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'users': None}))

    def test_links_dependees_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'dependees': None}))

    def test_links_dependants_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'dependants': None}))

    def test_links_prioritize_before_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links(
                {'prioritize_before': None}))

    def test_links_prioritize_after_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links(
                {'prioritize_after': None}))

    def test_links_notes_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'notes': None}))

    def test_links_attachments_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'attachments': None}))

    def test_links_task_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'task': None}))

    def test_links_parent_is_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'parent': dbtask})
        # then
        self.assertEqual({'parent': task}, result)

    def test_links_children_are_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'children': [dbtask]})
        # then
        self.assertEqual({'children': [task]}, result)

    def test_links_tags_are_translated(self):
        # given
        tag = Tag('tag')
        self.pl.add(tag)
        self.pl.commit()
        dbtag = self.pl._get_db_object_from_domain_object(tag)
        # when
        result = self.pl._domain_attrs_from_db_links({'tags': [dbtag]})
        # then
        self.assertEqual({'tags': [tag]}, result)

    def test_links_tasks_are_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'tasks': [dbtask]})
        # then
        self.assertEqual({'tasks': [task]}, result)

    def test_links_users_are_translated(self):
        # given
        user = User('name@example.com')
        self.pl.add(user)
        self.pl.commit()
        dbuser = self.pl._get_db_object_from_domain_object(user)
        # when
        result = self.pl._domain_attrs_from_db_links({'users': [dbuser]})
        # then
        self.assertEqual({'users': [user]}, result)

    def test_links_dependees_are_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'dependees':
                                                      [dbtask]})
        # then
        self.assertEqual({'dependees': [task]}, result)

    def test_links_dependants_are_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'dependants':
                                                      [dbtask]})
        # then
        self.assertEqual({'dependants': [task]}, result)

    def test_links_prioritize_before_are_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'prioritize_before':
                                                      [dbtask]})
        # then
        self.assertEqual({'prioritize_before': [task]}, result)

    def test_links_prioritize_after_are_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'prioritize_after':
                                                      [dbtask]})
        # then
        self.assertEqual({'prioritize_after': [task]}, result)

    def test_links_notes_are_translated(self):
        # given
        note = Note('note')
        self.pl.add(note)
        self.pl.commit()
        dbnote = self.pl._get_db_object_from_domain_object(note)
        # when
        result = self.pl._domain_attrs_from_db_links({'notes': [dbnote]})
        # then
        self.assertEqual({'notes': [note]}, result)

    def test_links_attachments_are_translated(self):
        # given
        att = Attachment('att')
        self.pl.add(att)
        self.pl.commit()
        dbatt = self.pl._get_db_object_from_domain_object(att)
        # when
        result = self.pl._domain_attrs_from_db_links({'attachments':
                                                      [dbatt]})
        # then
        self.assertEqual({'attachments': [att]}, result)

    def test_links_task_is_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'task': dbtask})
        # then
        self.assertEqual({'task': task}, result)

    def test_links_lazy_non_relational_attrs_are_ignored(self):
        # given
        d = {
            'timestamp': 123,
            'x': 456,
            0: 789,
            object(): None
        }
        # expect
        self.assertEqual({}, self.pl._domain_attrs_from_db_links_lazy(d))

    def test_links_lazy_parent_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'parent': None}))

    def test_links_lazy_children_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'children': None}))

    def test_links_lazy_tags_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'tags': None}))

    def test_links_lazy_tasks_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'tasks': None}))

    def test_links_lazy_users_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'users': None}))

    def test_links_lazy_dependees_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'dependees': None}))

    def test_links_lazy_dependants_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'dependants': None}))

    def test_links_lazy_prioritize_before_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy(
                {'prioritize_before': None}))

    def test_links_lazy_prioritize_after_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy(
                {'prioritize_after': None}))

    def test_links_lazy_notes_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'notes': None}))

    def test_links_lazy_attachments_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'attachments':
                                                          None}))

    def test_links_lazy_task_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'task': None}))

    def test_links_lazy_parent_is_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'parent': dbtask})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('parent', result)
        self.assertTrue(callable(result['parent']))
        self.assertEqual(task, result['parent']())

    def test_links_lazy_children_are_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'children':
                                                           [dbtask]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('children', result)
        self.assertIsInstance(result['children'], types.GeneratorType)
        self.assertEqual([task], list(result['children']))

    def test_links_lazy_tags_are_translated_lazily(self):
        # given
        tag = Tag('tag')
        self.pl.add(tag)
        self.pl.commit()
        dbtag = self.pl._get_db_object_from_domain_object(tag)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'tags': [dbtag]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('tags', result)
        self.assertIsInstance(result['tags'], types.GeneratorType)
        self.assertEqual([tag], list(result['tags']))

    def test_links_lazy_tasks_are_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'tasks': [dbtask]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('tasks', result)
        self.assertIsInstance(result['tasks'], types.GeneratorType)
        self.assertEqual([task], list(result['tasks']))

    def test_links_lazy_users_are_translated_lazily(self):
        # given
        user = User('name@example.com')
        self.pl.add(user)
        self.pl.commit()
        dbuser = self.pl._get_db_object_from_domain_object(user)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'users': [dbuser]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('users', result)
        self.assertIsInstance(result['users'], types.GeneratorType)
        self.assertEqual([user], list(result['users']))

    def test_links_lazy_dependees_are_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'dependees':
                                                           [dbtask]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('dependees', result)
        self.assertIsInstance(result['dependees'], types.GeneratorType)
        self.assertEqual([task], list(result['dependees']))

    def test_links_lazy_dependants_are_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'dependants':
                                                           [dbtask]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('dependants', result)
        self.assertIsInstance(result['dependants'], types.GeneratorType)
        self.assertEqual([task], list(result['dependants']))

    def test_links_lazy_prioritize_before_are_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'prioritize_before':
                                                           [dbtask]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('prioritize_before', result)
        self.assertIsInstance(result['prioritize_before'], types.GeneratorType)
        self.assertEqual([task], list(result['prioritize_before']))

    def test_links_lazy_prioritize_after_are_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'prioritize_after':
                                                           [dbtask]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('prioritize_after', result)
        self.assertIsInstance(result['prioritize_after'], types.GeneratorType)
        self.assertEqual([task], list(result['prioritize_after']))

    def test_links_lazy_notes_are_translated_lazily(self):
        # given
        note = Note('note')
        self.pl.add(note)
        self.pl.commit()
        dbnote = self.pl._get_db_object_from_domain_object(note)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'notes': [dbnote]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('notes', result)
        self.assertIsInstance(result['notes'], types.GeneratorType)
        self.assertEqual([note], list(result['notes']))

    def test_links_lazy_attachments_are_translated_lazily(self):
        # given
        att = Attachment('att')
        self.pl.add(att)
        self.pl.commit()
        dbatt = self.pl._get_db_object_from_domain_object(att)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'attachments':
                                                           [dbatt]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('attachments', result)
        self.assertIsInstance(result['attachments'], types.GeneratorType)
        self.assertEqual([att], list(result['attachments']))

    def test_links_lazy_task_is_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'task': dbtask})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('task', result)
        self.assertTrue(callable(result['task']))
        self.assertEqual(task, result['task']())
