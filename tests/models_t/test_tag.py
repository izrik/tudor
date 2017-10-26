#!/usr/bin/env python

import unittest

from models.tag import Tag


class TagTest(unittest.TestCase):
    def test_constructor_default_id_is_none(self):
        # when
        tag = Tag('name', 'description')
        # then
        self.assertIsNone(tag.id)

    def test_constructor_sets_value(self):
        # when
        tag = Tag('name', 'description')
        # then
        self.assertEqual('name', tag.value)

    def test_constructor_sets_description(self):
        # when
        tag = Tag('name', 'description')
        # then
        self.assertEqual('description', tag.description)

    def test_to_dict_returns_correct_values(self):
        # when
        tag = Tag('name', '12345')
        # then
        self.assertEqual({'value': 'name',
                          'description': '12345',
                          'id': None, 'tasks': []}, tag.to_dict())
