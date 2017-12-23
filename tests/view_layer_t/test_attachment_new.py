import unittest
from mock import Mock
from werkzeug.exceptions import BadRequest

from models.task import Task
from models.user import User
from tests.logic_layer_t.util import generate_ll
from tests.util import MockFileObject
from tests.view_layer_t.util import generate_mock_request
from view_layer import ViewLayer, DefaultRenderer


class AttachmentNewTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)

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
        self.assertRaises(
            BadRequest,
            self.vl.attachment_new,
            request, admin)
        # and
        self.r.redirect.assert_not_called()
