#!/usr/bin/env python

import unittest

from datetime import datetime
from decimal import Decimal

from conversions import bool_from_str, int_from_str, str_from_datetime
from conversions import money_from_str


class TypeConversionFunctionTest(unittest.TestCase):
    def test_bool_from_str(self):
        # true, unsurprising
        self.assertTrue(bool_from_str('True'))
        self.assertTrue(bool_from_str('true'))
        self.assertTrue(bool_from_str('tRuE'))
        self.assertTrue(bool_from_str('t'))
        self.assertTrue(bool_from_str('1'))
        self.assertTrue(bool_from_str('y'))

        # true, surprising
        self.assertTrue(bool_from_str('tr'))
        self.assertTrue(bool_from_str('tru'))
        self.assertTrue(bool_from_str('truee'))
        self.assertTrue(bool_from_str('ye'))
        self.assertTrue(bool_from_str('yes'))

        # false, unsurprising
        self.assertFalse(bool_from_str('False'))
        self.assertFalse(bool_from_str('false'))
        self.assertFalse(bool_from_str('fAlSe'))
        self.assertFalse(bool_from_str('f'))
        self.assertFalse(bool_from_str('0'))
        self.assertFalse(bool_from_str('n'))

        # false, surprising
        self.assertTrue(bool_from_str('no'))
        self.assertTrue(bool_from_str('fa'))
        self.assertTrue(bool_from_str('fal'))
        self.assertTrue(bool_from_str('fals'))
        self.assertTrue(bool_from_str('falsee'))

        # true, non-string, somewhat surprising
        self.assertTrue(bool_from_str(1))
        self.assertTrue(bool_from_str([1]))
        self.assertTrue(bool_from_str([False]))

        # false, non-string
        self.assertFalse(bool_from_str([]))
        self.assertFalse(bool_from_str(''))
        self.assertFalse(bool_from_str(None))

    def test_int_from_str(self):
        self.assertEqual(1, int_from_str('1'))
        self.assertEqual(123, int_from_str('123'))
        self.assertEqual(-123, int_from_str('-123'))
        self.assertIsNone(int_from_str(None))
        self.assertIsNone(int_from_str(''))
        self.assertIsNone(int_from_str([]))
        self.assertIsNone(int_from_str([1]))
        self.assertEqual(1, int_from_str(True))

    def test_int_from_str_with_default(self):
        self.assertEqual(1, int_from_str('1', 555))
        self.assertEqual(123, int_from_str('123', 555))
        self.assertEqual(-123, int_from_str('-123', 555))
        self.assertEqual(555, int_from_str(None, 555))
        self.assertEqual(555, int_from_str('', 555))
        self.assertEqual(555, int_from_str([], 555))
        self.assertEqual(555, int_from_str([1], 555))
        self.assertEqual(1, int_from_str(True, 555))

    def test_str_from_datetime(self):
        self.assertIsNone(None, str_from_datetime(None))
        self.assertEqual('2016-02-03 00:00:00',
                          str_from_datetime(datetime(2016, 2, 3)))
        self.assertEqual('2016-02-03 12:34:56',
                          str_from_datetime(datetime(2016, 2, 3, 12, 34, 56)))

        self.assertEqual('2016-02-03', str_from_datetime('2016-02-03'))
        self.assertEqual('abcdefgh', str_from_datetime('abcdefgh'))

    def test_money_from_str(self):
        self.assertEqual(Decimal('123.46'), money_from_str('123.4567'))
        self.assertEqual(Decimal('12345678901234567890.0'),
                          money_from_str('12345678901234567890'))
        self.assertEqual(None, money_from_str(None))
