import unittest

from mock import Mock

from logic.layer import LogicLayer
from persistence.in_memory.models.user import User
from persistence.in_memory.layer import InMemoryPersistenceLayer
from tests.util import MockFileObject
from tests.view_t.layer.ViewLayer.util import generate_mock_request
from view.layer import ViewLayer, DefaultRenderer


class ImportTest(unittest.TestCase):
    def setUp(self):
        self.ll = Mock(spec=LogicLayer)
        self.pl = Mock(spec=InMemoryPersistenceLayer)
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)

    def test_imports_data_from_file(self):
        # given
        src = '''{"tasks":[{
            "id": 1,
            "summary":"summary"
        }]}'''
        src_dict = {
            "tasks": [{
                "id": 1,
                "summary": "summary",
            }]
        }
        form = {}
        files = {'file': MockFileObject(filename='', content=src)}
        request = generate_mock_request(form=form, files=files)
        admin = User('admin', is_admin=True)
        # when
        result = self.vl.import_(request, admin)
        # then
        self.ll.do_import_data.assert_called_once_with(src_dict)
        # and
        self.r.url_for.assert_called_once_with('index')
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)

    def test_imports_data_from_form(self):
        # given
        src = '''{"tasks":[{
            "id": 1,
            "summary":"summary"
        }]}'''
        src_dict = {
            "tasks": [{
                "id": 1,
                "summary": "summary",
            }]
        }
        form = {'raw': src}
        files = {}
        request = generate_mock_request(form=form, files=files)
        admin = User('admin', is_admin=True)
        # when
        result = self.vl.import_(request, admin)
        # then
        self.ll.do_import_data.assert_called_once_with(src_dict)
        # and
        self.r.url_for.assert_called_once_with('index')
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)

    def test_get_request_returns_template(self):
        # given
        request = generate_mock_request(method='GET')
        admin = User('admin', is_admin=True)
        # self.r.render_template
        # when
        result = self.vl.import_(request, admin)
        # then
        self.r.render_template.assert_called_once_with('import.t.html')
        self.assertIs(self.r.render_template.return_value, result)
        # and
        self.r.url_for.assert_not_called()
        self.r.redirect.assert_not_called()
