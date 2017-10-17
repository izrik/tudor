import unittest

from models.task import Task
from tudor import generate_app, make_task_public, make_task_private


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.app.pl.create_all()

    def test_make_task_public(self):
        # given
        task = Task('task')
        task.id = 1
        self.app.pl.add(task)
        self.app.pl.commit()
        output = [None]

        def printer(*args):
            output[0] = args[0]

        # precondition
        self.assertFalse(task.is_public)
        # when
        make_task_public(self.app, task.id, printer=printer)
        # then
        self.assertTrue(task.is_public)
        # and
        self.assertEqual(['Made task 1, "task", public'], output)

    def test_make_task_public_non_existent(self):
        # given
        output = [None]

        def printer(*args):
            output[0] = args[0]

        # precondition
        self.assertEqual(0, self.app.pl.count_tasks())
        # when
        make_task_public(self.app, 1, printer=printer)
        # then
        self.assertEqual(['No task found by the id "1"'], output)

    def test_make_task_private(self):
        # given
        task = Task('task', is_public=True)
        task.id = 1
        self.app.pl.add(task)
        self.app.pl.commit()
        output = [None]

        def printer(*args):
            output[0] = args[0]

        # precondition
        self.assertTrue(task.is_public)
        # when
        make_task_private(self.app, task.id, printer=printer)
        # then
        self.assertFalse(task.is_public)
        # and
        self.assertEqual(['Made task 1, "task", private'], output)

    def test_make_task_private_non_existent(self):
        # given
        output = [None]

        def printer(*args):
            output[0] = args[0]

        # precondition
        self.assertEqual(0, self.app.pl.count_tasks())
        # when
        make_task_private(self.app, 1, printer=printer)
        # then
        self.assertEqual(['No task found by the id "1"'], output)
