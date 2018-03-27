#!/usr/bin/env python

import unittest

from tests.logic_t.layer.LogicLayer.util import generate_ll


class GetTagsTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_no_tags_returns_empty_list(self):
        # precondition
        self.assertEqual(0, self.pl.count_tags())
        # when
        result = self.ll.get_tags()
        # then
        self.assertEqual([], result)

    def test_gets_single_tag_in_list(self):
        # given
        tag = self.pl.create_tag('tag')
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertEqual(1, self.pl.count_tags())
        # when
        result = self.ll.get_tags()
        # then
        self.assertEqual([tag], result)

    def test_gets_two_tags_in_list(self):
        # given
        tag1 = self.pl.create_tag('tag1')
        self.pl.add(tag1)
        tag2 = self.pl.create_tag('tag2')
        self.pl.add(tag2)
        self.pl.commit()
        # precondition
        self.assertEqual(2, self.pl.count_tags())
        # when
        result = self.ll.get_tags()
        # then
        self.assertIsInstance(result, list)
        self.assertEqual({tag1, tag2}, set(result))
