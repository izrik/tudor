#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound

from models.tag import Tag
from tests.logic_layer_t.util import generate_ll


class GetTagTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.pl.create_all()

    def test_tag_id_none_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.ll.get_tag,
            None)

    def test_tag_not_found_raises(self):
        # precondition
        self.assertEqual(0, len(self.pl.get_tags()))
        self.assertIsNone(self.pl.get_tag(1))
        # expect
        self.assertRaises(
            NotFound,
            self.ll.get_tag,
            1)

    def test_edits_tag(self):
        # given
        tag = Tag(value='value', description='description')
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertEqual(1, len(self.pl.get_tags()))
        # when
        result = self.ll.get_tag(tag.id)
        # then
        self.assertIs(tag, result)
