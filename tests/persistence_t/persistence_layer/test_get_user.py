import unittest

from persistence.in_memory.models.user import User
from tests.persistence_t.persistence_layer.util import PersistenceLayerTestBase


class GetUserTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_get_user_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_user, None)

    def test_get_user_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_user(1))

    def test_get_user_existing_yields_that_user(self):
        # given
        user = User('user')
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(user.id)
        # when
        result = self.pl.get_user(user.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(user, result)

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
        self.assertIs(dbuser, result)
