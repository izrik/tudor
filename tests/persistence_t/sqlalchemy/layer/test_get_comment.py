
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class GetCommentTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()

    def test_get_comment_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_comment, None)

    def test_get_comment_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_comment(1))

    def test_get_comment_existing_yields_that_comment(self):
        # given
        comment = self.pl.create_comment('comment')
        self.pl.add(comment)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(comment.id)
        # when
        result = self.pl.get_comment(comment.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(comment, result)

    def test_get_db_comment_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl._get_db_comment, None)

    def test_get_db_comment_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl._get_db_comment(1))

    def test_get_db_comment_existing_yields_that_dbcomment(self):
        # given
        dbcomment = self.pl.DbComment('comment')
        self.pl.db.session.add(dbcomment)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbcomment.id)
        # when
        result = self.pl._get_db_comment(dbcomment.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(dbcomment, result)
