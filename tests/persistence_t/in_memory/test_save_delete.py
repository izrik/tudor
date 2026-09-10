import unittest

from models.attachment import Attachment
from models.comment import Comment
from models.option import Option
from models.tag import Tag
from models.task import Task
from models.user import User
from persistence.in_memory.layer import InMemoryPersistenceLayer
from persistence.sqlalchemy.layer import RecordNotFound


class InMemorySaveTest(unittest.TestCase):
    def setUp(self):
        self.pl = InMemoryPersistenceLayer()

    def test_save_no_args_is_noop(self):
        self.pl.save()  # should not raise

    def test_save_new_task_assigns_id(self):
        t = Task(summary='foo')
        self.assertIsNone(t.id)
        self.pl.save(t)
        self.assertIsNotNone(t.id)
        self.assertEqual(t.summary, 'foo')

    def test_save_new_tag_assigns_id(self):
        tag = Tag(value='red')
        self.pl.save(tag)
        self.assertIsNotNone(tag.id)

    def test_save_multiple_in_one_call(self):
        t = Task(summary='foo')
        tag = Tag(value='red')
        self.pl.save(t, tag)
        self.assertIsNotNone(t.id)
        self.assertIsNotNone(tag.id)

    def test_save_existing_task_updates(self):
        t = Task(summary='foo')
        self.pl.save(t)
        task_id = t.id
        t.summary = 'bar'
        self.pl.save(t)
        self.assertEqual(t.id, task_id)

    def test_save_with_unknown_id_raises(self):
        t = Task(summary='foo', id=999)
        with self.assertRaises(RecordNotFound):
            self.pl.save(t)

    def test_save_option_uses_key(self):
        o = Option(key='k', value='v')
        self.pl.save(o)
        self.assertIn('k', self.pl._options_by_key)


class InMemoryDeleteTest(unittest.TestCase):
    def setUp(self):
        self.pl = InMemoryPersistenceLayer()

    def test_delete_no_args_is_noop(self):
        self.pl.delete()

    def test_delete_domain_task(self):
        t = Task(summary='foo')
        self.pl.save(t)
        task_id = t.id
        self.pl.delete(t)
        self.assertNotIn(task_id, self.pl._tasks_by_id)

    def test_delete_unknown_raises(self):
        t = Task(summary='foo', id=999)
        with self.assertRaises(RecordNotFound):
            self.pl.delete(t)

    def test_delete_multiple(self):
        t = Task(summary='foo')
        tag = Tag(value='red')
        self.pl.save(t, tag)
        self.pl.delete(t, tag)
        self.assertEqual(len(self.pl._tasks), 0)
        self.assertEqual(len(self.pl._tags), 0)
