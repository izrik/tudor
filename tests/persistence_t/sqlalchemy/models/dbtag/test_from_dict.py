from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class DbTagFromDictTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()

    def test_empty_yields_empty_dbtag(self):
        # when
        result = self.pl.DbTag.from_dict({})
        # then
        self.assertIsInstance(result, self.pl.DbTag)
        self.assertIsNone(result.id)
        self.assertIsNone(result.value)
        self.assertIsNone(result.description)
        self.assertEqual([], list(result.tasks))

    def test_id_none_is_ignored(self):
        # when
        result = self.pl.DbTag.from_dict({'id': None})
        # then
        self.assertIsInstance(result, self.pl.DbTag)
        self.assertIsNone(result.id)

    def test_valid_id_gets_set(self):
        # when
        result = self.pl.DbTag.from_dict({'id': 123})
        # then
        self.assertIsInstance(result, self.pl.DbTag)
        self.assertEqual(123, result.id)

    def test_value_none_is_ignored(self):
        # when
        result = self.pl.DbTag.from_dict({'value': None})
        # then
        self.assertIsInstance(result, self.pl.DbTag)
        self.assertIsNone(result.value)

    def test_valid_value_gets_set(self):
        # when
        result = self.pl.DbTag.from_dict({'value': 'abc'})
        # then
        self.assertIsInstance(result, self.pl.DbTag)
        self.assertEqual('abc', result.value)

    def test_description_none_becomes_none(self):
        # when
        result = self.pl.DbTag.from_dict({'description': None})
        # then
        self.assertIsInstance(result, self.pl.DbTag)
        self.assertIsNone(result.description)

    def test_valid_description_gets_set(self):
        # when
        result = self.pl.DbTag.from_dict({'description': 'abc'})
        # then
        self.assertIsInstance(result, self.pl.DbTag)
        self.assertEqual('abc', result.description)

    def test_tasks_none_yields_empty(self):
        # when
        result = self.pl.DbTag.from_dict({'tasks': None})
        # then
        self.assertIsInstance(result, self.pl.DbTag)
        self.assertEqual([], list(result.tasks))

    def test_tasks_empty_yields_empty(self):
        # when
        result = self.pl.DbTag.from_dict({'tasks': []})
        # then
        self.assertIsInstance(result, self.pl.DbTag)
        self.assertEqual([], list(result.tasks))

    def test_tasks_non_empty_yields_same(self):
        # given
        task = self.pl.DbTask('task')
        # when
        result = self.pl.DbTag.from_dict({'tasks': [task]})
        # then
        self.assertIsInstance(result, self.pl.DbTag)
        self.assertEqual([task], list(result.tasks))

    def test_none_lazy_does_not_raise(self):
        # when
        result = self.pl.DbTag.from_dict({}, lazy=None)
        # then
        self.assertIsInstance(result, self.pl.DbTag)
        self.assertIsNone(result.id)
        self.assertIsNone(result.value)
        self.assertIsNone(result.description)
        self.assertEqual([], list(result.tasks))

    def test_empty_lazy_does_not_raise(self):
        # when
        result = self.pl.DbTag.from_dict({}, lazy={})
        # then
        self.assertIsInstance(result, self.pl.DbTag)
        self.assertIsNone(result.id)
        self.assertIsNone(result.value)
        self.assertIsNone(result.description)
        self.assertEqual([], list(result.tasks))

    def test_non_none_lazy_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl.DbTag.from_dict,
            {},
            lazy={'tasks': None})
