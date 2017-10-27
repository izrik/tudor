import unittest

from models.task import Task
from tests.persistence_layer_t.util import generate_pl, \
    PersistenceLayerTestBase


class GetTaskTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = generate_pl()
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
