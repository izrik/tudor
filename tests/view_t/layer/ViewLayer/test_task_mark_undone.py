
import unittest

from mock import Mock

from logic.layer import LogicLayer
from persistence.in_memory.models.user import User
from persistence.in_memory.layer import InMemoryPersistenceLayer
from tests.view_t.layer.ViewLayer.util import generate_mock_request
from view.layer import ViewLayer, DefaultRenderer


class TaskMarkUndoneTest(unittest.TestCase):
    def setUp(self):
        self.pl = Mock(spec=InMemoryPersistenceLayer)
        self.ll = Mock(spec=LogicLayer)
        self.ll.task_unset_done = Mock()
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)

    def test_sets_is_undone(self):
        # given
        task_id = 1
        user = User('admin@example.com', is_admin=True)
        req = generate_mock_request(method='GET', args={})
        self.r.url_for.return_value = 'http://example.com/'
        # when
        self.vl.task_mark_undone(req, current_user=user, task_id=task_id)
        # then
        self.ll.task_unset_done.assert_called_once_with(task_id, user)
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
        self.vl.task_mark_undone(req, current_user=user, task_id=task_id)
        # then
        self.ll.task_unset_done.assert_called_once_with(task_id, user)
        self.r.url_for.assert_not_called()
        self.r.redirect.assert_called_once_with('http://example2.org/')  #
