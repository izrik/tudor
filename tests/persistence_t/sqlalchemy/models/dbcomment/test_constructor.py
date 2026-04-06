from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class DbCommentConstructorTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()

    def test_none_lazy_is_allowed(self):
        # when
        comment = self.pl.DbComment('comment', lazy={})
        # then
        self.assertIsInstance(comment, self.pl.DbComment)

    def test_empty_lazy_is_allowed(self):
        # when
        comment = self.pl.DbComment('comment', lazy={})
        # then
        self.assertIsInstance(comment, self.pl.DbComment)

    def test_non_empty_lazy_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.DbComment, 'comment', lazy={'id': 1})
