#!/usr/bin/env python

import unittest

from persistence.in_memory.models.tag import IMTag


class TagReprTest(unittest.TestCase):
    def test_generates_repr_string(self):
        # given
        tag = IMTag(value='value')
        tag.id = 123
        #when
        r = repr(tag)
        # then
        self.assertEqual('IMTag(\'value\', id=123)', r)

    # TODO: test other values, other ids, None
