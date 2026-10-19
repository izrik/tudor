import unittest

from unittest.mock import Mock
from werkzeug.exceptions import Forbidden

from logic.layer import LogicLayer
from models.comment_base import CommentBase
from persistence.sqlalchemy.layer import SqlAlchemyPersistenceLayer
from tests.view_t.layer.ViewLayer.util import generate_mock_request
from view.layer import ViewLayer, DefaultRenderer


class CommentEditTest(unittest.TestCase):
    def setUp(self):
        self.ll = Mock(spec=LogicLayer)
        self.pl = Mock(spec=SqlAlchemyPersistenceLayer)
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)
        self.user = self.pl.create_user('user@example.org')

    def test_get_renders_the_comment_from_the_logic_layer(self):
        # given
        comment = Mock(spec=CommentBase)
        comment.id = 456
        self.ll.get_edit_comment_data.return_value = {'comment': comment}
        request = generate_mock_request(method='GET')
        # when
        result = self.vl.comment_edit(request, self.user, comment.id)
        # then
        self.ll.get_edit_comment_data.assert_called_once_with(
            comment.id, self.user)
        self.r.render_template.assert_called_once_with(
            'edit_comment.t.html', comment=comment)
        self.assertIs(self.r.render_template.return_value, result)

    def test_get_does_not_render_when_the_user_cannot_edit(self):
        # given
        self.ll.get_edit_comment_data.side_effect = Forbidden
        request = generate_mock_request(method='GET')
        # expect
        self.assertRaises(
            Forbidden,
            self.vl.comment_edit, request, self.user, 456)
        # and
        self.r.render_template.assert_not_called()

    def test_post_edits_the_comment_and_redirects_to_the_task(self):
        # given
        comment = Mock(spec=CommentBase)
        comment.id = 456
        comment.task_id = 123
        self.ll.edit_comment.return_value = comment
        request = generate_mock_request(method='POST',
                                        form={'content': 'new content'})
        # when
        result = self.vl.comment_edit(request, self.user, comment.id)
        # then
        self.ll.edit_comment.assert_called_once_with(
            comment.id, 'new content', self.user)
        # and
        self.r.url_for.assert_called_once_with('view_task',
                                               id=comment.task_id)
        self.r.redirect.assert_called_once_with(self.r.url_for.return_value)
        self.assertIs(self.r.redirect.return_value, result)
