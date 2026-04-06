
from tests.persistence_t.in_memory.in_memory_test_base import InMemoryTestBase


# copied from ../test_get_comments.py, with removals


class GetCommentsTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.n1 = self.pl.create_comment('n1')
        self.pl.add(self.n1)
        self.n2 = self.pl.create_comment('n2')
        self.pl.add(self.n2)
        self.pl.commit()

    def test_get_comments_without_params_returns_all_comments(self):
        # when
        results = self.pl.get_comments()
        # then
        self.assertEqual({self.n1, self.n2}, set(results))

    def test_count_comments_without_params_returns_all_comments(self):
        # expect
        self.assertEqual(2, self.pl.count_comments())

    def test_get_comments_comment_id_in_filters_only_matching_comments(self):
        # when
        results = self.pl.get_comments(comment_id_in=[self.n1.id])
        # then
        self.assertEqual({self.n1}, set(results))
        # when
        results = self.pl.get_comments(comment_id_in=[self.n2.id])
        # then
        self.assertEqual({self.n2}, set(results))
        # when
        results = self.pl.get_comments(comment_id_in=[self.n1.id, self.n2.id])
        # then
        self.assertEqual({self.n1, self.n2}, set(results))

    def test_get_comments_comment_id_in_unmatching_ids_do_not_filter(self):
        # given
        next_id = max([self.n1.id, self.n2.id]) + 1
        # when
        results = self.pl.get_comments(
            comment_id_in=[self.n1.id, self.n2.id, next_id])
        # then
        self.assertEqual({self.n1, self.n2}, set(results))

    def test_get_comments_comment_id_in_empty_yields_no_comments(self):
        # when
        results = self.pl.get_comments(comment_id_in=[])
        # then
        self.assertEqual(set(), set(results))

    def test_count_comments_comment_id_in_filters_only_matching_comments(self):
        # expect
        self.assertEqual(1, self.pl.count_comments(comment_id_in=[self.n1.id]))
        # expect
        self.assertEqual(1, self.pl.count_comments(comment_id_in=[self.n2.id]))
        # expect
        self.assertEqual(2, self.pl.count_comments(
            comment_id_in=[self.n1.id, self.n2.id]))

    def test_count_comments_comment_id_in_unmatching_ids_do_not_filter(self):
        # given
        next_id = max([self.n1.id, self.n2.id]) + 1
        # when
        results = self.pl.count_comments(
            comment_id_in=[self.n1.id, self.n2.id, next_id])
        # then
        self.assertEqual(2, results)

    def test_count_comments_comment_id_in_empty_yields_no_comments(self):
        # expect
        self.assertEqual(0, self.pl.count_comments(comment_id_in=[]))
