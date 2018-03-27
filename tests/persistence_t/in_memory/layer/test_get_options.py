
from tests.persistence_t.in_memory.in_memory_test_base import InMemoryTestBase


# copied from ../test_get_options.py, with removals


class GetOptionsTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.option1 = self.pl.create_option('option1', 'value1')
        self.pl.add(self.option1)
        self.option2 = self.pl.create_option('option2', 'value2')
        self.pl.add(self.option2)
        self.pl.commit()

    def test_get_options_without_params_returns_all_options(self):
        # when
        results = self.pl.get_options()
        # then
        self.assertEqual({self.option1, self.option2}, set(results))

    def test_count_options_without_params_returns_all_options(self):
        # expect
        self.assertEqual(2, self.pl.count_options())

    def test_get_options_key_in_filters_only_matching_options(self):
        # when
        results = self.pl.get_options(key_in=[self.option1.key])
        # then
        self.assertEqual({self.option1}, set(results))
        # when
        results = self.pl.get_options(key_in=[self.option2.key])
        # then
        self.assertEqual({self.option2}, set(results))
        # when
        results = self.pl.get_options(
            key_in=[self.option1.key, self.option2.key])
        # then
        self.assertEqual({self.option1, self.option2}, set(results))

    def test_get_options_key_in_unmatching_keys_do_not_filter(self):
        # given
        next_key = 'option3'
        # when
        results = self.pl.get_options(
            key_in=[self.option1.key, self.option2.key, next_key])
        # then
        self.assertEqual({self.option1, self.option2}, set(results))

    def test_get_options_key_in_empty_yields_no_options(self):
        # when
        results = self.pl.get_options(key_in=[])
        # then
        self.assertEqual(set(), set(results))

    def test_count_options_key_in_filters_only_matching_options(self):
        # expect
        self.assertEqual(1, self.pl.count_options(key_in=[self.option1.key]))
        # expect
        self.assertEqual(1, self.pl.count_options(key_in=[self.option2.key]))
        # expect
        self.assertEqual(2, self.pl.count_options(
            key_in=[self.option1.key, self.option2.key]))

    def test_count_options_key_in_unmatching_keys_do_not_filter(self):
        # given
        next_key = 'option3'
        # when
        results = self.pl.count_options(
            key_in=[self.option1.key, self.option2.key, next_key])
        # then
        self.assertEqual(2, results)

    def test_count_options_key_in_empty_yields_no_options(self):
        # expect
        self.assertEqual(0, self.pl.count_options(key_in=[]))
