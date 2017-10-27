import unittest

from tests.persistence_layer_t.util import generate_pl, \
    PersistenceLayerTestBase


class DbTagConstructorTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = generate_pl()

    def test_none_lazy_is_allowed(self):
        # when
        tag = self.pl.DbTag('tag', lazy={})
        # then
        self.assertIsInstance(tag, self.pl.DbTag)

    def test_empty_lazy_is_allowed(self):
        # when
        tag = self.pl.DbTag('tag', lazy={})
        # then
        self.assertIsInstance(tag, self.pl.DbTag)

    def test_non_empty_lazy_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.DbTag, 'tag', lazy={'id': 1})
