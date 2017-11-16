import unittest

from models.changeable import Changeable
from models.task import Task
from models.user import User
from tests.persistence_layer_t.util import PersistenceLayerTestBase


class DbUserMakeChangeTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.user = self.pl.DbUser('name@example.com')

    def test_setting_id_sets_id(self):
        # precondition
        self.assertIsNone(self.user.id)
        # when
        self.user.make_change(User.FIELD_ID, Changeable.OP_SET, 1)
        # then
        self.assertEqual(1, self.user.id)

    def test_adding_id_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            User.FIELD_ID, Changeable.OP_ADD, 1)

    def test_removing_id_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            User.FIELD_ID, Changeable.OP_REMOVE, 1)

    def test_changing_id_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            User.FIELD_ID, Changeable.OP_CHANGING, 1)

    def test_setting_email_sets_email(self):
        # precondition
        self.assertEqual('name@example.com', self.user.email)
        # when
        self.user.make_change(User.FIELD_EMAIL, Changeable.OP_SET,
                              'another@example.com')
        # then
        self.assertEqual('another@example.com', self.user.email)

    def test_adding_email_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            User.FIELD_EMAIL, Changeable.OP_ADD, 'another@example.com')

    def test_removing_email_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            User.FIELD_EMAIL, Changeable.OP_REMOVE, 'another@example.com')

    def test_changing_email_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            User.FIELD_EMAIL, Changeable.OP_CHANGING, 'another@example.com')

    def test_setting_hashed_password_sets_hashed_password(self):
        # precondition
        self.assertIsNone(self.user.hashed_password)
        # when
        self.user.make_change(User.FIELD_HASHED_PASSWORD, Changeable.OP_SET,
                              'b')
        # then
        self.assertEqual('b', self.user.hashed_password)

    def test_adding_hashed_password_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            User.FIELD_HASHED_PASSWORD, Changeable.OP_ADD, 'b')

    def test_removing_hashed_password_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            User.FIELD_HASHED_PASSWORD, Changeable.OP_REMOVE, 'b')

    def test_changing_hashed_password_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            User.FIELD_HASHED_PASSWORD, Changeable.OP_CHANGING, 'b')

    def test_setting_is_admin_sets_is_admin(self):
        # precondition
        self.assertFalse(self.user.is_admin)
        # when
        self.user.make_change(User.FIELD_IS_ADMIN, Changeable.OP_SET, True)
        # then
        self.assertTrue(self.user.is_admin)

    def test_adding_is_admin_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            User.FIELD_IS_ADMIN, Changeable.OP_ADD, True)

    def test_removing_is_admin_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            User.FIELD_IS_ADMIN, Changeable.OP_REMOVE, True)

    def test_changing_is_admin_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            User.FIELD_IS_ADMIN, Changeable.OP_CHANGING, True)

    def test_adding_tasks_adds(self):
        # given
        task = self.pl.DbTask('task')
        # precondition
        self.assertEqual([], list(self.user.tasks))
        # when
        self.user.make_change(User.FIELD_TASKS, Changeable.OP_ADD, task)
        # then
        self.assertEqual([task], list(self.user.tasks))

    def test_removing_tasks_removes(self):
        # given
        task = self.pl.DbTask('task')
        self.user.tasks.append(task)
        # precondition
        self.assertEqual([task], list(self.user.tasks))
        # when
        self.user.make_change(User.FIELD_TASKS, Changeable.OP_REMOVE, task)
        # then
        self.assertEqual([], list(self.user.tasks))

    def test_setting_tasks_raises(self):
        # given
        task = self.pl.DbTask('task')
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            User.FIELD_TASKS, Changeable.OP_SET, task)

    def test_changing_tasks_raises(self):
        # given
        task = self.pl.DbTask('task')
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            User.FIELD_TASKS, Changeable.OP_CHANGING, task)

    def test_non_user_field_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            Task.FIELD_SUMMARY, Changeable.OP_SET, 'value')

    def test_invalid_field_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.user.make_change,
            'SOME_OTHER_FIELD', Changeable.OP_SET, 'value')

    def test_adding_task_already_in_silently_ignored(self):
        # given
        task = self.pl.DbTask('task')
        self.user.tasks.append(task)
        # precondition
        self.assertEqual([task], list(self.user.tasks))
        # when
        self.user.make_change(User.FIELD_TASKS, Changeable.OP_ADD, task)
        # then
        self.assertEqual([task], list(self.user.tasks))

    def test_removing_task_not_in_silently_ignored(self):
        # given
        task = self.pl.DbTask('task')
        # precondition
        self.assertEqual([], list(self.user.tasks))
        # when
        self.user.make_change(User.FIELD_TASKS, Changeable.OP_REMOVE, task)
        # then
        self.assertEqual([], list(self.user.tasks))
