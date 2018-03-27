import unittest

from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class DbUserConstructorTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()

    def test_none_lazy_is_allowed(self):
        # when
        user = self.pl.DbUser('user', lazy={})
        # then
        self.assertIsInstance(user, self.pl.DbUser)

    def test_empty_lazy_is_allowed(self):
        # when
        user = self.pl.DbUser('user', lazy={})
        # then
        self.assertIsInstance(user, self.pl.DbUser)

    def test_non_empty_lazy_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.DbUser, 'user', lazy={'id': 1})
