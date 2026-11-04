import unittest
from datetime import datetime

from werkzeug.exceptions import Forbidden, NotFound

from .util import generate_ll


class EditAttachmentTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.user = self.pl.create_user('editor@example.org')
        self.task = self.pl.create_task('task', is_public=True)
        self.task.users.append(self.user)
        self.attachment = self.pl.create_attachment(
            'file.txt', 'original', timestamp=datetime(2020, 1, 1),
            filename='file.txt')
        self.attachment.task = self.task
        self.pl.save(self.user, self.task, self.attachment)

    def test_description_is_persisted_and_other_fields_are_unchanged(self):
        original = self.attachment.to_flat_dict()
        aid = self.attachment.id
        self.ll.edit_attachment(aid, 'updated <description>\nsecond line', self.user)
        self.pl.db.session.expire_all()
        expected = dict(original, description='updated <description>\nsecond line')
        self.assertEqual(expected, self.pl.get_attachment(aid).to_flat_dict())

    def test_description_can_be_cleared(self):
        self.ll.edit_attachment(self.attachment.id, '', self.user)
        self.pl.db.session.expire_all()
        self.assertEqual('', self.pl.get_attachment(self.attachment.id).description)

    def test_admin_can_edit(self):
        admin = self.pl.create_user('admin@example.org', is_admin=True)
        self.pl.save(admin)
        self.ll.edit_attachment(self.attachment.id, 'admin edit', admin)
        self.assertEqual('admin edit', self.attachment.description)

    def test_get_returns_attachment(self):
        self.assertEqual({'attachment': self.attachment},
                         self.ll.get_edit_attachment_data(
                             self.attachment.id, self.user))

    def test_missing_attachment_is_not_found_for_get_and_post(self):
        with self.assertRaises(NotFound):
            self.ll.get_edit_attachment_data(self.attachment.id + 1, self.user)
        with self.assertRaises(NotFound):
            self.ll.edit_attachment(self.attachment.id + 1, 'edit', self.user)

    def test_public_task_does_not_allow_unauthorized_edits(self):
        other = self.pl.create_user('other@example.org')
        self.pl.save(other)
        for user in (None, other):
            with self.subTest(user=str(user)):
                with self.assertRaises(Forbidden):
                    self.ll.get_edit_attachment_data(self.attachment.id, user)
                with self.assertRaises(Forbidden):
                    self.ll.edit_attachment(self.attachment.id, 'edit', user)
                self.assertEqual('original', self.attachment.description)

    def test_detached_attachment_is_not_found(self):
        self.attachment.task = None
        self.pl.save(self.attachment)
        with self.assertRaises(NotFound):
            self.ll.edit_attachment(self.attachment.id, 'edit', self.user)
