import unittest

from models.option import Option


class OptionTest(unittest.TestCase):
    def test_construction(self):
        o = Option(key='k', value='v')
        self.assertEqual(o.key, 'k')
        self.assertEqual(o.value, 'v')
        self.assertEqual(o.id, 'k')

    def test_round_trip(self):
        o = Option(key='k', value='v')
        o2 = Option.from_dict(o.to_dict())
        self.assertEqual(o2.key, 'k')
        self.assertEqual(o2.value, 'v')
