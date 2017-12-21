
import unittest
from mock import Mock

from in_memory_persistence_layer import InMemoryPersistenceLayer
from models.user import User
from tests.view_layer_t.util import generate_mock_request
from tudor import generate_app
from view_layer import ViewLayer, DefaultRenderer
from logic_layer import LogicLayer


class TaskUndeleteTest(unittest.TestCase):
    def setUp(self):
        self.pl = Mock(spec=InMemoryPersistenceLayer)
        self.ll = Mock(spec=LogicLayer)
        self.ll.task_unset_deleted = Mock()
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, self.pl, renderer=self.r)
        self.app = generate_app(vl=self.vl, ll=self.ll, pl=self.pl,
                                flask_configs={'LOGIN_DISABLED': True},
                                secret_key='12345', disable_admin_check=True)
        self.vl.app = self.app

    def test_unsets_is_deleted(self):
        # given
        task_id = 1
        user = User('admin@example.com', is_admin=True)
        req = generate_mock_request(method='GET', args={})
        self.r.url_for.return_value = 'http://example.com/'
        # when
        self.vl.task_undelete(req, current_user=user, task_id=task_id)
        # then
        self.ll.task_unset_deleted.assert_called_once_with(task_id, user)
        self.r.url_for.assert_called_once_with('index')
        self.r.redirect.assert_called_once_with('http://example.com/')

    def test_takes_redirect_url_from_args_next_if_available(self):
        # given
        task_id = 1
        user = User('admin@example.com', is_admin=True)
        req = generate_mock_request(method='GET',
                                    args={'next': 'http://example2.org/'})
        self.r.url_for.return_value = 'http://example.com/'
        # when
        self.vl.task_undelete(req, current_user=user, task_id=task_id)
        # then
        self.ll.task_unset_deleted.assert_called_once_with(task_id, user)
        self.r.url_for.assert_not_called()
        self.r.redirect.assert_called_once_with('http://example2.org/')  #
