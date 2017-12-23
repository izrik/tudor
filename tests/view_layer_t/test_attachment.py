import unittest
from mock import Mock
from werkzeug.exceptions import NotFound

from in_memory_persistence_layer import InMemoryPersistenceLayer
from logic_layer import LogicLayer
from models.attachment import Attachment
from models.user import User
from tests.view_layer_t.util import generate_mock_request
from tudor import generate_app
from view_layer import ViewLayer, DefaultRenderer


class AttachmentTest(unittest.TestCase):
    def setUp(self):
        self.pl = Mock(spec=InMemoryPersistenceLayer)
        self.ll = Mock(spec=LogicLayer)
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, None, renderer=self.r)
        self.app = generate_app(vl=self.vl, ll=self.ll, pl=self.pl,
                                flask_configs={'LOGIN_DISABLED': True,
                                               'SERVER_NAME': 'example.com'},
                                secret_key='12345', disable_admin_check=True)
        self.vl.app = self.app
        self.admin = Mock(spec=User)

    def test_gets_attachment(self):
        # given
        upload_folder = '/path/to/uploads'
        self.ll.upload_folder = upload_folder
        attachment_id = 123
        attachment_path = 'this/is/the/path'
        attachment = Mock(spec=Attachment)
        attachment.id = attachment_id
        attachment.path = attachment_path
        self.ll.pl_get_attachment.return_value = attachment
        request = generate_mock_request(method="GET")
        # when
        result = self.vl.attachment(request, self.admin, attachment_id, 'name')
        # then
        self.r.send_from_directory.assert_called_once_with(upload_folder,
                                                           attachment_path)
        # and
        self.ll.pl_get_attachment.assert_called_once_with(attachment_id)
        self.pl.get_attachment.assert_not_called()
        self.assertIs(self.r.send_from_directory.return_value, result)

    def test_attachment_not_found_raises(self):
        # given
        self.ll.pl_get_attachment.return_value = None
        request = generate_mock_request(method="GET")
        attachment_id = 123
        # expect
        with self.assertRaises(NotFound) as cm:
            self.vl.attachment(request, self.admin, attachment_id, 'name')
        # then
        self.assertEqual("No attachment found for the id '123'",
                         cm.exception.description)
        self.r.send_from_directory.assert_not_called()
        # and
        self.ll.pl_get_attachment.assert_called_once_with(attachment_id)
        self.pl.get_attachment.assert_not_called()
