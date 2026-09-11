#!/usr/bin/env python

import unittest

from tests.util import generate_test_app


class TagTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_test_app().pl

    def test_constructor_default_id_is_none(self):
        # when
        tag = self.pl.DbTag('name', 'description')
        # then
        self.assertIsNone(tag.id)

    def test_constructor_sets_value(self):
        # when
        tag = self.pl.DbTag('name', 'description')
        # then
        self.assertEqual('name', tag.value)

    def test_constructor_sets_description(self):
        # when
        tag = self.pl.DbTag('name', 'description')
        # then
        self.assertEqual('description', tag.description)

    def test_to_dict_returns_correct_values(self):
        # when
        tag = self.pl.DbTag('name', '12345')
        # then
        self.assertEqual({'value': 'name',
                          'description': '12345',
                          'id': None, 'tasks': []}, tag.to_dict())
