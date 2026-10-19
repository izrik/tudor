#!/usr/bin/env python

import unittest

from logic.layer import LogicLayer, MAX_FILENAME_LENGTH


class ShortenFilenameTest(unittest.TestCase):
    def test_short_name_is_unchanged(self):
        # expect
        self.assertEqual('filename.txt',
                         LogicLayer._shorten_filename('filename.txt'))

    def test_name_of_exactly_the_maximum_length_is_unchanged(self):
        # given
        name = 'a' * (MAX_FILENAME_LENGTH - 4) + '.txt'
        # precondition
        self.assertEqual(MAX_FILENAME_LENGTH, len(name))
        # expect
        self.assertEqual(name, LogicLayer._shorten_filename(name))

    def test_long_name_is_trimmed_and_keeps_its_extension(self):
        # when
        result = LogicLayer._shorten_filename('a' * 300 + '.txt')
        # then
        self.assertEqual('a' * (MAX_FILENAME_LENGTH - 4) + '.txt', result)
        self.assertEqual(MAX_FILENAME_LENGTH, len(result))

    def test_long_name_without_an_extension_is_trimmed(self):
        # when
        result = LogicLayer._shorten_filename('a' * 300)
        # then
        self.assertEqual('a' * MAX_FILENAME_LENGTH, result)

    def test_extension_longer_than_the_maximum_is_trimmed_by_itself(self):
        # when
        result = LogicLayer._shorten_filename('a.' + 'b' * 300)
        # then
        self.assertEqual('.' + 'b' * (MAX_FILENAME_LENGTH - 1), result)

    def test_the_maximum_length_can_be_overridden(self):
        # expect
        self.assertEqual('aaaaaa.txt',
                         LogicLayer._shorten_filename('a' * 100 + '.txt',
                                                      max_length=10))
