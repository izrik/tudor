#!/usr/bin/env python

import unittest

from logic_layer import LogicLayer


class MockPersistenceLayer(object):
    db = None


class AllowedFileTest(unittest.TestCase):
    def setUp(self):
        self.ll = LogicLayer('/tmp', ['txt', 'jpg', 'png', 'gif'],
                             MockPersistenceLayer())

    def test_no_dot_returns_false(self):
        # expect
        self.assertFalse(self.ll.allowed_file('filename'))

    def test_two_dots_gets_the_right_extension(self):
        # expect
        self.assertTrue(self.ll.allowed_file('filename.txt.png'))

    def test_extension_in_list_returns_true(self):
        # expect
        self.assertTrue(self.ll.allowed_file('filename.txt'))
        self.assertTrue(self.ll.allowed_file('filename.jpg'))
        self.assertTrue(self.ll.allowed_file('filename.png'))
        self.assertTrue(self.ll.allowed_file('filename.gif'))

    def test_Extension_not_in_list_returns_false(self):
        # expect
        self.assertFalse(self.ll.allowed_file('filename.pdf'))
        self.assertFalse(self.ll.allowed_file('filename.zip'))
        self.assertFalse(self.ll.allowed_file('filename.tar'))
        self.assertFalse(self.ll.allowed_file('filename.tgz'))
