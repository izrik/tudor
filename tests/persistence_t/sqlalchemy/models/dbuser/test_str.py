#!/usr/bin/env python

import unittest

from tests.util import generate_test_app


class UserStrTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_test_app().pl

    def test_generates_str_string(self):
        # given
        user = self.pl.DbUser(email='name@example.com')
        user.id = 123
        #when
        r = str(user)
        # then
        fmt = 'DbUser(\'name@example.com\', user id=123, id=[{}])'
        expected = fmt.format(id(user))
        self.assertEqual(expected, r)

    # TODO: test other emails, other ids, None
