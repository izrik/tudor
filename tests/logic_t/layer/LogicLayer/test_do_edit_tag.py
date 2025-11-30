#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound

from tests.logic_t.layer.LogicLayer.util import generate_ll


class EditTagTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_tag_id_none_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.ll.do_edit_tag,
            None, 'value', 'description')

    def test_tag_not_found_raises(self):
        # precondition
        self.assertEqual(0, self.pl.count_tags())
        self.assertIsNone(self.pl.get_tag(1))
        # expect
        self.assertRaises(
            NotFound,
            self.ll.do_edit_tag,
            1, 'value', 'description')

    def test_edits_tag(self):
        # given
        tag = self.pl.create_tag(value='a', description='b')
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertEqual('a', tag.value)
        self.assertEqual('b', tag.description)
        # when
        result = self.ll.do_edit_tag(tag.id, 'c', 'd')
        self.pl.commit()
        # then
        self.assertEqual(tag.id, result.id)
        self.assertEqual('c', tag.value)
        self.assertEqual('d', tag.description)
