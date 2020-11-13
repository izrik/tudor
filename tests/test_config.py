#!/usr/bin/env python

import unittest

from datetime import datetime
from decimal import Decimal

from conversions import bool_from_str, int_from_str, str_from_datetime
from conversions import money_from_str
from tudor import Config


class ConfigTest(unittest.TestCase):
    def test_repr(self):
        # given
        c = Config()
        # when
        result = repr(c)
        # then
        self.assertEqual(result,
                         'Config(DEBUG: None, HOST: None, PORT: None, '
                         'DB_URI: None, DB_URI_FILE: None, DB_OPTIONS: None, '
                         'DB_OPTIONS_FILE: None, UPLOAD_FOLDER: None, '
                         'ALLOWED_EXTENSIONS: None, SECRET_KEY: None, '
                         'SECRET_KEY_FILE: None, args: None)')

    def test_str(self):
        # given
        c = Config()
        # when
        result = str(c)
        # then
        self.assertEqual(result,
                         'DEBUG: None, HOST: None, PORT: None, DB_URI: None, '
                         'DB_URI_FILE: None, DB_OPTIONS: None, '
                         'DB_OPTIONS_FILE: None, UPLOAD_FOLDER: None, '
                         'ALLOWED_EXTENSIONS: None, SECRET_KEY: None, '
                         'SECRET_KEY_FILE: None, args: None')
