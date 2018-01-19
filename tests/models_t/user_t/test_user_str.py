#!/usr/bin/env python

import unittest

from models.user import User


class UserStrTest(unittest.TestCase):
    def test_generates_str_string(self):
        # given
        user = User(email='name@example.com')
        user.id = 123
        #when
        r = str(user)
        # then
        fmt = 'User(\'name@example.com\', user id=123, id=[{}])'
        expected = fmt.format(id(user))
        self.assertEqual(expected, r)

    # TODO: test other emails, other ids, None
