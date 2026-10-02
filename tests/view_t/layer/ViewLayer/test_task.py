
import itertools
import unittest

from unittest.mock import Mock

from flask import render_template

from logic.layer import LogicLayer
from models.task_user_ops import TaskUserOps
from tests.util import generate_test_app
from tests.view_t.layer.ViewLayer.util import generate_mock_request
from view.layer import ViewLayer, DefaultRenderer


class TaskTest(unittest.TestCase):
    def setUp(self):
        self.ll = Mock(spec=LogicLayer)
        self.return_value = {
            'task': None,
            'descendants': [],
            'pager': None,
            'sort': 'order_num',
            'order': 'desc',
        }
        self.ll.get_task_data = Mock(return_value=self.return_value)
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)

    def test_gets_task_data_from_logic_layer(self):
        # given
        request = generate_mock_request(args={}, cookies={})
        user = Mock()
        TASK_ID = 1
        # when
        result = self.vl.task(request, user, TASK_ID)
        # then
        self.assertIsNotNone(result)
        self.ll.get_task_data.assert_called_with(TASK_ID, user,
                                                 include_deleted=None,
                                                 include_done=None,
                                                 page_num=1, tasks_per_page=20,
                                                 sort='order_num', order='desc')
        self.r.render_template.assert_called()

    def test_page_num_not_int_defaults_to_one(self):
        # given
        request = generate_mock_request(args={'page': 'asdf'}, cookies={})
        user = Mock()
        TASK_ID = 1
        # when
        result = self.vl.task(request, user, TASK_ID)
        # then
        self.assertIsNotNone(result)
        self.ll.get_task_data.assert_called_with(TASK_ID, user,
                                                 include_deleted=None,
                                                 include_done=None,
                                                 page_num=1, tasks_per_page=20,
                                                 sort='order_num', order='desc')
        self.r.render_template.assert_called()

    def test_task_per_page_not_int_default_to_twenty(self):
        # given
        request = generate_mock_request(args={'per_page': 'asdf'}, cookies={})
        user = Mock()
        TASK_ID = 1
        # when
        result = self.vl.task(request, user, TASK_ID)
        # then
        self.assertIsNotNone(result)
        self.ll.get_task_data.assert_called_with(TASK_ID, user,
                                                 include_deleted=None,
                                                 include_done=None,
                                                 page_num=1, tasks_per_page=20,
                                                 sort='order_num', order='desc')
        self.r.render_template.assert_called()


class TaskTemplateTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_test_app()
        self.pl = self.app.pl
        self.ll = self.app.ll
        self.admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(self.admin)
        self.task = self.pl.create_task('the summary',
                                        description='the description')
        self.pl.add(self.task)
        self.pl.commit()

    def render(self):
        data = self.ll.get_task_data(self.task.id, self.admin)
        with self.app.test_request_context('/task/{}'.format(self.task.id)):
            return render_template(
                'task.t.html', task=data['task'],
                descendants=data['descendants'], cycle=itertools.cycle,
                show_deleted=False, show_done=False, pager=data['pager'],
                pager_link_page='view_task',
                pager_link_args={'id': self.task.id},
                current_user=self.admin, ops=TaskUserOps,
                show_hierarchy=False)

    def test_shows_tag_chips_between_summary_and_description(self):
        # given
        tag1 = self.pl.create_tag('tag1')
        self.pl.add(tag1)
        tag2 = self.pl.create_tag('tag2')
        self.pl.add(tag2)
        self.pl.commit()
        self.pl.add_tag_to_task(self.task.id, tag1.id)
        self.pl.add_tag_to_task(self.task.id, tag2.id)
        # when
        html = self.render()
        # then
        chip1 = ('<a class="label label-info tag_chip" href="/tags/{}">'
                 'tag1</a>'.format(tag1.id))
        chip2 = ('<a class="label label-info tag_chip" href="/tags/{}">'
                 'tag2</a>'.format(tag2.id))
        self.assertIn(chip1, html)
        self.assertIn(chip2, html)
        summary_pos = html.index('the summary</h1>')
        description_pos = html.index('the description')
        self.assertLess(summary_pos, html.index(chip1))
        self.assertLess(html.index(chip1), description_pos)
        self.assertLess(html.index(chip2), description_pos)

    def test_no_tag_chips_without_tags(self):
        # when
        html = self.render()
        # then
        self.assertNotIn('<div class="tag_chips">', html)
