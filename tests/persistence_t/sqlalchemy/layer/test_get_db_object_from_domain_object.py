from persistence.in_memory.models.attachment import Attachment
from persistence.in_memory.models.note import Note
from persistence.in_memory.models.option import Option
from persistence.in_memory.models.user import User
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class GetDbFromDomainTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_domobj_is_none_raises(self):
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object,
            None)

    def test_cache_domobj_is_none_raises(self):
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object_in_cache,
            None)

    def test_by_id_domobj_is_none_raises(self):
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object_by_id,
            None)

    def test_not_domobj_raises(self):
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object,
            1)
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object,
            self.pl.DbTask('task'))

    def test_cache_not_domobj_raises(self):
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object_in_cache,
            1)
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object_in_cache,
            self.pl.DbTask('task'))

    def test_by_id_not_domobj_raises(self):
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object_by_id,
            1)
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object_by_id,
            self.pl.DbTask('task'))

    def test_id_is_none_returns_none(self):
        # given
        task = self.pl.create_task('task')
        # precondition
        self.assertIsNone(task.id)
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(task)
        # then
        self.assertIsNone(result)

    def test_get_attachment_from_domain(self):
        # given
        att = Attachment('att')
        self.pl.add(att)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(att.id)
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(att)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbAttachment)
        self.assertEqual(att.timestamp, result.timestamp)
        self.assertEqual(att.path, result.path)
        self.assertEqual(att.filename, result.filename)
        self.assertEqual(att.description, result.description)

    def test_get_note_from_domain(self):
        # given
        note = Note('note')
        self.pl.add(note)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(note.id)
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(note)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbNote)
        self.assertEqual(note.content, result.content)
        self.assertEqual(note.timestamp, result.timestamp)

    def test_get_task_from_domain(self):
        # given
        task = self.pl.create_task('task')
        self.pl.add(task)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(task.id)
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(task)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual(task.summary, result.summary)
        self.assertEqual(task.description, result.description)

    def test_get_tag_from_domain(self):
        # given
        tag = self.pl.create_tag('tag')
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(tag.id)
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(tag)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbTag)
        self.assertEqual(tag.value, result.value)
        self.assertEqual(tag.description, result.description)

    def test_get_user_from_domain(self):
        # given
        user = User('user')
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(user.id)
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(user)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbUser)
        self.assertEqual(user.email, result.email)
        self.assertEqual(user.hashed_password, result.hashed_password)

    def test_get_option_from_domain(self):
        # given
        option = Option('key', 'value')
        self.pl.add(option)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(option.id)
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(option)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbOption)
        self.assertEqual(option.key, result.key)
        self.assertEqual(option.value, result.value)
