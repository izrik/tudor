#!/usr/bin/env python

import unittest

from models.user import User


class UserReprTest(unittest.TestCase):
    def test_generates_repr_string(self):
        # given
        user = User(email='name@example.com')
        user.id = 123
        #when
        r = repr(user)
        # then
        self.assertEqual('User(\'name@example.com\', id=123)', r)

    # TODO: test other emails, other ids, None
