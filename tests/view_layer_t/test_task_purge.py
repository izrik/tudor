import unittest
from mock import Mock
from werkzeug.exceptions import NotFound, BadRequest

from in_memory_persistence_layer import InMemoryPersistenceLayer
from logic_layer import LogicLayer
from models.task import Task
from models.user import User
from tests.view_layer_t.util import generate_mock_request
from tudor import generate_app
from view_layer import ViewLayer, DefaultRenderer


class TaskPurgeTest(unittest.TestCase):
    def setUp(self):
        self.pl = Mock(spec=InMemoryPersistenceLayer)
        self.ll = Mock(spec=LogicLayer)
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, self.pl, renderer=self.r)
        self.app = generate_app(vl=self.vl, ll=self.ll, pl=self.pl,
                                flask_configs={'LOGIN_DISABLED': True,
                                               'SERVER_NAME': 'example.com'},
                                secret_key='12345', disable_admin_check=True)
        self.vl.app = self.app
        self.admin = Mock(spec=User)

    def test_purges_deleted_task(self):
        # given
        task = Mock(spec=Task)
        task.is_deleted = True
        self.pl.get_task.return_value = task
        request = generate_mock_request(method="GET")
        task_id = 123
        # when
        result = self.vl.task_purge(request, self.admin, task_id)
        # then
        self.ll.purge_task.assert_called_once_with(task, self.admin)
        # and
        self.pl.get_task.assert_called_once_with(task_id)
        self.r.url_for.assert_called_once_with('index')
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)

    def test_task_not_found_raises(self):
        # given
        self.pl.get_task.return_value = None
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
        self.pl.get_task.assert_called_once_with(task_id)
        self.r.url_for.assert_not_called()
        self.r.redirect.assert_not_called()

    def test_task_not_deleted_raises(self):
        # given
        task = Mock(spec=Task)
        task.is_deleted = False
        self.pl.get_task.return_value = task
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
        self.pl.get_task.assert_called_once_with(task_id)
        self.r.url_for.assert_not_called()
        self.r.redirect.assert_not_called()
