
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class GetTagTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()

    def test_get_tag_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_tag, None)

    def test_get_tag_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_tag(1))

    def test_get_tag_existing_yields_that_tag(self):
        # given
        tag = self.pl.create_tag('tag')
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(tag.id)
        # when
        result = self.pl.get_tag(tag.id)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(tag.id, result.id)

    def test_get_db_tag_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl._get_db_tag, None)

    def test_get_db_tag_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl._get_db_tag(1))

    def test_get_db_tag_existing_yields_that_dbtag(self):
        # given
        dbtag = self.pl.DbTag('tag')
        self.pl.db.session.add(dbtag)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbtag.id)
        # when
        result = self.pl._get_db_tag(dbtag.id)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(dbtag.id, result.id)
