import unittest
from mock import Mock

from models.user import User
from tests.logic_layer_t.util import generate_ll
from tests.util import MockFileObject
from tests.view_layer_t.util import generate_mock_request
from tudor import generate_app
from view_layer import ViewLayer, DefaultRenderer


class ImportTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)
        self.app = generate_app(vl=self.vl, ll=self.ll, pl=self.pl,
                                flask_configs={'LOGIN_DISABLED': True,
                                               'SERVER_NAME': 'example.com'},
                                secret_key='12345', disable_admin_check=True)
        self.vl.app = self.app

    def test_imports_data_from_file(self):
        # given
        src = '''{"tasks":[{
            "id": 1,
            "summary":"summary"
        }]}'''
        form = {}
        files = {'file': MockFileObject(filename='', content=src)}
        request = generate_mock_request(form=form, files=files)
        admin = User('admin', is_admin=True)
        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        # when
        with self.app.app_context():
            result = self.vl.import_(request, admin)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(1, self.pl.count_tasks())
        self.r.redirect.assert_called()
        self.r.render_template.assert_not_called()

    def test_imports_data_from_form(self):
        # given
        src = '''{"tasks":[{
            "id": 1,
            "summary":"summary"
        }]}'''
        form = {'raw': src}
        files = {}
        request = generate_mock_request(form=form, files=files)
        admin = User('admin', is_admin=True)
        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        # when
        with self.app.app_context():
            result = self.vl.import_(request, admin)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(1, self.pl.count_tasks())
        self.r.redirect.assert_called()
        self.r.render_template.assert_not_called()

    def test_get_request_returns_content(self):
        # given
        request = generate_mock_request(method='GET')
        admin = User('admin', is_admin=True)
        # self.r.render_template
        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        # when
        with self.app.app_context():
            result = self.vl.import_(request, admin)
        # then
        self.assertIsNotNone(result)
        self.r.render_template.assert_called()
        self.assertEqual(0, self.pl.count_tasks())
        self.r.redirect.assert_not_called()
        self.r.render_template.assert_called()
