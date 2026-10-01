import unittest

from unittest.mock import Mock

from flask import render_template

from logic.layer import LogicLayer
from tests.util import generate_test_app
from tests.view_t.layer.ViewLayer.util import generate_mock_request
from view.layer import ViewLayer, DefaultRenderer


class TagsTest(unittest.TestCase):
    def setUp(self):
        self.ll = Mock(spec=LogicLayer)
        self.pager = Mock()
        self.ll.get_tags_data = Mock(side_effect=lambda **kw: {
            'pager': self.pager, 'sort': kw['sort'], 'order': kw['order'],
            'task_counts': self.task_counts})
        self.task_counts = {}
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)

    def call(self, args):
        request = generate_mock_request(method='GET', args=args)
        self.user = Mock()
        return self.vl.tags(request, self.user)

    def test_defaults(self):
        # when
        self.call({})
        # then
        self.ll.get_tags_data.assert_called_with(
            current_user=self.user, page_num=1, tags_per_page=20,
            sort='name', order='asc')
        kwargs = self.r.render_template.call_args.kwargs
        self.assertIs(self.pager, kwargs['pager'])
        self.assertIs(self.task_counts, kwargs['task_counts'])
        self.assertEqual('name', kwargs['sort'])
        self.assertEqual('asc', kwargs['order'])
        self.assertEqual('list_tags', kwargs['pager_link_page'])
        self.assertEqual({'sort': 'name', 'order': 'asc'},
                         kwargs['pager_link_args'])

    def test_passes_query_params(self):
        # when
        self.call({'page': '3', 'per_page': '5', 'sort': 'id',
                   'order': 'desc'})
        # then
        self.ll.get_tags_data.assert_called_with(
            current_user=self.user, page_num=3, tags_per_page=5,
            sort='id', order='desc')

    def test_invalid_query_params_use_defaults(self):
        # when
        self.call({'page': 'x', 'per_page': 'y', 'sort': 'bogus',
                   'order': 'sideways'})
        # then
        self.ll.get_tags_data.assert_called_with(
            current_user=self.user, page_num=1, tags_per_page=20,
            sort='name', order='asc')

    def test_non_positive_numbers_use_defaults(self):
        # when
        self.call({'page': '0', 'per_page': '-1'})
        # then
        self.ll.get_tags_data.assert_called_with(
            current_user=self.user, page_num=1, tags_per_page=20,
            sort='name', order='asc')


class ListTagsTemplateTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_test_app()
        self.pl = self.app.pl
        self.ll = self.app.ll

    def render(self, **kwargs):
        data = self.ll.get_tags_data(**kwargs)
        with self.app.test_request_context('/tags'):
            return render_template(
                'list_tags.t.html', pager=data['pager'],
                task_counts=data['task_counts'], sort=data['sort'],
                order=data['order'], pager_link_page='list_tags',
                pager_link_args={'sort': data['sort'],
                                 'order': data['order']},
                cycle=__import__('itertools').cycle)

    def test_shows_description_excerpt(self):
        # given
        tag1 = self.pl.create_tag('tag1', description='x' * 150)
        self.pl.add(tag1)
        tag2 = self.pl.create_tag('tag2', description='short desc')
        self.pl.add(tag2)
        tag3 = self.pl.create_tag('tag3')
        self.pl.add(tag3)
        self.pl.commit()
        # when
        html = self.render()
        # then
        self.assertIn('<th>Description</th>', html)
        self.assertIn('x' * 99 + '…', html)
        self.assertNotIn('x' * 100, html)
        self.assertIn('short desc', html)
        self.assertIn('<td></td>', html)
        self.assertNotIn('None', html)

    def test_header_links_toggle_sort(self):
        # given
        tag = self.pl.create_tag('tag1')
        self.pl.add(tag)
        self.pl.commit()
        # when
        html = self.render(sort='name', order='asc')
        # then
        self.assertIn('sort=name&amp;order=desc', html)
        self.assertIn('sort=id&amp;order=asc', html)
        self.assertIn('glyphicon-triangle-top', html)

    def test_page_links_shown_when_multiple_pages(self):
        # given
        for i in range(3):
            self.pl.add(self.pl.create_tag('tag{}'.format(i)))
        self.pl.commit()
        # when
        html = self.render(tags_per_page=2, sort='id', order='desc')
        # then
        self.assertIn('pagination', html)
        self.assertIn('page=2', html)
        self.assertIn('sort=id', html)
        self.assertIn('order=desc', html)

    def test_no_page_links_when_single_page(self):
        # given
        self.pl.add(self.pl.create_tag('tag1'))
        self.pl.commit()
        # when
        html = self.render()
        # then
        self.assertNotIn('pagination', html)

    def test_shows_task_counts(self):
        # given
        tag1 = self.pl.create_tag('tag1')
        tag2 = self.pl.create_tag('tag2')
        task1 = self.pl.create_task('task1', is_public=True)
        task2 = self.pl.create_task('task2', is_public=True)
        task1.tags.append(tag1)
        task2.tags.append(tag1)
        for obj in [tag1, tag2, task1, task2]:
            self.pl.add(obj)
        self.pl.commit()
        # when
        html = self.render(sort='id')
        # then
        self.assertIn('<th>Tasks</th>', html)
        self.assertRegex(html, r'>tag1</a></td>\s*<td></td>\s*<td>2</td>')
        self.assertRegex(html, r'>tag2</a></td>\s*<td></td>\s*<td>0</td>')
