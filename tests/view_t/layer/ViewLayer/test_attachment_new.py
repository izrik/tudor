import unittest

from unittest.mock import Mock
from werkzeug.exceptions import BadRequest

from logic.layer import LogicLayer
from persistence.in_memory.models.task import Task
from persistence.in_memory.layer import InMemoryPersistenceLayer
from tests.util import MockFileObject
from tests.view_t.layer.ViewLayer.util import generate_mock_request
from view.layer import ViewLayer, DefaultRenderer


class AttachmentNewTest(unittest.TestCase):
    def setUp(self):
        self.ll = Mock(spec=LogicLayer)
        self.pl = Mock(spec=InMemoryPersistenceLayer)
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)

    def test_creates_new_attachment(self):
        # given
        task = Mock(spec=Task)
        task.id = 123
        form = {'task_id': task.id}
        f = MockFileObject('/filename.txt')
        files = {'filename': f}
        request = generate_mock_request(form=form, files=files)
        admin = self.pl.create_user('admin', is_admin=True)
        # when
        result = self.vl.attachment_new(request, admin)
        # then
        self.ll.create_new_attachment.assert_called_once_with(
            task.id, f, '', admin, timestamp=None)
        # and
        self.r.url_for.assert_called_once_with('view_task', id=task.id)
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)

    def test_description_none_yields_none(self):
        # given
        task = Mock(spec=Task)
        task.id = 123
        form = {'task_id': task.id,
                'description': None}
        f = MockFileObject('/filename.txt')
        files = {'filename': f}
        request = generate_mock_request(form=form, files=files)
        admin = self.pl.create_user('admin', is_admin=True)
        # when
        result = self.vl.attachment_new(request, admin)
        # then
        self.ll.create_new_attachment.assert_called_once_with(
            task.id, f, None, admin, timestamp=None)
        # and
        self.r.url_for.assert_called_once_with('view_task', id=task.id)
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)

    def test_empty_description_yields_empty_description(self):
        # given
        task = Mock(spec=Task)
        task.id = 123
        form = {'task_id': task.id,
                'description': ''}
        f = MockFileObject('/filename.txt')
        files = {'filename': f}
        request = generate_mock_request(form=form, files=files)
        admin = self.pl.create_user('admin', is_admin=True)
        # when
        result = self.vl.attachment_new(request, admin)
        # then
        self.ll.create_new_attachment.assert_called_once_with(
            task.id, f, '', admin, timestamp=None)
        # and
        self.r.url_for.assert_called_once_with('view_task', id=task.id)
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)

    def test_description_sets_description(self):
        # given
        task = Mock(spec=Task)
        task.id = 123
        form = {'task_id': task.id,
                'description': 'asdf'}
        f = MockFileObject('/filename.txt')
        files = {'filename': f}
        request = generate_mock_request(form=form, files=files)
        admin = self.pl.create_user('admin', is_admin=True)
        # when
        result = self.vl.attachment_new(request, admin)
        # then
        self.ll.create_new_attachment.assert_called_once_with(
            task.id, f, 'asdf', admin, timestamp=None)
        # and
        self.r.url_for.assert_called_once_with('view_task', id=task.id)
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)

    def test_null_file_object_raises(self):
        # given
        task = Mock(spec=Task)
        task.id = 123
        form = {'task_id': task.id,
                'description': 'asdf'}
        files = {'filename': None}
        request = generate_mock_request(form=form, files=files)
        admin = self.pl.create_user('admin', is_admin=True)
        # expect
        self.assertRaises(
            BadRequest,
            self.vl.attachment_new,
            request, admin)
        # and
        self.r.redirect.assert_not_called()

    def test_null_filename_raises(self):
        # given
        task = Mock(spec=Task)
        task.id = 123
        form = {'task_id': task.id,
                'description': 'asdf'}
        files = {'filename': MockFileObject(None)}
        request = generate_mock_request(form=form, files=files)
        admin = self.pl.create_user('admin', is_admin=True)
        # expect
        self.assertRaises(
            BadRequest,
            self.vl.attachment_new,
            request, admin)
        # and
        self.r.redirect.assert_not_called()

    def test_empty_filename_raises(self):
        # given
        task = Mock(spec=Task)
        task.id = 123
        form = {'task_id': task.id,
                'description': 'asdf'}
        files = {'filename': MockFileObject('')}
        request = generate_mock_request(form=form, files=files)
        admin = self.pl.create_user('admin', is_admin=True)
        # expect
        self.assertRaises(
            BadRequest,
            self.vl.attachment_new,
            request, admin)
        # and
        self.r.redirect.assert_not_called()

    def test_extension_not_allowed_raises(self):
        # given
        task = Mock(spec=Task)
        task.id = 123
        form = {'task_id': task.id,
                'description': 'asdf'}
        files = {'filename': MockFileObject('/filename.exe')}
        request = generate_mock_request(form=form, files=files)
        admin = self.pl.create_user('admin', is_admin=True)
        self.ll.allowed_file.return_value = False
        # expect
        self.assertRaises(
            BadRequest,
            self.vl.attachment_new,
            request, admin)
        # and
        self.r.redirect.assert_not_called()

    def test_task_id_not_sepcified_raises(self):
        # given
        task = Mock(spec=Task)
        task.id = 123
        form = {}
        files = {'filename': MockFileObject('/filename.exe')}
        request = generate_mock_request(form=form, files=files)
        admin = self.pl.create_user('admin', is_admin=True)
        # expect
        self.assertRaises(
            BadRequest,
            self.vl.attachment_new,
            request, admin)
        # and
        self.r.redirect.assert_not_called()
