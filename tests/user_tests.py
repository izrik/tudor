#!/usr/bin/env python

import unittest

from models.user import User


class UserTest(unittest.TestCase):
    def test_constructor_default_id_is_none(self):
        # when
        user = User('name@example.org', 'hashed_password')
        # then
        self.assertIsNone(user.id)

    def test_constructor_sets_email(self):
        # when
        user = User('name@example.org', 'hashed_password')
        # then
        self.assertEqual('name@example.org', user.email)

    def test_constructor_sets_hashed_password(self):
        # when
        user = User('name@example.org', 'hashed_password')
        # then
        self.assertEqual('hashed_password', user.hashed_password)

    def test_constructor_default_is_admin_is_false(self):
        # when
        user = User('name@example.org', 'hashed_password')
        # then
        self.assertFalse(user.is_admin)

    def test_constructor_sets_is_admin(self):
        # when
        user = User('name@example.org', 'hashed_password', False)
        # then
        self.assertFalse(user.is_admin)

        # when
        user = User('name@example.org', 'hashed_password', True)
        # then
        self.assertTrue(user.is_admin)

    def test_get_id_gets_email(self):
        # when
        user = User('name@example.org', 'hashed_password')
        # then
        self.assertEqual('name@example.org', user.get_id())

    def test_is_active_always_true(self):
        # when
        user = User('name@example.org', 'hashed_password')
        # then
        self.assertTrue(user.is_active())

    def test_is_anonymous_always_false(self):
        # when
        user = User('name@example.org', 'hashed_password')
        # then
        self.assertFalse(user.is_anonymous())

    def test_is_authenticated_always_true(self):
        # when
        user = User('name@example.org', 'hashed_password')
        # then
        self.assertTrue(user.is_authenticated())

    def test_to_dict_returns_correct_values(self):
        # when
        user = User('name@example.org', '12345')
        # then
        self.assertEqual({'email': 'name@example.org',
                          'hashed_password': '12345',
                          'is_admin': False, 'id': None, 'tasks': []},
                         user.to_dict())
