import unittest

from persistence_layer import as_iterable


class AsIterableTest(unittest.TestCase):
    def test_iterable_returns_same(self):
        # expect
        self.assertEquals([1, 2, 3], as_iterable([1, 2, 3]))

    def test_non_iterable_returns_tuple(self):
        # expect
        self.assertEqual((4,), as_iterable(4))
