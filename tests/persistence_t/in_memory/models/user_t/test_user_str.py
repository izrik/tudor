#!/usr/bin/env python

import unittest

from persistence.in_memory.models.user import IMUser


class UserStrTest(unittest.TestCase):
    def test_generates_str_string(self):
        # given
        user = IMUser(email='name@example.com')
        user.id = 123
        #when
        r = str(user)
        # then
        fmt = 'IMUser(\'name@example.com\', user id=123, id=[{}])'
        expected = fmt.format(id(user))
        self.assertEqual(expected, r)

    # TODO: test other emails, other ids, None
