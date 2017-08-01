#!/usr/bin/env python

import unittest
from datetime import datetime

from models.note import Note, NoteBase


class CleanTimestampTest(unittest.TestCase):
    def test_none_yields_none(self):
        # expect
        self.assertIsNone(NoteBase._clean_timestamp(None))

    def test_string_gets_parsed(self):
        # when
        result = NoteBase._clean_timestamp('2017-01-01')
        # then
        self.assertEqual(datetime(2017, 1, 1), result)

    def test_unicode_gets_parsed(self):
        # when
        result = NoteBase._clean_timestamp(u'2017-01-01')
        # then
        self.assertEqual(datetime(2017, 1, 1), result)

    def test_datetime_gets_set(self):
        # when
        result = NoteBase._clean_timestamp(datetime(2017, 1, 1))
        # then
        self.assertEqual(datetime(2017, 1, 1), result)
