#!/usr/bin/env python

import unittest

from models.attachment import Attachment


class AttachmentReprTest(unittest.TestCase):
    def test_generates_repr_string(self):
        # given
        att = Attachment(path='/path/to/file')
        att.id = 123
        #when
        r = repr(att)
        # then
        self.assertEqual('Attachment(\'/path/to/file\', id=123)', r)

    # TODO: test other paths, other ids, None
