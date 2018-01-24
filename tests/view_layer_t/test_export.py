import unittest
from mock import Mock

from in_memory_persistence_layer import InMemoryPersistenceLayer
from logic_layer import LogicLayer
from models.user import User
from tests.view_layer_t.util import generate_mock_request
from view_layer import ViewLayer, DefaultRenderer


class ImportTest(unittest.TestCase):
    def setUp(self):
        self.ll = Mock(spec=LogicLayer)
        self.pl = Mock(spec=InMemoryPersistenceLayer)
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)

    def test_get_yields_template(self):
        # given
        request = generate_mock_request(method='GET')
        admin = User('admin', is_admin=True)
        # when
        result = self.vl.export(request, admin)
        # then
        self.r.render_template.assert_called_once_with('export.t.html',
                                                       results=None)
        self.ll.do_export_data.assert_not_called()
        self.assertNotIsInstance(result, str)
        self.assertNotIsInstance(result, unicode)

    # def test_post_yields_exported_data(self):
    #     # given
    #     request = generate_mock_request(method='POST', form={'tasks':'all'})
    #     admin = User('admin', is_admin=True)
    #     self.r.render_template
    #     # when
    #     result = self.vl.export(request, admin)
    #     # then
    #     self.r.render_template.assert_called_once_with('export.t.html',
    #                                                    results=None)
    #     self.ll.do_export_data.assert_not_called()
    #     self.assertNotIsInstance(result, str)
    #     self.assertNotIsInstance(result, unicode)
