#!/usr/bin/env python

import unittest

from werkzeug.exceptions import Forbidden, NotFound

from tests.logic_t.layer.LogicLayer.util import generate_ll


class GetUserDataTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_gets_user_data(self):
        # given a user
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        # and an admin user to attempt the retrieval
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # when
        result = self.ll.do_get_user_data(user.id, admin)
        # then returns the user
        self.assertEqual(user.id, result.id)

    def test_user_not_found_raises(self):
        # given only an admin user to attempt the retrieval
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition: no user exists with that id
        self.assertIsNone(self.pl.get_user(admin.id + 1))
        # expect
        self.assertRaises(
            NotFound,
            self.ll.do_get_user_data,
            admin.id + 1, admin)

    def test_user_can_get_self(self):
        # given a user
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        self.pl.commit()
        # when
        result = self.ll.do_get_user_data(user.id, user)
        # then returns the user
        self.assertEqual(user.id, result.id)

    def test_current_user_not_self_and_not_admin_raises(self):
        # given a user to get
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        # and a non-admin user to attempt the retrieval
        non_admin = self.pl.create_user('nonadmin@example.com')
        self.pl.add(non_admin)
        self.pl.commit()
        # precondition
        self.assertIsNot(user, non_admin)
        self.assertFalse(non_admin.is_admin)
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.do_get_user_data,
            user.id, non_admin)
