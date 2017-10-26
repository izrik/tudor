import unittest

from models.attachment import Attachment
from models.note import Note
from models.option import Option
from models.tag import Tag
from models.task import Task
from models.user import User
from tests.persistence_layer.util import generate_pl


class BridgeTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_db_task_is_db_object(self):
        # given
        task = self.pl.DbTask('task')
        # expect
        self.assertTrue(self.pl._is_db_object(task))

    def test_db_task_is_not_domain_object(self):
        # given
        task = self.pl.DbTask('task')
        # expect
        self.assertFalse(self.pl._is_domain_object(task))

    def test_domain_task_is_not_db_object(self):
        # given
        task = Task('task')
        # expect
        self.assertFalse(self.pl._is_db_object(task))

    def test_domain_task_is_domain_object(self):
        # given
        task = Task('task')
        # expect
        self.assertTrue(self.pl._is_domain_object(task))

    def test_get_domain_object_db_task_returns_domain_task(self):
        # given
        task = self.pl.DbTask('task')
        # when
        result = self.pl._get_domain_object_from_db_object(task)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Task)

    def test_get_db_object_db_task_raises(self):
        # given
        task = self.pl.DbTask('task')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_db_object_from_domain_object,
                          task)

    def test_get_domain_object_domain_task_raises(self):
        # given
        task = Task('task')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_domain_object_from_db_object,
                          task)

    def test_get_db_object_domain_task_returns_db_task(self):
        # given
        task = Task('task')
        # when
        result = self.pl._get_db_object_from_domain_object(task)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbTask)

    def test_db_tag_is_db_object(self):
        # given
        tag = self.pl.DbTag('tag')
        # expect
        self.assertTrue(self.pl._is_db_object(tag))

    def test_db_tag_is_not_domain_object(self):
        # given
        tag = self.pl.DbTag('tag')
        # expect
        self.assertFalse(self.pl._is_domain_object(tag))

    def test_domain_tag_is_not_db_object(self):
        # given
        tag = Tag('tag')
        # expect
        self.assertFalse(self.pl._is_db_object(tag))

    def test_domain_tag_is_domain_object(self):
        # given
        tag = Tag('tag')
        # expect
        self.assertTrue(self.pl._is_domain_object(tag))

    def test_get_domain_object_db_tag_returns_domain_tag(self):
        # given
        tag = self.pl.DbTag('tag')
        # when
        result = self.pl._get_domain_object_from_db_object(tag)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Tag)

    def test_get_domain_object_domain_tag_raises(self):
        # given
        tag = Tag('tag')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_domain_object_from_db_object,
                          tag)

    def test_get_db_object_db_tag_raises(self):
        # given
        tag = self.pl.DbTag('tag')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_db_object_from_domain_object,
                          tag)

    def test_get_db_object_domain_tag_returns_dg_tag(self):
        # given
        tag = Tag('tag')
        # when
        result = self.pl._get_db_object_from_domain_object(tag)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbTag)

    def test_db_note_is_db_object(self):
        # given
        note = self.pl.DbNote('note')
        # expect
        self.assertTrue(self.pl._is_db_object(note))

    def test_domain_note_is_not_db_object(self):
        # given
        note = Note('note')
        # expect
        self.assertFalse(self.pl._is_db_object(note))

    def test_domain_note_is_domain_object(self):
        # given
        note = Note('note')
        # expect
        self.assertTrue(self.pl._is_domain_object(note))

    def test_db_note_is_not_domain_object(self):
        # given
        note = self.pl.DbNote('note')
        # expect
        self.assertFalse(self.pl._is_domain_object(note))

    def test_get_domain_object_db_note_returns_domain_object(self):
        # given
        note = self.pl.DbNote('note')
        # when
        result = self.pl._get_domain_object_from_db_object(note)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Note)

    def test_get_db_object_db_note_raises(self):
        # given
        note = self.pl.DbNote('note')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_db_object_from_domain_object,
                          note)

    def test_get_domain_object_domain_note_raises(self):
        # given
        note = Note('note')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_domain_object_from_db_object,
                          note)

    def test_get_db_object_domain_note_returns_db_object(self):
        # given
        note = Note('note')
        # when
        result = self.pl._get_db_object_from_domain_object(note)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbNote)

    def test_db_attachment_is_db_object(self):
        # given
        attachment = self.pl.DbAttachment('attachment')
        # expect
        self.assertTrue(self.pl._is_db_object(attachment))

    def test_domain_attachment_is_not_db_object(self):
        # given
        attachment = Attachment('attachment')
        # expect
        self.assertFalse(self.pl._is_db_object(attachment))

    def test_db_attachment_is_not_domain_object(self):
        # given
        attachment = self.pl.DbAttachment('attachment')
        # expect
        self.assertFalse(self.pl._is_domain_object(attachment))

    def test_domain_attachment_is_domain_object(self):
        # given
        attachment = Attachment('attachment')
        # expect
        self.assertTrue(self.pl._is_domain_object(attachment))

    def test_get_domain_object_domain_attachment_raises(self):
        # given
        attachment = Attachment('attachment')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_domain_object_from_db_object,
                          attachment)

    def test_get_domain_object_db_attachment_returns_domain(self):
        # given
        attachment = self.pl.DbAttachment('attachment')
        # when
        result = self.pl._get_domain_object_from_db_object(attachment)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Attachment)

    def test_get_db_object_db_attachment_raises(self):
        # given
        attachment = self.pl.DbAttachment('attachment')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_db_object_from_domain_object,
                          attachment)

    def test_get_db_object_domain_attachment_returns_db(self):
        # given
        attachment = Attachment('attachment')
        # when
        result = self.pl._get_db_object_from_domain_object(attachment)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbAttachment)

    def test_db_user_is_db_object(self):
        # given
        user = self.pl.DbUser('name@example.com')
        # expect
        self.assertTrue(self.pl._is_db_object(user))

    def test_db_user_is_not_domain_object(self):
        # given
        user = self.pl.DbUser('name@example.com')
        # expect
        self.assertFalse(self.pl._is_domain_object(user))

    def test_domain_user_is_not_db_object(self):
        # given
        user = User('name@example.com')
        # expect
        self.assertFalse(self.pl._is_db_object(user))

    def test_domain_user_is_domain_object(self):
        # given
        user = User('name@example.com')
        # expect
        self.assertTrue(self.pl._is_domain_object(user))

    def test_get_domain_object_db_user_returns_domain_user(self):
        # given
        user = self.pl.DbUser('name@example.com')
        # when
        result = self.pl._get_domain_object_from_db_object(user)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, User)

    def test_get_domain_object_domain_user_raises(self):
        # given
        user = User('name@example.com')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_domain_object_from_db_object,
                          user)

    def test_get_db_object_db_user_raises(self):
        # given
        user = self.pl.DbUser('name@example.com')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_db_object_from_domain_object,
                          user)

    def test_get_db_object_domain_user_returns_db_user(self):
        # given
        user = User('name@example.com')
        # when
        result = self.pl._get_db_object_from_domain_object(user)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbUser)

    def test_db_option_is_db_object(self):
        # given
        option = self.pl.DbOption('key', 'value')
        # expect
        self.assertTrue(self.pl._is_db_object(option))

    def test_domain_option_is_not_db_object(self):
        # given
        option = Option('key', 'value')
        # expect
        self.assertFalse(self.pl._is_db_object(option))

    def test_db_option_is_not_domain_object(self):
        # given
        option = self.pl.DbOption('key', 'value')
        # expect
        self.assertFalse(self.pl._is_domain_object(option))

    def test_domain_option_is_domain_object(self):
        # given
        option = Option('key', 'value')
        # expect
        self.assertTrue(self.pl._is_domain_object(option))

    def test_get_domain_object_domain_option_raises(self):
        # given
        option = Option('key', 'value')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_domain_object_from_db_object,
                          option)

    def test_get_domain_object_db_option_returns_domain_object(self):
        # given
        option = self.pl.DbOption('key', 'value')
        # when
        result = self.pl._get_domain_object_from_db_object(option)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Option)

    def test_get_db_object_domain_option_returns_db_object(self):
        # given
        option = Option('key', 'value')
        # when
        result = self.pl._get_db_object_from_domain_object(option)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbOption)

    def test_get_db_object_db_option_raises(self):
        # given
        option = self.pl.DbOption('key', 'value')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_db_object_from_domain_object,
                          option)
