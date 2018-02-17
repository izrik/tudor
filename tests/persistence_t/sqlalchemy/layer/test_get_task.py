
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class GetTaskTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

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
        self.assertIs(task, result)
