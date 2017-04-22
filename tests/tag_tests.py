#!/usr/bin/env python

import unittest

from tudor import generate_app


class TagTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.Tag = self.app.Tag

    def test_constructor_default_id_is_none(self):
        # when
        tag = self.Tag('name', 'description')
        # then
        self.assertIsNone(tag.id)

    def test_constructor_sets_value(self):
        # when
        tag = self.Tag('name', 'description')
        # then
        self.assertEqual('name', tag.value)

    def test_constructor_sets_description(self):
        # when
        tag = self.Tag('name', 'description')
        # then
        self.assertEqual('description', tag.description)

    def test_to_dict_returns_correct_values(self):
        # when
        tag = self.Tag('name', '12345')
        # then
        self.assertEqual({'value': 'name',
                          'description': '12345',
                          'id': None}, tag.to_dict())
