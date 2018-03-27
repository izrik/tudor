#!/usr/bin/env python

import unittest

from tests.logic_t.layer.LogicLayer.util import generate_ll


class DeleteOptionTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_no_option_found_returns_none(self):
        # precondition
        self.assertEqual(0, self.pl.count_options())
        # when
        result = self.ll.do_delete_option('asdf')
        # then
        self.assertIsNone(result)
        self.assertEqual(0, self.pl.count_options())

    def test_option_found_gets_deleted(self):
        # given
        opt = self.pl.create_option('key', 'value')
        self.pl.add(opt)
        self.pl.commit()
        # precondition
        self.assertEqual(1, self.pl.count_options())
        self.assertIs(opt, self.pl.get_option('key'))
        # when
        result = self.ll.do_delete_option('key')
        self.pl.commit()
        # then
        self.assertIs(opt, result)
        self.assertEqual(0, self.pl.count_options())
