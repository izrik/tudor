#!/usr/bin/env python

import unittest

from models.attachment import Attachment


class AttachmentStrTest(unittest.TestCase):
    def test_generates_str_string(self):
        # given
        att = Attachment(path='/path/to/file')
        att.id = 123
        #when
        r = str(att)
        # then
        expected = 'Attachment(\'/path/to/file\', attachment id=123, id=[{}])'
        expected = expected.format(id(att))
        self.assertEqual(expected, r)

    # TODO: test other paths, other ids, None
