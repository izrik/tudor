import unittest

from tests.persistence_layer.util import generate_pl


class DbOptionFromDictTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_empty_yields_empty_dboption(self):
        # when
        result = self.pl.DbOption.from_dict({})
        # then
        self.assertIsInstance(result, self.pl.DbOption)
        self.assertIsNone(result.key)
        self.assertIsNone(result.value)

    def test_key_none_is_ignored(self):
        # when
        result = self.pl.DbOption.from_dict({'key': None})
        # then
        self.assertIsInstance(result, self.pl.DbOption)
        self.assertIsNone(result.key)

    def test_valid_key_gets_set(self):
        # when
        result = self.pl.DbOption.from_dict({'key': 123})
        # then
        self.assertIsInstance(result, self.pl.DbOption)
        self.assertEqual(123, result.key)

    def test_value_none_is_ignored(self):
        # when
        result = self.pl.DbOption.from_dict({'value': None})
        # then
        self.assertIsInstance(result, self.pl.DbOption)
        self.assertIsNone(result.value)

    def test_valid_value_gets_set(self):
        # when
        result = self.pl.DbOption.from_dict({'value': 'something'})
        # then
        self.assertIsInstance(result, self.pl.DbOption)
        self.assertEqual('something', result.value)

    def test_none_lazy_does_not_raise(self):
        # when
        result = self.pl.DbOption.from_dict({}, lazy=None)
        # then
        self.assertIsInstance(result, self.pl.DbOption)
        self.assertIsNone(result.key)
        self.assertIsNone(result.value)

    def test_empty_lazy_does_not_raise(self):
        # when
        result = self.pl.DbOption.from_dict({}, lazy={})
        # then
        self.assertIsInstance(result, self.pl.DbOption)
        self.assertIsNone(result.key)
        self.assertIsNone(result.value)

    def test_non_none_lazy_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl.DbOption.from_dict,
            {},
            lazy={'tasks': None})
