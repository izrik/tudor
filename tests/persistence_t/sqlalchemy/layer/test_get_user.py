
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class GetUserTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()

    def test_get_user_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_user, None)

    def test_get_user_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_user(1))

    def test_get_user_existing_yields_that_user(self):
        # given
        user = self.pl.create_user('user')
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(user.id)
        # when
        result = self.pl.get_user(user.id)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(user.id, result.id)

    def test_get_db_user_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl._get_db_user, None)

    def test_get_db_user_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl._get_db_user(1))

    def test_get_db_user_existing_yields_that_dbuser(self):
        # given
        dbuser = self.pl.DbUser('user')
        self.pl.db.session.add(dbuser)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbuser.id)
        # when
        result = self.pl._get_db_user(dbuser.id)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(dbuser.id, result.id)
