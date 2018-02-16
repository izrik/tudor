#!/usr/bin/env python

import unittest

from persistence.in_memory.models.tag import Tag


class TagReprTest(unittest.TestCase):
    def test_generates_repr_string(self):
        # given
        tag = Tag(value='value')
        tag.id = 123
        #when
        r = repr(tag)
        # then
        self.assertEqual('Tag(\'value\', id=123)', r)

    # TODO: test other values, other ids, None
