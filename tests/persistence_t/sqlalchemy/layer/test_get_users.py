
from models.object_types import ObjectTypes
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class GetUsersTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()
        self.user1 = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(self.user1)
        self.user2 = self.pl.create_user('name@example.com')
        self.pl.add(self.user2)
        self.pl.commit()

    def test_get_user_by_email(self):
        # when
        results = self.pl.get_user_by_email('admin@example.com')
        # then
        self.assertIs(self.user1, results)
        # when
        results = self.pl.get_user_by_email('name@example.com')
        # then
        self.assertIs(self.user2, results)

    def test_get_user_by_email_invalid_email_yields_none(self):
        # when
        results = self.pl.get_user_by_email('someone@example.org')
        # then
        self.assertIsNone(results)

    def test_get_user_by_email_returns_none_after_email_changes(self):
        # given
        self.user1.email = 'asdf'
        self.pl.commit()
        # precondition
        self.assertEqual('asdf', self.user1.email)
        # when
        result = self.pl.get_user_by_email('user1')
        # then
        self.assertIsNone(result)

    def test_get_user_by_email_returns_user_after_email_changes(self):
        # given
        self.user1.email = 'asdf'
        self.pl.commit()
        # precondition
        self.assertEqual('asdf', self.user1.email)
        # when
        result = self.pl.get_user_by_email('asdf')
        # then
        self.assertIsNotNone(result)
        self.assertEqual(result.object_type, ObjectTypes.User)
        self.assertIs(self.user1, result)

    def test_get_users_without_params_returns_all_users(self):
        # when
        results = self.pl.get_users()
        # then
        self.assertEqual({self.user1, self.user2}, set(results))

    def test_count_users_without_params_returns_all_users(self):
        # expect
        self.assertEqual(2, self.pl.count_users())

    def test_get_users_email_in_filters_only_matching_users(self):
        # when
        results = self.pl.get_users(email_in=[self.user1.email])
        # then
        self.assertEqual({self.user1}, set(results))
        # when
        results = self.pl.get_users(email_in=[self.user2.email])
        # then
        self.assertEqual({self.user2}, set(results))
        # when
        results = self.pl.get_users(
            email_in=[self.user1.email, self.user2.email])
        # then
        self.assertEqual({self.user1, self.user2}, set(results))

    def test_get_users_email_in_unmatching_emails_do_not_filter(self):
        # given
        next_email = (list({self.user1.email, self.user2.email}))[0] + 'a'
        # when
        results = self.pl.get_users(
            email_in=[self.user1.email, self.user2.email, next_email])
        # then
        self.assertEqual({self.user1, self.user2}, set(results))

    def test_get_users_email_in_empty_yields_no_users(self):
        # when
        results = self.pl.get_users(email_in=[])
        # then
        self.assertEqual(set(), set(results))

    def test_count_users_email_in_filters_only_matching_users(self):
        # expect
        self.assertEqual(1, self.pl.count_users(email_in=[self.user1.email]))
        # expect
        self.assertEqual(1, self.pl.count_users(email_in=[self.user2.email]))
        # expect
        self.assertEqual(2, self.pl.count_users(
            email_in=[self.user1.email, self.user2.email]))

    def test_count_users_email_in_unmatching_emails_do_not_filter(self):
        # given
        next_email = (list({self.user1.email, self.user2.email}))[0] + 'a'
        # when
        results = self.pl.count_users(
            email_in=[self.user1.email, self.user2.email, next_email])
        # then
        self.assertEqual(2, results)

    def test_count_users_email_in_empty_yields_no_users(self):
        # expect
        self.assertEqual(0, self.pl.count_users(email_in=[]))
