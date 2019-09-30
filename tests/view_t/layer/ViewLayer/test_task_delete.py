
import unittest

from unittest.mock import Mock

from logic.layer import LogicLayer
from persistence.in_memory.layer import InMemoryPersistenceLayer
from tests.view_t.layer.ViewLayer.util import generate_mock_request
from view.layer import ViewLayer, DefaultRenderer


class TaskDeleteTest(unittest.TestCase):
    def setUp(self):
        self.pl = Mock(spec=InMemoryPersistenceLayer)
        self.ll = Mock(spec=LogicLayer)
        self.ll.task_set_deleted = Mock()
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)

    def test_sets_is_deleted(self):
        # given
        task_id = 1
        user = self.pl.create_user('admin@example.com', is_admin=True)
        req = generate_mock_request(method='GET', args={})
        self.r.url_for.return_value = 'http://example.com/'
        # when
        self.vl.task_delete(req, current_user=user, task_id=task_id)
        # then
        self.ll.task_set_deleted.assert_called_once_with(task_id, user)
        self.r.url_for.assert_called_once_with('index')
        self.r.redirect.assert_called_once_with('http://example.com/')

    def test_takes_redirect_url_from_args_next_if_available(self):
        # given
        task_id = 1
        user = self.pl.create_user('admin@example.com', is_admin=True)
        req = generate_mock_request(method='GET',
                                    args={'next': 'http://example2.org/'})
        self.r.url_for.return_value = 'http://example.com/'
        # when
        self.vl.task_delete(req, current_user=user, task_id=task_id)
        # then
        self.ll.task_set_deleted.assert_called_once_with(task_id, user)
        self.r.url_for.assert_not_called()
        self.r.redirect.assert_called_once_with('http://example2.org/')  #
