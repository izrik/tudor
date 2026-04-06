import unittest
from datetime import datetime

from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class DbCommentFromDictTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()

    def test_empty_yields_empty_dbcomment(self):
        # when
        result = self.pl.DbComment.from_dict({})
        # then
        self.assertIsInstance(result, self.pl.DbComment)
        self.assertIsNone(result.id)
        self.assertIsNone(result.content)
        self.assertIsNone(result.timestamp)
        self.assertIsNone(result.task)

    def test_id_none_is_ignored(self):
        # when
        result = self.pl.DbComment.from_dict({'id': None})
        # then
        self.assertIsInstance(result, self.pl.DbComment)
        self.assertIsNone(result.id)

    def test_valid_id_gets_set(self):
        # when
        result = self.pl.DbComment.from_dict({'id': 123})
        # then
        self.assertIsInstance(result, self.pl.DbComment)
        self.assertEqual(123, result.id)

    def test_content_none_is_ignored(self):
        # when
        result = self.pl.DbComment.from_dict({'content': None})
        # then
        self.assertIsInstance(result, self.pl.DbComment)
        self.assertIsNone(result.content)

    def test_valid_content_gets_set(self):
        # when
        result = self.pl.DbComment.from_dict({'content': 'abc'})
        # then
        self.assertIsInstance(result, self.pl.DbComment)
        self.assertEqual('abc', result.content)

    def test_timestamp_none_becomes_none(self):
        # when
        result = self.pl.DbComment.from_dict({'timestamp': None})
        # then
        self.assertIsInstance(result, self.pl.DbComment)
        self.assertIsNone(result.timestamp)

    def test_valid_timestamp_gets_set(self):
        # when
        result = self.pl.DbComment.from_dict({'timestamp': datetime(2017, 1, 1)})
        # then
        self.assertIsInstance(result, self.pl.DbComment)
        self.assertEqual(datetime(2017, 1, 1), result.timestamp)

    def test_task_none_yields_empty(self):
        # when
        result = self.pl.DbComment.from_dict({'task': None})
        # then
        self.assertIsInstance(result, self.pl.DbComment)
        self.assertIsNone(result.task)

    def test_task_not_none_yields_same(self):
        # given
        task = self.pl.DbTask('task')
        # when
        result = self.pl.DbComment.from_dict({'task': task})
        # then
        self.assertIsInstance(result, self.pl.DbComment)
        self.assertIs(task, result.task)

    def test_none_lazy_does_not_raise(self):
        # when
        result = self.pl.DbComment.from_dict({}, lazy=None)
        # then
        self.assertIsInstance(result, self.pl.DbComment)
        self.assertIsNone(result.id)
        self.assertIsNone(result.content)
        self.assertIsNone(result.timestamp)
        self.assertIsNone(result.task)

    def test_empty_lazy_does_not_raise(self):
        # when
        result = self.pl.DbComment.from_dict({}, lazy={})
        # then
        self.assertIsInstance(result, self.pl.DbComment)
        self.assertIsNone(result.id)
        self.assertIsNone(result.content)
        self.assertIsNone(result.timestamp)
        self.assertIsNone(result.task)

    def test_non_none_lazy_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl.DbComment.from_dict,
            {},
            lazy={'tasks': None})
