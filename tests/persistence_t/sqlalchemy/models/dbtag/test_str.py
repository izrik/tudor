#!/usr/bin/env python

import unittest

from tests.util import generate_test_app


class TagStrTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_test_app().pl

    def test_generates_str_string(self):
        # given
        tag = self.pl.DbTag(value='value')
        tag.id = 123
        #when
        r = str(tag)
        # then
        fmt = 'DbTag(\'value\', tag id=123, id=[{}])'
        expected = fmt.format(id(tag))
        self.assertEqual(expected, r)

    # TODO: test other values, other ids, None
