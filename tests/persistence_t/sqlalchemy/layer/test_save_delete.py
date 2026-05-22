from models.task import Task
from models.tag import Tag
from models.comment import Comment
from models.attachment import Attachment
from models.user import User
from models.option import Option
from persistence.sqlalchemy.layer import RecordNotFound
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class SaveTest(PersistenceLayerTestBase):
    def test_save_no_args_is_noop(self):
        self.pl.save()

    def test_save_new_task_assigns_id(self):
        t = Task(summary='foo')
        self.assertIsNone(t.id)
        self.pl.save(t)
        self.assertIsNotNone(t.id)

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
        # confirm it persisted
        db_task = self.pl._get_db_task(task_id)
        self.assertEqual(db_task.summary, 'bar')

    def test_save_with_unknown_id_raises(self):
        t = Task(summary='foo', id=999)
        with self.assertRaises(RecordNotFound):
            self.pl.save(t)

    def test_save_option_uses_key(self):
        o = Option(key='k', value='v')
        self.pl.save(o)
        db_option = self.pl._get_db_option('k')
        self.assertEqual(db_option.value, 'v')

    def test_save_option_update_existing(self):
        self.pl.save(Option(key='k', value='v1'))
        self.pl.save(Option(key='k', value='v2'))
        self.assertEqual(self.pl._get_db_option('k').value, 'v2')


class DeleteTest(PersistenceLayerTestBase):
    def test_delete_no_args_is_noop(self):
        self.pl.delete()

    def test_delete_domain_task(self):
        t = Task(summary='foo')
        self.pl.save(t)
        task_id = t.id
        self.pl.delete(t)
        self.assertIsNone(self.pl._get_db_task(task_id))

    def test_delete_unknown_raises(self):
        t = Task(summary='foo', id=999)
        with self.assertRaises(RecordNotFound):
            self.pl.delete(t)
