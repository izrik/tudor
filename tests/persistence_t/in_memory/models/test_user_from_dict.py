
import unittest

from persistence.in_memory.models.task import Task
from persistence.in_memory.models.user import User


class UserFromDictTest(unittest.TestCase):
    def test_empty_yields_empty_dbuser(self):
        # when
        result = User.from_dict({})
        # then
        self.assertIsInstance(result, User)
        self.assertIsNone(result.id)
        self.assertIsNone(result.email)
        self.assertIsNone(result.hashed_password)
        self.assertFalse(result.is_admin)
        self.assertEqual([], list(result.tasks))

    def test_id_none_is_ignored(self):
        # when
        result = User.from_dict({'id': None})
        # then
        self.assertIsInstance(result, User)
        self.assertIsNone(result.id)

    def test_valid_id_gets_set(self):
        # when
        result = User.from_dict({'id': 123})
        # then
        self.assertIsInstance(result, User)
        self.assertEqual(123, result.id)

    def test_email_none_is_ignored(self):
        # when
        result = User.from_dict({'email': None})
        # then
        self.assertIsInstance(result, User)
        self.assertIsNone(result.email)

    def test_valid_email_gets_set(self):
        # when
        result = User.from_dict({'email': 'name@example.com'})
        # then
        self.assertIsInstance(result, User)
        self.assertEqual('name@example.com', result.email)

    def test_hashed_password_none_becomes_none(self):
        # when
        result = User.from_dict({'hashed_password': None})
        # then
        self.assertIsInstance(result, User)
        self.assertIsNone(result.hashed_password)

    def test_valid_hashed_password_gets_set(self):
        # when
        result = User.from_dict({'hashed_password': 'abc'})
        # then
        self.assertIsInstance(result, User)
        self.assertEqual('abc', result.hashed_password)

    def test_is_admin_none_becomes_none(self):
        # when
        result = User.from_dict({'is_admin': None})
        # then
        self.assertIsInstance(result, User)
        self.assertIsNone(result.is_admin)

    def test_valid_is_admin_gets_set(self):
        # when
        result = User.from_dict({'is_admin': True})
        # then
        self.assertIsInstance(result, User)
        self.assertTrue(result.is_admin)

    def test_tasks_none_yields_empty(self):
        # when
        result = User.from_dict({'tasks': None})
        # then
        self.assertIsInstance(result, User)
        self.assertEqual([], list(result.tasks))

    def test_tasks_empty_yields_empty(self):
        # when
        result = User.from_dict({'tasks': []})
        # then
        self.assertIsInstance(result, User)
        self.assertEqual([], list(result.tasks))

    def test_tasks_non_empty_yields_same(self):
        # given
        task = Task('task')
        # when
        result = User.from_dict({'tasks': [task]})
        # then
        self.assertIsInstance(result, User)
        self.assertEqual([task], list(result.tasks))
