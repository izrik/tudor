from datetime import datetime

from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class CreateTaskTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_has_sensible_defaults(self):
        # when
        task = self.pl.create_task('summary')
        # then
        self.assertEqual('', task.description)
        self.assertFalse(task.is_done)
        self.assertFalse(task.is_deleted)
        self.assertIsNone(task.deadline)
        self.assertIsNone(task.expected_duration_minutes)
        self.assertIsNone(task.expected_cost)
        self.assertFalse(task.is_public)

    def test_sets_fields(self):
        # when
        task = self.pl.create_task(
            summary='summary',
            description='description',
            is_done=True,
            is_deleted=True,
            deadline='2038-01-19',
            expected_duration_minutes=5,
            expected_cost=7,
            is_public=True)
        # then
        self.assertEqual('description', task.description)
        self.assertTrue(task.is_done)
        self.assertTrue(task.is_deleted)
        self.assertEqual(datetime(2038, 1, 19), task.deadline)
        self.assertEqual(5, task.expected_duration_minutes)
        self.assertEqual(7, task.expected_cost)
        self.assertTrue(task.is_public)
