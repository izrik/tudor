
import unittest

from models.option import Option


class OptionFromDictTest(unittest.TestCase):
    def test_empty_yields_empty_dboption(self):
        # when
        result = Option.from_dict({})
        # then
        self.assertIsInstance(result, Option)
        self.assertIsNone(result.key)
        self.assertIsNone(result.value)

    def test_id_none_is_ignored(self):
        # when
        result = Option.from_dict({'key': None})
        # then
        self.assertIsInstance(result, Option)
        self.assertIsNone(result.key)

    def test_valid_id_gets_set(self):
        # when
        result = Option.from_dict({'key': 123})
        # then
        self.assertIsInstance(result, Option)
        self.assertEqual(123, result.key)

    def test_value_none_is_ignored(self):
        # when
        result = Option.from_dict({'value': None})
        # then
        self.assertIsInstance(result, Option)
        self.assertIsNone(result.value)

    def test_valid_value_gets_set(self):
        # when
        result = Option.from_dict({'value': 'something'})
        # then
        self.assertIsInstance(result, Option)
        self.assertEqual('something', result.value)
