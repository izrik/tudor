#!/usr/bin/env python

import unittest

from tests.util import generate_test_app


class AttachmentStrTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_test_app().pl

    def test_generates_str_string(self):
        # given
        att = self.pl.DbAttachment(path='/path/to/file')
        att.id = 123
        #when
        r = str(att)
        # then
        expected = 'DbAttachment(\'/path/to/file\', attachment id=123, id=[{}])'
        expected = expected.format(id(att))
        self.assertEqual(expected, r)

    # TODO: test other paths, other ids, None
