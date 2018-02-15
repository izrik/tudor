#!/usr/bin/env python

import unittest

from models.tag import Tag
from models.user import User
from tests.logic_t.layer.LogicLayer.util import generate_ll


class LogicLayerTaskTagsTest(unittest.TestCase):

    def setUp(self):
        self.ll = generate_ll(db_uri='sqlite://')
        self.pl = self.ll.pl
        self.admin = User('name@example.org', None, True)
        self.pl.add(self.admin)
        self.user = User('name2@example.org', None, False)
        self.pl.add(self.user)

    def test_get_or_create_tag_nonexistent_creates_tag(self):
        # precondition
        self.assertEqual(0, self.pl.count_tags())

        # when
        tag = self.ll.get_or_create_tag('abc')

        # then
        self.assertEqual(1, self.pl.count_tags())
        self.assertIsNotNone(tag)
        self.assertIsInstance(tag, Tag)
        self.assertEqual('abc', tag.value)

    def test_get_or_create_tag_existent_gets_tag(self):
        # given
        tag1 = Tag('def')
        self.pl.add(tag1)
        self.pl.commit()

        # precondition
        self.assertEqual(1, self.pl.count_tags())

        # when
        tag2 = self.ll.get_or_create_tag('def')

        # then
        self.assertEqual(1, self.pl.count_tags())
        self.assertIsNotNone(tag2)
        self.assertIsInstance(tag2, Tag)
        self.assertEqual('def', tag2.value)
        self.assertIs(tag1, tag2)
