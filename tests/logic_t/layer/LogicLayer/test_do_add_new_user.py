#!/usr/bin/env python

import unittest

from werkzeug.exceptions import Conflict

from tests.logic_t.layer.LogicLayer.util import generate_ll


class AddNewUserTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_email_already_exists_raises(self):
        # given
        user = self.pl.create_user('name@example.com')
        self.pl.add(user)
        self.pl.commit()
        # expect
        self.assertRaises(
            Conflict,
            self.ll.do_add_new_user,
            'name@example.com', False)
        # expect
        self.assertRaises(
            Conflict,
            self.ll.do_add_new_user,
            'name@example.com', True)

    def test_returns_new_user(self):
        # when
        result = self.ll.do_add_new_user('name@example.com')
        self.pl.commit()
        # then
        self.assertEqual('name@example.com', result.email)
        self.assertFalse(result.is_admin)

    def test_adds_user(self):
        # precondition
        self.assertEqual(0, self.pl.count_users())
        # when
        self.ll.do_add_new_user('name@example.com')
        self.pl.commit()
        # then
        self.assertEqual(1, self.pl.count_users())

    def test_is_admin_false_sets_is_admin_false(self):
        # when
        result = self.ll.do_add_new_user('name@example.com', False)
        self.pl.commit()
        # then
        self.assertEqual('name@example.com', result.email)
        self.assertFalse(result.is_admin)

    def test_is_admin_true_sets_is_admin_true(self):
        # when
        result = self.ll.do_add_new_user('name@example.com', True)
        self.pl.commit()
        # then
        self.assertEqual('name@example.com', result.email)
        self.assertTrue(result.is_admin)
