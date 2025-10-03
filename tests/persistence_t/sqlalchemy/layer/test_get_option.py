
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class GetOptionTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()

    def test_get_option_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_option, None)

    def test_get_option_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_option(1))

    def test_get_option_existing_yields_that_option(self):
        # given
        option = self.pl.create_option('key', 'value')
        self.pl.add(option)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(option.id)
        # when
        result = self.pl.get_option(option.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(option, result)

    def test_get_db_option_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl._get_db_option, None)

    def test_get_db_option_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl._get_db_option(1))

    def test_get_db_option_existing_yields_that_dboption(self):
        # given
        dboption = self.pl.DbOption('key', 'value')
        self.pl.db.session.add(dboption)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dboption.id)
        # when
        result = self.pl._get_db_option(dboption.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(dboption, result)
