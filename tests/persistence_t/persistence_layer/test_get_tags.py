import unittest

from persistence.in_memory.models.tag import Tag
from tests.persistence_t.persistence_layer.util import PersistenceLayerTestBase


class GetTagsTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.t1 = Tag('t1')
        self.pl.add(self.t1)
        self.t2 = Tag('t2')
        self.pl.add(self.t2)
        self.pl.commit()

    def test_get_tags_without_params_returns_all_tags(self):
        # when
        results = self.pl.get_tags()
        # then
        self.assertEqual({self.t1, self.t2}, set(results))

    def test_specifying_value_filters_tags_1(self):
        # when
        results = self.pl.get_tags(value='t1')
        # then
        self.assertEqual({self.t1}, set(results))

    def test_specifying_value_filters_tags_2(self):
        # when
        results = self.pl.get_tags(value='t2')
        # then
        self.assertEqual({self.t2}, set(results))

    def test_non_existing_value_yields_empty(self):
        # when
        results = self.pl.get_tags(value='tx')
        # then
        self.assertEqual(set(), set(results))

    def test_limit_yields_only_that_many_tags(self):
        # when
        results = self.pl.get_tags(limit=1)
        # then
        results = list(results)
        self.assertEqual(1, len(results))
        self.assertIn(results[0], {self.t1, self.t2})

    def test_limit_greater_than_max_yields_max(self):
        # when
        results = self.pl.get_tags(limit=3)
        # then
        self.assertEqual({self.t1, self.t2}, set(results))

    def test_limit_zero_yields_empty(self):
        # when
        results = self.pl.get_tags(limit=0)
        # then
        self.assertEqual(set(), set(results))

    def test_count_tags_without_params_returns_total_count(self):
        # when
        results = self.pl.count_tags()
        # then
        self.assertEqual(2, results)

    def test_count_tags_specifying_value_returns_one(self):
        # when
        results = self.pl.count_tags(value='t1')
        # then
        self.assertEqual(1, results)

    def test_count_tags_specifying_limit_returns_that_limit(self):
        # given
        t3 = Tag('t3')
        self.pl.add(t3)
        self.pl.commit()
        # when
        results = self.pl.count_tags(limit=1)
        # then
        self.assertEqual(1, results)
        # when
        results = self.pl.count_tags(limit=2)
        # then
        self.assertEqual(2, results)
        # when
        results = self.pl.count_tags(limit=3)
        # then
        self.assertEqual(3, results)

    def test_count_tags_limit_greater_than_max_yields_max(self):
        # given
        t3 = Tag('t3')
        self.pl.add(t3)
        self.pl.commit()
        # when
        results = self.pl.count_tags(limit=4)
        # then
        self.assertEqual(3, results)

    def test_get_tag_by_value_tag_present_returns_tag(self):
        # when
        results = self.pl.get_tag_by_value('t1')
        # then
        self.assertIsNotNone(results)
        self.assertIsInstance(results, Tag)
        self.assertIs(self.t1, results)

    def test_get_tag_by_value_tag_missing_returns_none(self):
        # when
        results = self.pl.get_tag_by_value('x')
        # then
        self.assertIsNone(results)

    def test_get_tag_by_value_returns_none_after_value_changes(self):
        # given
        self.t1.value = 'asdf'
        self.pl.commit()
        # precondition
        self.assertEqual('asdf', self.t1.value)
        # when
        result = self.pl.get_tag_by_value('t1')
        # then
        self.assertIsNone(result)

    def test_get_tag_by_value_returns_tag_after_value_changes(self):
        # given
        self.t1.value = 'asdf'
        self.pl.commit()
        # precondition
        self.assertEqual('asdf', self.t1.value)
        # when
        result = self.pl.get_tag_by_value('asdf')
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Tag)
        self.assertIs(self.t1, result)
