import unittest

import collections_util


class CollectionsUtilTest(unittest.TestCase):

    def test_add_to_list_adds(self):
        # given
        the_list = []
        # precondition
        self.assertEqual(0, len(the_list))
        # when
        collections_util.add(the_list, 'a')
        # then
        self.assertEqual(1, len(the_list))

    def test_add_to_set_adds(self):
        # given
        the_set = set()
        # precondition
        self.assertEqual(0, len(the_set))
        # when
        collections_util.add(the_set, 'a')
        # then
        self.assertEqual(1, len(the_set))

    def test_remove_from_list_removes(self):
        # given
        the_list = ['a']
        # precondition
        self.assertEqual(1, len(the_list))
        # when
        collections_util.remove(the_list, 'a')
        # then
        self.assertEqual(0, len(the_list))

    def test_remove_from_set_removes(self):
        # given
        the_set = {'a'}
        # precondition
        self.assertEqual(1, len(the_set))
        # when
        collections_util.remove(the_set, 'a')
        # then
        self.assertEqual(0, len(the_set))

    def test_remove_nonexistent_from_list_does_not_remove(self):
        # given
        the_list = ['a']
        # precondition
        self.assertEqual(1, len(the_list))
        # when
        collections_util.remove(the_list, 'b')
        # then
        self.assertEqual(1, len(the_list))

    def test_remove_nonexistent_from_set_does_not_remove(self):
        # given
        the_set = {'a'}
        # precondition
        self.assertEqual(1, len(the_set))
        # when
        collections_util.remove(the_set, 'b')
        # then
        self.assertEqual(1, len(the_set))

    def test_clear_list_removes_all(self):
        # given
        the_list = ['a', 'b']
        # precondition
        self.assertEqual(2, len(the_list))
        # when
        collections_util.clear(the_list)
        # then
        self.assertEqual(0, len(the_list))

    def test_clear_set_removes_all(self):
        # given
        the_set = {'a', 'b'}
        # precondition
        self.assertEqual(2, len(the_set))
        # when
        collections_util.clear(the_set)
        # then
        self.assertEqual(0, len(the_set))

    def test_extend_list_add_multiple(self):
        # given
        the_list = []
        # precondition
        self.assertEqual(0, len(the_list))
        # when
        collections_util.extend(the_list, ['a','b','c'])
        # then
        self.assertEqual(3, len(the_list))

    def test_extend_set_add_multiple(self):
        # given
        the_set = set()
        # precondition
        self.assertEqual(0, len(the_set))
        # when
        collections_util.extend(the_set, ['a', 'b', 'c'])
        # then
        self.assertEqual(3, len(the_set))

    def test_extend_list_adds_duplicates(self):
        # given
        the_list = ['a','b','c']
        # precondition
        self.assertEqual(3, len(the_list))
        # when
        collections_util.extend(the_list, ['b','c','d'])
        # then
        self.assertEqual(6, len(the_list))

    def test_extend_set_does_not_add_duplicates(self):
        # given
        the_set = {'a','b','c'}
        # precondition
        self.assertEqual(3, len(the_set))
        # when
        collections_util.extend(the_set, ['b', 'c', 'd'])
        # then
        self.assertEqual(4, len(the_set))

    def test_assign_list_replaces_all_and_may_reorder(self):
        # given
        the_list = ['a','b','c']
        # precondition
        self.assertEqual(3, len(the_list))
        # when
        collections_util.assign(the_list, ['d','e','f'])
        # then
        self.assertEqual({'d','e','f'}, set(the_list))

    def test_assign_set_replaces_all(self):
        # given
        the_set = {'a','b','c'}
        # precondition
        self.assertEqual(3, len(the_set))
        # when
        collections_util.assign(the_set, ['d','e','f'])
        # then
        self.assertEqual({'d','e','f'}, the_set)

    def test_assign_treats__none__like_empty_collection(self):
        # given
        the_set = {'a','b','c'}
        # precondition
        self.assertEqual(3, len(the_set))
        # when
        collections_util.assign(the_set, None)
        # then
        self.assertEqual(0, len(the_set))
