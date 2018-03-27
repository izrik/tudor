
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class BridgeTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_str_is_not_db_object(self):
        # expect
        self.assertFalse(self.pl._is_db_object('note'))

    def test_db_task_is_db_object(self):
        # given
        task = self.pl.DbTask('task')
        # expect
        self.assertTrue(self.pl._is_db_object(task))

    def test_db_tag_is_db_object(self):
        # given
        tag = self.pl.DbTag('tag')
        # expect
        self.assertTrue(self.pl._is_db_object(tag))

    def test_db_note_is_db_object(self):
        # given
        note = self.pl.DbNote('note')
        # expect
        self.assertTrue(self.pl._is_db_object(note))

    def test_db_attachment_is_db_object(self):
        # given
        attachment = self.pl.DbAttachment('attachment')
        # expect
        self.assertTrue(self.pl._is_db_object(attachment))

    def test_db_user_is_db_object(self):
        # given
        user = self.pl.DbUser('name@example.com')
        # expect
        self.assertTrue(self.pl._is_db_object(user))

    def test_db_option_is_db_object(self):
        # given
        option = self.pl.DbOption('key', 'value')
        # expect
        self.assertTrue(self.pl._is_db_object(option))
