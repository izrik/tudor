import unittest

from models.attachment import Attachment
from models.note import Note
from models.option import Option
from models.tag import Tag
from models.task import Task
from models.user import User
from tests.persistence_t.persistence_layer.util import PersistenceLayerTestBase


class CreateDomainFromDbTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_none_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_domain_object_from_db_object,
            None)

    def test_not_db_object_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_domain_object_from_db_object,
            1)
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_domain_object_from_db_object,
            Task('task'))

    def test_already_cached_raises(self):
        # given
        dbtask = self.pl.DbTask('task')
        self.pl.db.session.add(dbtask)
        self.pl.db.session.commit()
        task = self.pl.get_task(dbtask.id)
        # precondition
        self.assertIn(task, self.pl._db_by_domain)
        self.assertIn(dbtask, self.pl._domain_by_db)
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_domain_object_from_db_object,
            dbtask)

    def test_create_attachment_from_db(self):
        # given
        dbatt = self.pl.DbAttachment('att')
        self.pl.db.session.add(dbatt)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbatt.id)
        # when
        result = self.pl._create_domain_object_from_db_object(dbatt)
        # then
        self.assertIsNotNone(result)

        self.assertIsInstance(result, Attachment)
        self.assertEqual(dbatt.timestamp, result.timestamp)
        self.assertEqual(dbatt.path, result.path)
        self.assertEqual(dbatt.filename, result.filename)
        self.assertEqual(dbatt.description, result.description)

    def test_create_note_from_db(self):
        # given
        dbnote = self.pl.DbNote('note')
        self.pl.db.session.add(dbnote)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbnote.id)
        # when
        result = self.pl._create_domain_object_from_db_object(dbnote)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Note)
        self.assertEqual(dbnote.content, result.content)
        self.assertEqual(dbnote.timestamp, result.timestamp)

    def test_create_task_from_db(self):
        # given
        dbtask = self.pl.DbTask('task')
        self.pl.db.session.add(dbtask)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbtask.id)
        # when
        result = self.pl._create_domain_object_from_db_object(dbtask)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Task)
        self.assertEqual(dbtask.summary, result.summary)
        self.assertEqual(dbtask.description, result.description)

    def test_create_tag_from_db(self):
        # given
        dbtag = self.pl.DbTag('tag')
        self.pl.db.session.add(dbtag)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbtag.id)
        # when
        result = self.pl._create_domain_object_from_db_object(dbtag)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Tag)
        self.assertEqual(dbtag.value, result.value)
        self.assertEqual(dbtag.description, result.description)

    def test_create_user_from_db(self):
        # given
        dbuser = self.pl.DbUser('user')
        self.pl.db.session.add(dbuser)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbuser.id)
        # when
        result = self.pl._create_domain_object_from_db_object(dbuser)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, User)
        self.assertEqual(dbuser.email, result.email)
        self.assertEqual(dbuser.hashed_password, result.hashed_password)

    def test_create_option_from_db(self):
        # given
        dboption = self.pl.DbOption('key', 'value')
        self.pl.db.session.add(dboption)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dboption.id)
        # when
        result = self.pl._create_domain_object_from_db_object(dboption)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Option)
        self.assertEqual(dboption.key, result.key)
        self.assertEqual(dboption.value, result.value)
