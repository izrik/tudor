#!/usr/bin/env python

import unittest

from tests.logic_t.layer.LogicLayer.util import generate_ll


class GetTagsDataTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.b = self.pl.create_tag('b')
        self.pl.add(self.b)
        self.c = self.pl.create_tag('c')
        self.pl.add(self.c)
        self.a = self.pl.create_tag('a')
        self.pl.add(self.a)
        self.pl.commit()

    def test_defaults_sort_by_name_ascending(self):
        # when
        result = self.ll.get_tags_data()
        # then
        self.assertEqual('name', result['sort'])
        self.assertEqual('asc', result['order'])
        self.assertEqual(20, result['pager'].per_page)
        self.assertEqual([self.a, self.b, self.c], result['pager'].items)

    def test_sort_by_name_descending(self):
        # when
        result = self.ll.get_tags_data(sort='name', order='desc')
        # then
        self.assertEqual([self.c, self.b, self.a], result['pager'].items)

    def test_sort_by_id_ascending(self):
        # when
        result = self.ll.get_tags_data(sort='id', order='asc')
        # then
        self.assertEqual([self.b, self.c, self.a], result['pager'].items)

    def test_sort_by_id_descending(self):
        # when
        result = self.ll.get_tags_data(sort='id', order='desc')
        # then
        self.assertEqual([self.a, self.c, self.b], result['pager'].items)

    def test_paginates(self):
        # when
        result = self.ll.get_tags_data(page_num=2, tags_per_page=2)
        # then
        pager = result['pager']
        self.assertEqual(2, pager.page)
        self.assertEqual(2, pager.pages)
        self.assertEqual(3, pager.total)
        self.assertEqual([self.c], pager.items)

    def test_unknown_sort_raises(self):
        self.assertRaises(ValueError, self.ll.get_tags_data, sort='value')

    def test_unknown_order_raises(self):
        self.assertRaises(ValueError, self.ll.get_tags_data, order='up')
