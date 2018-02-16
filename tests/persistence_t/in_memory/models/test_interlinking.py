
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


class InterlinkedSetTest(unittest.TestCase):
    def setUp(self):
        self.c = object()
        self.s = TestingCollection(self.c)

    def test_init_sets_container(self):
        # expect
        self.assertIsNotNone(self.c)
        self.assertIsNotNone(self.s)
        self.assertIs(self.c, self.s.container)
        self.assertIs(self.c, self.s.c)

    def test_init_creates_backing_store(self):
        # expect
        self.assertIsNotNone(self.s.set)
        self.assertIsInstance(self.s.set, set)

    def test_not_in(self):
        # precondition
        self.assertTrue(1 not in self.s.set)
        # expect
        self.assertTrue(1 not in self.s)

    def test_in(self):
        # given
        self.s.set.add(1)
        # precondition
        self.assertTrue(1 in self.s.set)
        # expect
        self.assertTrue(1 in self.s)

    def test_len_zero(self):
        # precondition
        self.assertEqual(0, len(self.s.set))
        # expect
        self.assertEqual(0, len(self.s))

    def test_len_one(self):
        # given
        self.s.set.add(123)
        # precondition
        self.assertEqual(1, len(self.s.set))
        # expect
        self.assertEqual(1, len(self.s))

    def test_len_two(self):
        # given
        self.s.set.add(456)
        self.s.set.add(789)
        # precondition
        self.assertEqual(2, len(self.s.set))
        # expect
        self.assertEqual(2, len(self.s))

    def test_iter(self):
        # given
        self.s.set.add(456)
        self.s.set.add(789)
        # precondition
        self.assertEqual(2, len(self.s.set))
        # when
        result = set(iter(self.s))
        # then
        self.assertEqual({456, 789}, result)

    def test_str(self):
        # given
        self.s.set.add(456)
        self.s.set.add(789)
        # precondition
        self.assertEqual(2, len(self.s.set))
        # when
        result = str(self.s)
        # then
        self.assertEqual('set([456, 789])', result)

    def test_repr(self):
        # given
        self.s.set.add(456)
        self.s.set.add(789)
        # precondition
        self.assertEqual(2, len(self.s.set))
        # when
        result = repr(self.s)
        # then
        self.assertEqual('TestingCollection(set([456, 789]))', result)

    def test_add_adds_item(self):
        # precondition
        self.assertEqual(0, len(self.s))
        self.assertFalse(1 in self.s)
        # when
        self.s.add(1)
        # then
        self.assertEqual(1, len(self.s))
        self.assertTrue(1 in self.s)

    def test__add_adds_item(self):
        # precondition
        self.assertEqual(0, len(self.s))
        self.assertFalse(1 in self.s)
        # when
        self.s._add(1)
        # then
        self.assertEqual(1, len(self.s))
        self.assertTrue(1 in self.s)

    def test_append_adds_item(self):
        # precondition
        self.assertEqual(0, len(self.s))
        self.assertFalse(1 in self.s)
        # when
        self.s.append(1)
        # then
        self.assertEqual(1, len(self.s))
        self.assertTrue(1 in self.s)

    def test_discard_discards_item(self):
        # given
        self.s._add(1)
        # precondition
        self.assertEqual(1, len(self.s))
        self.assertTrue(1 in self.s)
        # when
        self.s.discard(1)
        # then
        self.assertEqual(0, len(self.s))
        self.assertFalse(1 in self.s)

    def test__discard_discards_item(self):
        # given
        self.s._add(1)
        # precondition
        self.assertEqual(1, len(self.s))
        self.assertTrue(1 in self.s)
        # when
        self.s._discard(1)
        # then
        self.assertEqual(0, len(self.s))
        self.assertFalse(1 in self.s)

    def test_container_none_raises(self):
        # expect
        self.assertRaises(ValueError, TestingCollection, None)
