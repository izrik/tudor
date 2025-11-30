
from tests.persistence_t.in_memory.in_memory_test_base import InMemoryTestBase


# copied from ../test_get_option.py, with removals


class GetOptionTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

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
        self.assertEqual(option.id, result.id)
