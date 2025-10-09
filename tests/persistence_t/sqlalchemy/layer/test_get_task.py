
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class GetTaskTest(PersistenceLayerTestBase):

    def test_none_returns_none(self):
        # when
        result = self.pl.get_task(None)
        # then
        self.assertIsNone(result)

    def test_non_existent_task_returns_none(self):
        # when
        result = self.pl.get_task(2)
        # then
        self.assertIsNone(result)

    def test_valid_task_returns_task(self):
        # given
        task = self.pl.create_task('task')
        self.pl.add(task)
        self.pl.commit()
        # when
        result = self.pl.get_task(1)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(task.id, result.id)
        self.assertEqual(task.summary, result.summary)
