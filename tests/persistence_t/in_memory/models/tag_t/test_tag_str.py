#!/usr/bin/env python

import unittest

from persistence.in_memory.models.tag import IMTag


class TagStrTest(unittest.TestCase):
    def test_generates_str_string(self):
        # given
        tag = Tag(value='value')
        tag.id = 123
        #when
        r = str(tag)
        # then
        fmt = 'Tag(\'value\', tag id=123, id=[{}])'
        expected = fmt.format(id(tag))
        self.assertEqual(expected, r)

    # TODO: test other values, other ids, None
