import unittest
from mock import Mock
from werkzeug.exceptions import BadRequest

from models.task import Task
from models.user import User
from tests.logic_layer_t.util import generate_ll
from tests.util import MockFileObject
from tests.view_layer_t.util import generate_mock_request
from tudor import generate_app
from view_layer import ViewLayer, DefaultRenderer


class AttachmentNewTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, None, renderer=self.r)
        self.app = generate_app(vl=self.vl, ll=self.ll, pl=self.pl,
                                flask_configs={'LOGIN_DISABLED': True,
                                               'SERVER_NAME': 'example.com'},
                                secret_key='12345', disable_admin_check=True)
        self.vl.app = self.app

    def test_creates_new_attachment(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        form = {'task_id': task.id}
        files = {'filename': MockFileObject('/filename.txt')}
        request = generate_mock_request(form=form, files=files)
        admin = User('admin', is_admin=True)
        # precondition
        self.assertEqual(0, len(task.attachments))
        # when
        with self.app.app_context():
            result = self.vl.attachment_new(request, admin)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(1, len(task.attachments))
        att = list(task.attachments)[0]
        self.assertEqual('', att.description)
        self.assertIsNone(att.filename)
        self.assertEqual('filename.txt', att.path)
        self.r.redirect.assert_called()

    def test_description_none_yields_none(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        form = {'task_id': task.id,
                'description': None}
        files = {'filename': MockFileObject('/filename.txt')}
        request = generate_mock_request(form=form, files=files)
        admin = User('admin', is_admin=True)
        # precondition
        self.assertEqual(0, len(task.attachments))
        # when
        with self.app.app_context():
            self.vl.attachment_new(request, admin)
        # then
        self.assertEqual(1, len(task.attachments))
        att = list(task.attachments)[0]
        self.assertIsNone(att.description)
        self.r.redirect.assert_called()

    def test_empty_description_yields_empty_description(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        form = {'task_id': task.id,
                'description': ''}
        files = {'filename': MockFileObject('/filename.txt')}
        request = generate_mock_request(form=form, files=files)
        admin = User('admin', is_admin=True)
        # precondition
        self.assertEqual(0, len(task.attachments))
        # when
        with self.app.app_context():
            self.vl.attachment_new(request, admin)
        # then
        self.assertEqual(1, len(task.attachments))
        att = list(task.attachments)[0]
        self.assertEqual('', att.description)
        self.r.redirect.assert_called()

    def test_description_sets_description(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        form = {'task_id': task.id,
                'description': 'asdf'}
        files = {'filename': MockFileObject('/filename.txt')}
        request = generate_mock_request(form=form, files=files)
        admin = User('admin', is_admin=True)
        # precondition
        self.assertEqual(0, len(task.attachments))
        # when
        with self.app.app_context():
            self.vl.attachment_new(request, admin)
        # then
        self.assertEqual(1, len(task.attachments))
        att = list(task.attachments)[0]
        self.assertEqual('asdf', att.description)
        self.r.redirect.assert_called()

    def test_null_file_object_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        form = {'task_id': task.id,
                'description': 'asdf'}
        files = {'filename': None}
        request = generate_mock_request(form=form, files=files)
        admin = User('admin', is_admin=True)
        # precondition
        self.assertEqual(0, len(task.attachments))
        # expect
        with self.app.app_context():
            self.assertRaises(
                BadRequest,
                self.vl.attachment_new,
                request, admin)
        # and
        self.r.redirect.assert_not_called()

    def test_null_filename_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        form = {'task_id': task.id,
                'description': 'asdf'}
        files = {'filename': MockFileObject(None)}
        request = generate_mock_request(form=form, files=files)
        admin = User('admin', is_admin=True)
        # precondition
        self.assertEqual(0, len(task.attachments))
        # expect
        with self.app.app_context():
            self.assertRaises(
                BadRequest,
                self.vl.attachment_new,
                request, admin)
        # and
        self.r.redirect.assert_not_called()

    def test_empty_filename_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        form = {'task_id': task.id,
                'description': 'asdf'}
        files = {'filename': MockFileObject('')}
        request = generate_mock_request(form=form, files=files)
        admin = User('admin', is_admin=True)
        # precondition
        self.assertEqual(0, len(task.attachments))
        # expect
        with self.app.app_context():
            self.assertRaises(
                BadRequest,
                self.vl.attachment_new,
                request, admin)
        # and
        self.r.redirect.assert_not_called()

    def test_extension_not_allowed_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        form = {'task_id': task.id,
                'description': 'asdf'}
        files = {'filename': MockFileObject('/filename.exe')}
        request = generate_mock_request(form=form, files=files)
        admin = User('admin', is_admin=True)
        # precondition
        self.assertEqual(0, len(task.attachments))
        # expect
        with self.app.app_context():
            self.assertRaises(
                BadRequest,
                self.vl.attachment_new,
                request, admin)
        # and
        self.r.redirect.assert_not_called()

    def test_task_id_not_sepcified_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        form = {}
        files = {'filename': MockFileObject('/filename.exe')}
        request = generate_mock_request(form=form, files=files)
        admin = User('admin', is_admin=True)
        # precondition
        self.assertEqual(0, len(task.attachments))
        # expect
        with self.app.app_context():
            self.assertRaises(
                BadRequest,
                self.vl.attachment_new,
                request, admin)
        # and
        self.r.redirect.assert_not_called()
