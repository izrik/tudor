#!/usr/bin/env python

import unittest

from models.user import User, GuestUser


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

    def test_to_dict_all_fields_returns_correct_values(self):
        # when
        user = User('name@example.org', '12345')
        # then
        self.assertEqual({'email': 'name@example.org',
                          'hashed_password': '12345',
                          'is_admin': False, 'id': None, 'tasks': []},
                         user.to_dict({user.FIELD_ID, user.FIELD_EMAIL,
                                       user.FIELD_HASHED_PASSWORD,
                                       user.FIELD_IS_ADMIN, user.FIELD_TASKS}))

    def test_to_dict_field_id_returns_id(self):
        # when
        user = User('name@example.org', '12345')
        # then
        self.assertEqual({'id': None},
                         user.to_dict({user.FIELD_ID}))

    def test_to_dict_field_email_returns_email(self):
        # when
        user = User('name@example.org', '12345')
        # then
        self.assertEqual({'email': 'name@example.org'},
                         user.to_dict({user.FIELD_EMAIL}))

    def test_to_dict_field_hashed_password_returns_hashed_password(self):
        # when
        user = User('name@example.org', '12345')
        # then
        self.assertEqual({'hashed_password': '12345'},
                         user.to_dict({user.FIELD_HASHED_PASSWORD}))

    def test_to_dict_field_is_admin_returns_is_admin(self):
        # when
        user = User('name@example.org', '12345')
        # then
        self.assertEqual({'is_admin': False},
                         user.to_dict({user.FIELD_IS_ADMIN}))

    def test_to_dict_field_tasks_returns_tasks(self):
        # when
        user = User('name@example.org', '12345')
        # then
        self.assertEqual({'tasks': []},
                         user.to_dict({user.FIELD_TASKS}))


class GuestUserTest(unittest.TestCase):
    def test_create_is_not_none(self):
        # when
        guest = GuestUser()
        # then
        self.assertIsNotNone(guest)
        self.assertFalse(guest.authenticated)
        self.assertTrue(guest.is_active())
        self.assertEqual('Guest', guest.get_id())
        self.assertFalse(guest.is_authenticated())
        self.assertTrue(guest.is_anonymous())
        self.assertFalse(guest.is_admin)

    def test_setting_is_admin_does_not_set_is_admin(self):
        # given
        guest = GuestUser()
        # precondition
        self.assertFalse(guest.is_admin)
        # when
        guest.is_admin = True
        # then
        self.assertFalse(guest.is_admin)
