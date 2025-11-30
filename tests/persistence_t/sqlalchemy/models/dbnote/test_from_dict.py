import unittest
from datetime import datetime

from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class DbNoteFromDictTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()

    def test_empty_yields_empty_dbnote(self):
        # when
        result = self.pl.DbNote.from_dict({})
        # then
        self.assertIsInstance(result, self.pl.DbNote)
        self.assertIsNone(result.id)
        self.assertIsNone(result.content)
        self.assertIsNone(result.timestamp)

    def test_id_none_is_ignored(self):
        # when
        result = self.pl.DbNote.from_dict({'id': None})
        # then
        self.assertIsInstance(result, self.pl.DbNote)
        self.assertIsNone(result.id)

    def test_valid_id_gets_set(self):
        # when
        result = self.pl.DbNote.from_dict({'id': 123})
        # then
        self.assertIsInstance(result, self.pl.DbNote)
        self.assertEqual(123, result.id)

    def test_content_none_is_ignored(self):
        # when
        result = self.pl.DbNote.from_dict({'content': None})
        # then
        self.assertIsInstance(result, self.pl.DbNote)
        self.assertIsNone(result.content)

    def test_valid_content_gets_set(self):
        # when
        result = self.pl.DbNote.from_dict({'content': 'abc'})
        # then
        self.assertIsInstance(result, self.pl.DbNote)
        self.assertEqual('abc', result.content)

    def test_timestamp_none_becomes_none(self):
        # when
        result = self.pl.DbNote.from_dict({'timestamp': None})
        # then
        self.assertIsInstance(result, self.pl.DbNote)
        self.assertIsNone(result.timestamp)

    def test_valid_timestamp_gets_set(self):
        # when
        result = self.pl.DbNote.from_dict({'timestamp': datetime(2017, 1, 1)})
        # then
        self.assertIsInstance(result, self.pl.DbNote)
        self.assertEqual(datetime(2017, 1, 1), result.timestamp)

    def test_task_id_none_yields_none(self):
        # when
        result = self.pl.DbNote.from_dict({'task_id': None})
        # then
        self.assertIsInstance(result, self.pl.DbNote)
        self.assertIsNone(result.task_id)

    def test_task_id_not_none_yields_same(self):
        # given
        task = self.pl.DbTask('task')
        self.pl.save(task)
        # when
        result = self.pl.DbNote.from_dict({'task_id': task.id})
        # then
        self.assertIsInstance(result, self.pl.DbNote)
        self.assertEqual(task.id, result.task_id)

