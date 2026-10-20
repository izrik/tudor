import unittest

from sqlalchemy import text

from persistence.migration import (LEGACY_SCHEMA_VERSION_KEY,
                                   SCHEMA_VERSION_KEY,
                                   get_current_schema_version,
                                   set_schema_version)
from tests.util import generate_test_app


class SchemaVersionOptionTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_test_app()
        self.pl = self.app.pl

    def _stored_options(self):
        rows = self.pl.db.session.execute(
            text('select key, value from option;')).fetchall()
        return {row[0]: row[1] for row in rows}

    def _store(self, key, value):
        self.pl.execute(text('insert into option (key, value) '
                             f"values ('{key}', '{value}');"))
        self.pl.commit()

    def test_version_of_a_database_with_no_options_is_zero(self):
        # expect
        self.assertIsNone(self.pl.get_schema_version())
        self.assertEqual(0, get_current_schema_version(self.pl))

    def test_set_then_get(self):
        # when
        set_schema_version(self.pl, 18)
        # then
        option = self.pl.get_schema_version()
        self.assertEqual(SCHEMA_VERSION_KEY, option.key)
        self.assertEqual('18', option.value)
        self.assertEqual(18, get_current_schema_version(self.pl))

    def test_the_version_under_the_old_key_is_still_read(self):
        # given a database last touched before the key was renamed
        self._store(LEGACY_SCHEMA_VERSION_KEY, '0.17')
        # expect
        option = self.pl.get_schema_version()
        self.assertEqual(LEGACY_SCHEMA_VERSION_KEY, option.key)
        self.assertEqual(17, get_current_schema_version(self.pl))

    def test_the_new_key_wins_over_the_old_one(self):
        # given
        self._store(LEGACY_SCHEMA_VERSION_KEY, '0.17')
        self._store(SCHEMA_VERSION_KEY, '20')
        # expect
        self.assertEqual(SCHEMA_VERSION_KEY,
                         self.pl.get_schema_version().key)
        self.assertEqual(20, get_current_schema_version(self.pl))

    def test_recording_a_version_clears_out_the_old_key(self):
        # given
        self._store(LEGACY_SCHEMA_VERSION_KEY, '0.17')
        # when
        set_schema_version(self.pl, 18)
        # then
        self.assertEqual({SCHEMA_VERSION_KEY: '18'}, self._stored_options())

    def test_other_options_are_left_alone(self):
        # given
        self._store('some_other_option', 'value')
        # when
        set_schema_version(self.pl, 18)
        # then
        self.assertEqual({'some_other_option': 'value',
                          SCHEMA_VERSION_KEY: '18'},
                         self._stored_options())
