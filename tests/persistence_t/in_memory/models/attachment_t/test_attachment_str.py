#!/usr/bin/env python

import unittest

from persistence.in_memory.models.attachment import IMAttachment


class AttachmentStrTest(unittest.TestCase):
    def test_generates_str_string(self):
        # given
        att = IMAttachment(path='/path/to/file')
        att.id = 123
        #when
        r = str(att)
        # then
        expected = 'IMAttachment(\'/path/to/file\', attachment id=123, id=[{}])'
        expected = expected.format(id(att))
        self.assertEqual(expected, r)

    # TODO: test other paths, other ids, None
