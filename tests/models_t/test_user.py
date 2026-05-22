import unittest

from models.user import User


class UserTest(unittest.TestCase):
    def test_minimal_construction(self):
        u = User(email='a@b.c')
        self.assertEqual(u.email, 'a@b.c')
        self.assertIsNone(u.id)
        self.assertIsNone(u.hashed_password)
        self.assertFalse(u.is_admin)

    def test_full_construction(self):
        u = User(id=1, email='a@b.c', hashed_password='h', is_admin=True)
        self.assertEqual(u.id, 1)
        self.assertEqual(u.email, 'a@b.c')
        self.assertEqual(u.hashed_password, 'h')
        self.assertTrue(u.is_admin)

    def test_to_dict_omits_tasks(self):
        u = User(id=1, email='a@b.c')
        d = u.to_dict()
        self.assertNotIn('tasks', d)
        self.assertNotIn('task_ids', d)

    def test_flask_login_helpers(self):
        u = User(email='a@b.c')
        self.assertTrue(u.is_active())
        self.assertTrue(u.is_authenticated)
        self.assertFalse(u.is_anonymous)
        self.assertEqual(u.get_id(), 'a@b.c')

    def test_round_trip(self):
        u = User(id=1, email='a@b.c', hashed_password='h', is_admin=True)
        u2 = User.from_dict(u.to_dict())
        self.assertEqual(u2.id, 1)
        self.assertEqual(u2.email, 'a@b.c')
        self.assertEqual(u2.hashed_password, 'h')
        self.assertTrue(u2.is_admin)
