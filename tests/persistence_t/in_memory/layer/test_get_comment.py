
from tests.persistence_t.in_memory.in_memory_test_base import InMemoryTestBase


# copied from ../test_get_comment.py, with removals


class GetCommentTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

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
