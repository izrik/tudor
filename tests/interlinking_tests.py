
import unittest

from models.interlinking import InterlinkedSet


class TestingCollection(InterlinkedSet):
    def add(self, item):
        self._add(item)

    def discard(self, item):
        self._discard(item)


class ItemSource(object):
    def __init__(self, count):
        self.count = count
        self.expanded = False

    def __iter__(self):
        self.expanded = True
        for item in xrange(self.count):
            yield item


class LazyLoadingTest(unittest.TestCase):
    def test_underlying_set_is_not_initialized(self):
        # given
        c = object()
        lazy = ItemSource(3)
        # precondition
        self.assertFalse(lazy.expanded)
        # when
        i = TestingCollection(c, lazy)
        # then
        self.assertIsNotNone(i._lazy)
        self.assertFalse(lazy.expanded)
        self.assertEqual(set(), i.set)

    def test_repr_does_not_populate(self):
        # given
        c = object()
        lazy = ItemSource(3)
        i = TestingCollection(c, lazy)
        # precondition
        self.assertFalse(lazy.expanded)
        # when
        result = repr(i)
        # then
        self.assertEqual('TestingCollection(<lazy>)', result)
        self.assertIsNotNone(i._lazy)
        self.assertFalse(lazy.expanded)
        self.assertEqual(set(), i.set)

    def test_str_does_not_populate(self):
        # given
        c = object()
        lazy = ItemSource(3)
        i = TestingCollection(c, lazy)
        # precondition
        self.assertFalse(lazy.expanded)
        # when
        result = str(i)
        # then
        self.assertEqual('set(<lazy>)', result)
        self.assertIsNotNone(i._lazy)
        self.assertFalse(lazy.expanded)
        self.assertEqual(set(), i.set)

    def test_len_populates(self):
        # given
        c = object()
        lazy = ItemSource(3)
        i = TestingCollection(c, lazy)
        # precondition
        self.assertFalse(lazy.expanded)
        # when
        result = len(i)
        # then
        self.assertEqual(3, result)
        self.assertIsNone(i._lazy)
        self.assertTrue(lazy.expanded)
        self.assertEqual({0, 1, 2}, i.set)

    def test_in_populates(self):
        # given
        c = object()
        lazy = ItemSource(3)
        i = TestingCollection(c, lazy)
        # precondition
        self.assertFalse(lazy.expanded)
        # when
        result = (0 in i)
        # then
        self.assertTrue(result)
        self.assertIsNone(i._lazy)
        self.assertTrue(lazy.expanded)
        self.assertEqual({0, 1, 2}, i.set)

    def test_iter_populates(self):
        # given
        c = object()
        lazy = ItemSource(3)
        i = TestingCollection(c, lazy)
        # precondition
        self.assertFalse(lazy.expanded)
        # when
        result = list(i)
        # then
        self.assertEqual([0, 1, 2], result)
        self.assertIsNone(i._lazy)
        self.assertTrue(lazy.expanded)
        self.assertEqual({0, 1, 2}, i.set)

    def test_append_populates(self):
        # given
        c = object()
        lazy = ItemSource(3)
        i = TestingCollection(c, lazy)
        # precondition
        self.assertFalse(lazy.expanded)
        # when
        i.append(3)
        # then
        self.assertIsNone(i._lazy)
        self.assertTrue(lazy.expanded)
        self.assertEqual({0, 1, 2, 3}, i.set)

    def test_add_populates(self):
        # given
        c = object()
        lazy = ItemSource(3)
        i = TestingCollection(c, lazy)
        # precondition
        self.assertFalse(lazy.expanded)
        # when
        i.add(3)
        # then
        self.assertIsNone(i._lazy)
        self.assertTrue(lazy.expanded)
        self.assertEqual({0, 1, 2, 3}, i.set)

    def test_discard_populates(self):
        # given
        c = object()
        lazy = ItemSource(3)
        i = TestingCollection(c, lazy)
        # precondition
        self.assertFalse(lazy.expanded)
        # when
        i.discard(2)
        # then
        self.assertIsNone(i._lazy)
        self.assertTrue(lazy.expanded)
        self.assertEqual({0, 1}, i.set)

    def test_non_lazy_collection_lazy_is_null(self):
        # given
        c = object()
        # when
        i = TestingCollection(c)
        # then
        self.assertIsNone(i._lazy)
        self.assertEqual(set(), i.set)
