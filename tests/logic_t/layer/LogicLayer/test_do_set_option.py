#!/usr/bin/env python

import unittest

from models.option import Option
from tests.logic_t.layer.LogicLayer.util import generate_ll


class SetOptionTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_option_key_none_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.ll.do_set_option,
            None, 'value')

    def test_option_not_found_creates_option(self):
        # precondition
        self.assertEqual(0, self.pl.count_options())
        self.assertIsNone(self.pl.get_option('key'))
        # when
        result = self.ll.do_set_option('key', 'value')
        self.pl.commit()
        # then
        self.assertEqual(1, self.pl.count_options())
        opt = self.pl.get_option('key')
        self.assertIsNotNone(opt)
        self.assertIs(opt, result)

    def test_edits_option(self):
        # given
        option = Option('a', 'b')
        self.pl.add(option)
        self.pl.commit()
        # precondition
        self.assertEqual('a', option.key)
        self.assertEqual('b', option.value)
        # when
        result = self.ll.do_set_option('a', 'c')
        self.pl.commit()
        # then
        self.assertIs(option, result)
        self.assertEqual('a', option.key)
        self.assertEqual('c', option.value)
