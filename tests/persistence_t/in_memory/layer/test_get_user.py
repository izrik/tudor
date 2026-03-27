
from tests.persistence_t.in_memory.in_memory_test_base import InMemoryTestBase


# copied from ../test_get_user.py, with removals


class GetUserTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_get_user_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_user, None)

    def test_get_user_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_user(1))

    def test_get_user_existing_yields_that_user(self):
        # given
        user = self.pl.create_user('user')
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(user.id)
        # when
        result = self.pl.get_user(user.id)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(user.id, result.id)
