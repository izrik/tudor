from persistence.in_memory.models.task import Task
from tests.persistence_t.in_memory.in_memory_test_base \
    import InMemoryTestBase


# copied from ../test_get_task.py


class GetTaskTest(InMemoryTestBase):
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
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        # when
        result = self.pl.get_task(1)
        # then
        self.assertIsNotNone(result)
        self.assertIs(task, result)
