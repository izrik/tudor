import unittest

from unittest.mock import Mock
from werkzeug.exceptions import Forbidden

from logic.layer import LogicLayer
from models.attachment_base import AttachmentBase
from persistence.sqlalchemy.layer import SqlAlchemyPersistenceLayer
from tests.view_t.layer.ViewLayer.util import generate_mock_request
from view.layer import ViewLayer, DefaultRenderer


class AttachmentEditTest(unittest.TestCase):
    def setUp(self):
        self.ll = Mock(spec=LogicLayer)
        self.pl = Mock(spec=SqlAlchemyPersistenceLayer)
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)
        self.user = self.pl.create_user('user@example.org')

    def test_get_renders_the_attachment_from_the_logic_layer(self):
        # given
        attachment = Mock(spec=AttachmentBase)
        attachment.id = 456
        self.ll.get_edit_attachment_data.return_value = {'attachment': attachment}
        request = generate_mock_request(method='GET')
        # when
        result = self.vl.attachment_edit(request, self.user, attachment.id)
        # then
        self.ll.get_edit_attachment_data.assert_called_once_with(
            attachment.id, self.user)
        self.r.render_template.assert_called_once_with(
            'edit_attachment.t.html', attachment=attachment)
        self.assertIs(self.r.render_template.return_value, result)

    def test_get_does_not_render_when_the_user_cannot_edit(self):
        # given
        self.ll.get_edit_attachment_data.side_effect = Forbidden
        request = generate_mock_request(method='GET')
        # expect
        self.assertRaises(
            Forbidden,
            self.vl.attachment_edit, request, self.user, 456)
        # and
        self.r.render_template.assert_not_called()

    def test_post_edits_the_attachment_and_redirects_to_the_task(self):
        # given
        attachment = Mock(spec=AttachmentBase)
        attachment.id = 456
        attachment.task_id = 123
        self.ll.edit_attachment.return_value = attachment
        request = generate_mock_request(method='POST',
                                        form={'description': 'new description'})
        # when
        result = self.vl.attachment_edit(request, self.user, attachment.id)
        # then
        self.ll.edit_attachment.assert_called_once_with(
            attachment.id, 'new description', self.user)
        # and
        self.r.url_for.assert_called_once_with('view_task',
                                               id=attachment.task_id)
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)

    def test_post_can_clear_description(self):
        attachment = self.ll.edit_attachment.return_value
        attachment.task_id = 123
        request = generate_mock_request(method='POST', form={'description': ''})
        self.vl.attachment_edit(request, self.user, 456)
        self.ll.edit_attachment.assert_called_once_with(456, '', self.user)

    def test_post_does_not_redirect_when_forbidden(self):
        self.ll.edit_attachment.side_effect = Forbidden
        request = generate_mock_request(method='POST', form={'description': 'new'})
        with self.assertRaises(Forbidden):
            self.vl.attachment_edit(request, self.user, 456)
        self.r.redirect.assert_not_called()
