import unittest
from mock import Mock

from in_memory_persistence_layer import InMemoryPersistenceLayer
from logic_layer import LogicLayer
from models.user import User
from tests.view_layer_t.util import generate_mock_request
from view_layer import ViewLayer, DefaultRenderer, DefaultLoginSource


class LogoutTest(unittest.TestCase):
    def setUp(self):
        self.pl = Mock(spec=InMemoryPersistenceLayer)
        self.ll = Mock(spec=LogicLayer)
        self.r = Mock(spec=DefaultRenderer)
        self.ls = Mock(spec=DefaultLoginSource)
        self.vl = ViewLayer(self.ll, None, renderer=self.r,
                            login_src=self.ls)
        self.admin = Mock(spec=User)

    def test_logs_out_user(self):
        # given
        request = generate_mock_request(method="GET")
        # when
        result = self.vl.logout(request, self.admin)
        # then
        self.ls.logout_user.assert_called_once_with()
        # and
        self.r.url_for.assert_called_once_with('index')
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)

    def test_post_also_logs_out_user(self):
        # given
        request = generate_mock_request(method="POST")
        # when
        result = self.vl.logout(request, self.admin)
        # then
        self.ls.logout_user.assert_called_once_with()
        # and
        self.r.url_for.assert_called_once_with('index')
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)
