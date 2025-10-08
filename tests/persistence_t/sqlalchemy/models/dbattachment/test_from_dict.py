from datetime import datetime

from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class DbAttachmentFromDictTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()

    def test_empty_yields_empty_dbattachment(self):
        # when
        result = self.pl.DbAttachment.from_dict({})
        # then
        self.assertIsInstance(result, self.pl.DbAttachment)
        self.assertIsNone(result.id)
        self.assertIsNone(result.path)
        self.assertIsNone(result.description)
        self.assertIsNone(result.timestamp)
        self.assertIsNone(result.filename)

    def test_id_none_is_ignored(self):
        # when
        result = self.pl.DbAttachment.from_dict({'id': None})
        # then
        self.assertIsInstance(result, self.pl.DbAttachment)
        self.assertIsNone(result.id)

    def test_valid_id_gets_set(self):
        # when
        result = self.pl.DbAttachment.from_dict({'id': 123})
        # then
        self.assertIsInstance(result, self.pl.DbAttachment)
        self.assertEqual(123, result.id)

    def test_path_none_is_ignored(self):
        # when
        result = self.pl.DbAttachment.from_dict({'path': None})
        # then
        self.assertIsInstance(result, self.pl.DbAttachment)
        self.assertIsNone(result.path)

    def test_valid_path_gets_set(self):
        # when
        result = self.pl.DbAttachment.from_dict({'path': 'abc'})
        # then
        self.assertIsInstance(result, self.pl.DbAttachment)
        self.assertEqual('abc', result.path)

    def test_description_none_is_ignored(self):
        # when
        result = self.pl.DbAttachment.from_dict({'description': None})
        # then
        self.assertIsInstance(result, self.pl.DbAttachment)
        self.assertIsNone(result.description)

    def test_valid_description_gets_set(self):
        # when
        result = self.pl.DbAttachment.from_dict({'description': 'abc'})
        # then
        self.assertIsInstance(result, self.pl.DbAttachment)
        self.assertEqual('abc', result.description)

    def test_timestamp_none_becomes_none(self):
        # when
        result = self.pl.DbAttachment.from_dict({'timestamp': None})
        # then
        self.assertIsInstance(result, self.pl.DbAttachment)
        self.assertIsNone(result.timestamp)

    def test_valid_timestamp_gets_set(self):
        # when
        result = self.pl.DbAttachment.from_dict({'timestamp':
                                                 datetime(2017, 1, 1)})
        # then
        self.assertIsInstance(result, self.pl.DbAttachment)
        self.assertEqual(datetime(2017, 1, 1), result.timestamp)

    def test_filename_none_is_ignored(self):
        # when
        result = self.pl.DbAttachment.from_dict({'filename': None})
        # then
        self.assertIsInstance(result, self.pl.DbAttachment)
        self.assertIsNone(result.filename)

    def test_valid_filename_gets_set(self):
        # when
        result = self.pl.DbAttachment.from_dict({'filename': 'abc'})
        # then
        self.assertIsInstance(result, self.pl.DbAttachment)
        self.assertEqual('abc', result.filename)

    def test_task_none_yields_empty(self):
        # when
        result = self.pl.DbAttachment.from_dict({'task': None})
        # then
        self.assertIsInstance(result, self.pl.DbAttachment)
        self.assertIsNone(result.task)

    def test_task_not_none_yields_same(self):
        # given
        task = self.pl.DbTask('task')
        # when
        result = self.pl.DbAttachment.from_dict({'task': task})
        # then
        self.assertIsInstance(result, self.pl.DbAttachment)
        self.assertIs(task, result.task)
