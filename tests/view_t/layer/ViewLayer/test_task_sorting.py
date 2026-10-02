import itertools
import unittest

from unittest.mock import Mock

from flask import render_template

from logic.layer import LogicLayer
from tests.util import generate_test_app
from tests.view_t.layer.ViewLayer.util import generate_mock_request
from view.layer import ViewLayer, DefaultRenderer


def echo_sort(**data):
    def get_data(*args, **kwargs):
        return dict(data, sort=kwargs['sort'], order=kwargs['order'])
    return get_data


class TaskSortingViewTest(unittest.TestCase):
    def setUp(self):
        self.ll = Mock(spec=LogicLayer)
        self.ll.get_index_data = Mock(side_effect=echo_sort(
            show_deleted=None, show_done=None, tasks=[], all_tags=[],
            pager=None))
        self.ll.get_deadlines_data = Mock(side_effect=echo_sort(
            deadline_tasks=[]))
        self.ll.get_tag_data = Mock(side_effect=echo_sort(tag=None, tasks=[]))
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)
        self.user = Mock()

    def request(self, args):
        return generate_mock_request(method='GET', args=args, cookies={})

    def test_index_defaults(self):
        # when
        self.vl.index(self.request({}), self.user)
        # then
        kwargs = self.ll.get_index_data.call_args.kwargs
        self.assertEqual('order_num', kwargs['sort'])
        self.assertEqual('desc', kwargs['order'])
        kwargs = self.r.render_template.call_args.kwargs
        self.assertEqual('order_num', kwargs['sort'])
        self.assertEqual('desc', kwargs['order'])
        self.assertEqual('index', kwargs['sort_link_page'])
        self.assertEqual({}, kwargs['sort_link_args'])
        self.assertEqual({'sort': 'order_num', 'order': 'desc'},
                         kwargs['pager_link_args'])

    def test_index_passes_query_params(self):
        # when
        self.vl.index(self.request({'sort': 'summary', 'order': 'asc'}),
                      self.user)
        # then
        kwargs = self.ll.get_index_data.call_args.kwargs
        self.assertEqual('summary', kwargs['sort'])
        self.assertEqual('asc', kwargs['order'])
        kwargs = self.r.render_template.call_args.kwargs
        self.assertEqual({'sort': 'summary', 'order': 'asc'},
                         kwargs['pager_link_args'])

    def test_index_invalid_query_params_use_defaults(self):
        # when
        self.vl.index(self.request({'sort': 'bogus', 'order': 'sideways'}),
                      self.user)
        # then
        kwargs = self.ll.get_index_data.call_args.kwargs
        self.assertEqual('order_num', kwargs['sort'])
        self.assertEqual('desc', kwargs['order'])

    def test_deadlines(self):
        # when
        self.vl.deadlines(self.request({'sort': 'id', 'order': 'desc'}),
                          self.user)
        # then
        self.ll.get_deadlines_data.assert_called_with(
            self.user, sort='id', order='desc')
        kwargs = self.r.render_template.call_args.kwargs
        self.assertEqual('deadlines', kwargs['sort_link_page'])
        self.assertEqual({}, kwargs['sort_link_args'])

    def test_deadlines_default_to_deadline_ascending(self):
        # when
        self.vl.deadlines(self.request({}), self.user)
        # then
        self.ll.get_deadlines_data.assert_called_with(
            self.user, sort='deadline', order='asc')

    def test_tag(self):
        # when
        self.vl.tags_id_get(self.request({'sort': 'deadline'}), self.user, 5)
        # then
        self.ll.get_tag_data.assert_called_with(
            5, self.user, sort='deadline', order='desc')
        kwargs = self.r.render_template.call_args.kwargs
        self.assertEqual('view_tag', kwargs['sort_link_page'])
        self.assertEqual({'id': 5}, kwargs['sort_link_args'])


class TaskTableSortHeaderTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_test_app()
        self.pl = self.app.pl
        self.ll = self.app.ll
        self.tag = self.pl.create_tag('tag')
        self.pl.add(self.tag)
        task = self.pl.create_task('task')
        task.tags.append(self.tag)
        self.pl.add(task)
        self.pl.commit()

    def render_tag(self, sort, order):
        data = self.ll.get_tag_data(self.tag.id, None, sort=sort, order=order)
        with self.app.test_request_context('/tags/{}'.format(self.tag.id)):
            return render_template(
                'tag.t.html', tag=data['tag'], tasks=data['tasks'],
                cycle=itertools.cycle, sort=data['sort'],
                order=data['order'], sort_link_page='view_tag',
                sort_link_args={'id': self.tag.id})

    def test_header_links_toggle_sort(self):
        # when
        html = self.render_tag('summary', 'asc')
        # then
        self.assertIn('href="/tags/{}?sort=summary&amp;order=desc"'.format(
            self.tag.id), html)
        self.assertIn('href="/tags/{}?sort=id&amp;order=asc"'.format(
            self.tag.id), html)
        self.assertIn('href="/tags/{}?sort=deadline&amp;order=asc"'.format(
            self.tag.id), html)
        self.assertIn('glyphicon-triangle-top', html)
        self.assertNotIn('glyphicon-triangle-bottom', html)

    def test_descending_sort_shows_down_arrow(self):
        # when
        html = self.render_tag('id', 'desc')
        # then
        self.assertIn('href="/tags/{}?sort=id&amp;order=asc"'.format(
            self.tag.id), html)
        self.assertIn('glyphicon-triangle-bottom', html)

    def test_plain_headers_without_sort_link_page(self):
        # given
        with self.app.test_request_context('/hierarchy'):
            # when
            html = render_template(
                'hierarchy.t.html', tasks_h=[], cycle=itertools.cycle,
                show_deleted=False, show_done=False, user=Mock(),
                tags=[])
        # then
        self.assertIn('<th>ID</th>', html)
        self.assertIn('<th>Summary</th>', html)
        self.assertNotIn('sort=', html)
