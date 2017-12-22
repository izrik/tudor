import unittest
from mock import Mock

from in_memory_persistence_layer import InMemoryPersistenceLayer
from logic_layer import LogicLayer
from models.user import User
from tests.view_layer_t.util import generate_mock_request
from tudor import generate_app
from view_layer import ViewLayer, DefaultRenderer, DefaultLoginSource


class LoginTest(unittest.TestCase):
    def setUp(self):
        self.pl = Mock(spec=InMemoryPersistenceLayer)
        self.ll = Mock(spec=LogicLayer)
        self.r = Mock(spec=DefaultRenderer)
        self.ls = Mock(spec=DefaultLoginSource)
        self.vl = ViewLayer(self.ll, None, renderer=self.r,
                            login_src=self.ls)
        self.app = generate_app(vl=self.vl, ll=self.ll, pl=self.pl,
                                flask_configs={'LOGIN_DISABLED': True,
                                               'SERVER_NAME': 'example.com'},
                                secret_key='12345', disable_admin_check=True)
        self.vl.app = self.app
        self.admin = Mock(spec=User)

    def test_renders_template_on_get(self):
        # given
        request = generate_mock_request(method="GET")
        # when
        result = self.vl.login(request, self.admin)
        # then
        self.r.render_template.assert_called_once_with('login.t.html')
        self.ls.login_user.assert_not_called()
        self.assertIs(self.r.render_template.return_value, result)
        # and
        self.ll.pl_get_user_by_email.assert_not_called()
        self.pl.get_user_by_email.assert_not_called()
        self.r.flash.assert_not_called()
        self.r.redirect.assert_not_called()
        self.r.url_for.assert_not_called()

    def test_logs_in_user(self):
        # given
        email = 'name@example.com'
        password = '12345'
        hashed_password = 'hashhashhash'
        user = Mock(spec=User)
        user.email = email
        user.hashed_password = hashed_password
        self.ls.check_password_hash.return_value = True
        self.ll.pl_get_user_by_email.return_value = user
        request = generate_mock_request(method="POST",
                                        form={'email': email,
                                              'password': password})
        # when
        result = self.vl.login(request, self.admin)
        # then
        self.ls.login_user.assert_called_once_with(user)
        self.r.url_for.assert_called_once_with('index')
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)
        # and
        self.r.flash.assert_called_once_with('Logged in successfully')
        self.ll.pl_get_user_by_email.assert_called_once_with(email)
        self.pl.get_user_by_email.assert_not_called()
        self.ls.check_password_hash.assert_called_once_with(hashed_password,
                                                            password)
        self.r.render_template.assert_not_called()

    def test_email_not_found_redirects(self):
        # given
        email = 'name@example.com'
        password = '12345'
        self.ls.check_password_hash.return_value = True
        self.ll.pl_get_user_by_email.return_value = None  #
        request = generate_mock_request(method="POST",
                                        form={'email': email,
                                              'password': password})
        # when
        result = self.vl.login(request, self.admin)
        # then
        self.ls.login_user.assert_not_called()
        self.ll.pl_get_user_by_email.assert_called_once_with(email)
        self.pl.get_user_by_email.assert_not_called()
        self.r.flash.assert_called_once_with('Username or Password is invalid',
                                             'error')
        self.r.url_for.assert_called_once_with('login')
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)
        # and
        self.ls.check_password_hash.assert_not_called()
        self.r.render_template.assert_not_called()

    def test_hashed_password_none_redirects(self):
        # given
        email = 'name@example.com'
        password = '12345'
        hashed_password = None  #
        user = Mock(spec=User)
        user.email = email
        user.hashed_password = hashed_password
        self.ls.check_password_hash.return_value = True
        self.ll.pl_get_user_by_email.return_value = user
        request = generate_mock_request(method="POST",
                                        form={'email': email,
                                              'password': password})
        # when
        result = self.vl.login(request, self.admin)
        # then
        self.ls.login_user.assert_not_called()
        self.ll.pl_get_user_by_email.assert_called_once_with(email)
        self.pl.get_user_by_email.assert_not_called()
        self.r.flash.assert_called_once_with('Username or Password is invalid',
                                             'error')
        self.r.url_for.assert_called_once_with('login')
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)
        # and
        self.ls.check_password_hash.assert_not_called()
        self.r.render_template.assert_not_called()

    def test_hashed_password_empty_redirects(self):
        # given
        email = 'name@example.com'
        password = '12345'
        hashed_password = ''  #
        user = Mock(spec=User)
        user.email = email
        user.hashed_password = hashed_password
        self.ls.check_password_hash.return_value = True
        self.ll.pl_get_user_by_email.return_value = user
        request = generate_mock_request(method="POST",
                                        form={'email': email,
                                              'password': password})
        # when
        result = self.vl.login(request, self.admin)
        # then
        self.ls.login_user.assert_not_called()
        self.ll.pl_get_user_by_email.assert_called_once_with(email)
        self.pl.get_user_by_email.assert_not_called()
        self.r.flash.assert_called_once_with('Username or Password is invalid',
                                             'error')
        self.r.url_for.assert_called_once_with('login')
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)
        # and
        self.ls.check_password_hash.assert_not_called()
        self.r.render_template.assert_not_called()

    def test_hashed_password_does_not_match_redirects(self):
        # given
        email = 'name@example.com'
        password = '12345'
        hashed_password = 'hashhashhash'
        user = Mock(spec=User)
        user.email = email
        user.hashed_password = hashed_password
        self.ls.check_password_hash.return_value = False  #
        self.ll.pl_get_user_by_email.return_value = user
        request = generate_mock_request(method="POST",
                                        form={'email': email,
                                              'password': password})
        # when
        result = self.vl.login(request, self.admin)
        # then
        self.ls.login_user.assert_not_called()
        self.ll.pl_get_user_by_email.assert_called_once_with(email)
        self.pl.get_user_by_email.assert_not_called()
        self.r.flash.assert_called_once_with('Username or Password is invalid',
                                             'error')
        self.r.url_for.assert_called_once_with('login')
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)
        self.ls.check_password_hash.assert_called_once_with(hashed_password,
                                                            password)
        # and
        self.r.render_template.assert_not_called()
