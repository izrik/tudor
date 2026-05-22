import unittest
from types import SimpleNamespace

from models.task import Task
from models.tag import Tag
from models.comment import Comment
from models.attachment import Attachment
from models.user import User
from models.option import Option
from persistence.sqlalchemy.conversion import (
    to_task, apply_task_to_db,
    to_tag, apply_tag_to_db,
    to_comment, apply_comment_to_db,
    to_attachment, apply_attachment_to_db,
    to_user, apply_user_to_db,
    to_option, apply_option_to_db)


def _fake_db_task(**kw):
    defaults = dict(id=1, summary='foo', description='', is_done=False,
                    is_deleted=False, deadline=None,
                    expected_duration_minutes=None, expected_cost=None,
                    order_num=0, parent_id=None, is_public=False,
                    date_created=None, date_last_updated=None)
    defaults.update(kw)
    return SimpleNamespace(**defaults)


class SqlAlchemyConversionTest(unittest.TestCase):
    def test_to_task_none(self):
        self.assertIsNone(to_task(None))

    def test_to_task_basic(self):
        db = _fake_db_task(id=5, summary='s', parent_id=3, order_num=7)
        t = to_task(db)
        self.assertIsInstance(t, Task)
        self.assertEqual(t.id, 5)
        self.assertEqual(t.summary, 's')
        self.assertEqual(t.parent_id, 3)
        self.assertEqual(t.order_num, 7)

    def test_apply_task_to_db(self):
        db = _fake_db_task()
        t = Task(id=2, summary='new', description='d', parent_id=4)
        apply_task_to_db(t, db)
        self.assertEqual(db.id, 2)
        self.assertEqual(db.summary, 'new')
        self.assertEqual(db.description, 'd')
        self.assertEqual(db.parent_id, 4)

    def test_to_tag_none(self):
        self.assertIsNone(to_tag(None))

    def test_to_tag_basic(self):
        db = SimpleNamespace(id=1, value='x', description='d')
        tag = to_tag(db)
        self.assertIsInstance(tag, Tag)
        self.assertEqual(tag.id, 1)
        self.assertEqual(tag.value, 'x')
        self.assertEqual(tag.description, 'd')

    def test_apply_tag_to_db(self):
        db = SimpleNamespace(id=None, value=None, description=None)
        apply_tag_to_db(Tag(id=2, value='v', description='d'), db)
        self.assertEqual(db.value, 'v')

    def test_to_comment(self):
        db = SimpleNamespace(id=1, content='c', timestamp=None,
                             date_last_updated=None, task_id=7)
        c = to_comment(db)
        self.assertIsInstance(c, Comment)
        self.assertEqual(c.task_id, 7)

    def test_apply_comment_to_db(self):
        db = SimpleNamespace(id=None, content=None, timestamp=None,
                             date_last_updated=None, task_id=None)
        apply_comment_to_db(Comment(content='c', task_id=7), db)
        self.assertEqual(db.task_id, 7)
        self.assertEqual(db.content, 'c')

    def test_to_attachment(self):
        db = SimpleNamespace(id=1, path='/p', description='d', timestamp=None,
                             filename='f', task_id=7)
        a = to_attachment(db)
        self.assertIsInstance(a, Attachment)
        self.assertEqual(a.task_id, 7)
        self.assertEqual(a.description, 'd')

    def test_to_attachment_none_description(self):
        db = SimpleNamespace(id=1, path='/p', description=None, timestamp=None,
                             filename=None, task_id=None)
        a = to_attachment(db)
        self.assertEqual(a.description, '')

    def test_to_user(self):
        db = SimpleNamespace(id=1, email='a@b', hashed_password='h',
                             is_admin=True)
        u = to_user(db)
        self.assertIsInstance(u, User)
        self.assertEqual(u.email, 'a@b')
        self.assertTrue(u.is_admin)

    def test_to_option(self):
        db = SimpleNamespace(key='k', value='v')
        o = to_option(db)
        self.assertIsInstance(o, Option)
        self.assertEqual(o.key, 'k')
        self.assertEqual(o.value, 'v')
