import unittest

from mock import Mock
from werkzeug.exceptions import NotFound, BadRequest

from logic.layer import LogicLayer
from models.task import Task
from models.user import User
from persistence.in_memory.layer import InMemoryPersistenceLayer
from tests.view_t.layer.ViewLayer.util import generate_mock_request
from view.layer import ViewLayer, DefaultRenderer


class TaskPurgeTest(unittest.TestCase):
    def setUp(self):
        self.pl = Mock(spec=InMemoryPersistenceLayer)
        self.ll = Mock(spec=LogicLayer)
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)
        self.admin = Mock(spec=User)

    def test_purges_deleted_task(self):
        # given
        task = Mock(spec=Task)
        task.is_deleted = True
        self.ll.pl_get_task.return_value = task
        request = generate_mock_request(method="GET")
        task_id = 123
        # when
        result = self.vl.task_purge(request, self.admin, task_id)
        # then
        self.ll.purge_task.assert_called_once_with(task, self.admin)
        # and
        self.ll.pl_get_task.assert_called_once_with(task_id)
        self.pl.get_task.assert_not_called()
        self.r.url_for.assert_called_once_with('index')
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)

    def test_task_not_found_raises(self):
        # given
        self.ll.pl_get_task.return_value = None
        request = generate_mock_request(method="GET")
        task_id = 123
        # expect
        with self.assertRaises(NotFound) as cm:
            self.vl.task_purge(request, self.admin, task_id)
        # then
        self.assertEqual("No task found for the id '123'",
                         cm.exception.description)
        self.ll.purge_task.assert_not_called()
        # and
        self.ll.pl_get_task.assert_called_once_with(task_id)
        self.pl.get_task.assert_not_called()
        self.r.url_for.assert_not_called()
        self.r.redirect.assert_not_called()

    def test_task_not_deleted_raises(self):
        # given
        task = Mock(spec=Task)
        task.is_deleted = False
        self.ll.pl_get_task.return_value = task
        request = generate_mock_request(method="GET")
        task_id = 123
        # expect
        with self.assertRaises(BadRequest) as cm:
            self.vl.task_purge(request, self.admin, task_id)
        # then
        self.assertEqual("Indicated task (id 123) has not been deleted.",
                         cm.exception.description)
        self.ll.purge_task.assert_not_called()
        # and
        self.ll.pl_get_task.assert_called_once_with(task_id)
        self.pl.get_task.assert_not_called()
        self.r.url_for.assert_not_called()
        self.r.redirect.assert_not_called()
