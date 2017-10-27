import unittest

from tests.persistence_layer_t.util import generate_pl, \
    PersistenceLayerTestBase


class DbOptionConstructorTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = generate_pl()

    def test_none_lazy_is_allowed(self):
        # when
        option = self.pl.DbOption('key', 'value', lazy={})
        # then
        self.assertIsInstance(option, self.pl.DbOption)

    def test_empty_lazy_is_allowed(self):
        # when
        option = self.pl.DbOption('key', 'value', lazy={})
        # then
        self.assertIsInstance(option, self.pl.DbOption)

    def test_non_empty_lazy_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl.DbOption,
            'key', 'value',
            lazy={'id': 1})
