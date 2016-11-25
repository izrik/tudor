#!/usr/bin/env python

import unittest
from mock import Mock
from flask import request
import werkzeug.exceptions

from tudor import generate_app
from render.render_layer import RenderLayer


class TaskRenderLayerTest(unittest.TestCase):

    def setUp(self):
        # app = generate_app(db_uri='sqlite://')
        # self.db = app.ds.db
        # self.db.create_all()
        # self.app = app
        # self.rl = app.rl
        self.hr = Mock()
        self.jr = Mock()
        self.rl = RenderLayer(self.hr, self.jr)
        self.data = {}

    def test_render_index_html(self):

        # when
        self.rl.render_index(self.data, 'html')

        # then
        self.hr.render_index.assert_called()
        self.jr.render_index.assert_not_called()

    def test_render_index_json(self):

        # when
        self.rl.render_index(self.data, 'json')

        # then
        self.hr.render_index.assert_not_called()
        self.jr.render_index.assert_called()

    def test_render_deadlines_html(self):

        # when
        self.rl.render_deadlines(self.data, 'html')

        # then
        self.hr.render_deadlines.assert_called()
        self.jr.render_deadlines.assert_not_called()

    def test_render_deadlines_json(self):

        # when
        self.rl.render_deadlines(self.data, 'json')

        # then
        self.hr.render_deadlines.assert_not_called()
        self.jr.render_deadlines.assert_called()

    def test_render_task_html(self):

        # when
        self.rl.render_task(self.data, 'html')

        # then
        self.hr.render_task.assert_called()
        self.jr.render_task.assert_not_called()

    def test_render_task_json(self):

        # when
        self.rl.render_task(self.data, 'json')

        # then
        self.hr.render_task.assert_not_called()
        self.jr.render_task.assert_called()

    def test_render_list_users_html(self):

        # when
        self.rl.render_list_users(self.data, 'html')

        # then
        self.hr.render_list_users.assert_called()
        self.jr.render_list_users.assert_not_called()

    def test_render_list_users_json(self):

        # when
        self.rl.render_list_users(self.data, 'json')

        # then
        self.hr.render_list_users.assert_not_called()
        self.jr.render_list_users.assert_called()

    def test_render_user_html(self):

        # when
        self.rl.render_user(self.data, 'html')

        # then
        self.hr.render_user.assert_called()
        self.jr.render_user.assert_not_called()

    def test_render_user_json(self):

        # when
        self.rl.render_user(self.data, 'json')

        # then
        self.hr.render_user.assert_not_called()
        self.jr.render_user.assert_called()

    def test_render_options_html(self):

        # when
        self.rl.render_options(self.data, 'html')

        # then
        self.hr.render_options.assert_called()
        self.jr.render_options.assert_not_called()

    def test_render_options_json(self):

        # when
        self.rl.render_options(self.data, 'json')

        # then
        self.hr.render_options.assert_not_called()
        self.jr.render_options.assert_called()

    def test_render_list_tags_html(self):

        # when
        self.rl.render_list_tags(self.data, 'html')

        # then
        self.hr.render_list_tags.assert_called()
        self.jr.render_list_tags.assert_not_called()

    def test_render_list_tags_json(self):

        # when
        self.rl.render_list_tags(self.data, 'json')

        # then
        self.hr.render_list_tags.assert_not_called()
        self.jr.render_list_tags.assert_called()

    def test_render_tag_html(self):

        # when
        self.rl.render_tag(self.data, 'html')

        # then
        self.hr.render_tag.assert_called()
        self.jr.render_tag.assert_not_called()

    def test_render_tag_json(self):

        # when
        self.rl.render_tag(self.data, 'json')

        # then
        self.hr.render_tag.assert_not_called()
        self.jr.render_tag.assert_called()


class TaskRenderLayerGetAcceptTypeTest(unittest.TestCase):
    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.db = app.ds.db
        self.db.create_all()
        self.app = app
        self.rl = app.rl

    def test_get_accept_type_raises_on_no_accept(self):
        with self.app.test_request_context('/'):
            # expect
            self.assertRaises(werkzeug.exceptions.NotAcceptable,
                              self.rl.get_accept_type)

    def test_get_accept_type_html(self):
        with self.app.test_request_context('/',
                                           headers={'Accept': 'text/html'}):

            # when
            accept = self.rl.get_accept_type()

            # then
            self.assertEqual('html', accept)

    def test_get_accept_type_json(self):
        with self.app.test_request_context(
                '/', headers={'Accept': 'application/json'}):

            # when
            accept = self.rl.get_accept_type()

            # then
            self.assertEqual('json', accept)


class TaskRenderLayerSwitchOnGetAcceptTypeTest(unittest.TestCase):
    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.db = app.ds.db
        self.db.create_all()
        self.app = app
        # self.rl = app.rl
        self.hr = Mock()
        self.jr = Mock()
        self.rl = RenderLayer(self.hr, self.jr)
        self.data = {}

    def test_render_index(self):
        with self.app.test_request_context('/',
                                           headers={'Accept': 'text/html'}):

            # when
            self.rl.render_index(self.data)

            # then
            self.hr.render_index.assert_called()
            self.jr.render_index.assert_not_called()

    def test_render_deadlines(self):
        with self.app.test_request_context('/deadlines',
                                           headers={'Accept': 'text/html'}):
            # when
            self.rl.render_deadlines(self.data)

            # then
            self.hr.render_deadlines.assert_called()
            self.jr.render_deadlines.assert_not_called()

    def test_render_task(self):
        with self.app.test_request_context('/task/1',
                                           headers={'Accept': 'text/html'}):
            # when
            self.rl.render_task(self.data)

            # then
            self.hr.render_task.assert_called()
            self.jr.render_task.assert_not_called()

    def test_render_list_users(self):
        with self.app.test_request_context('/users',
                                           headers={'Accept': 'text/html'}):
            # when
            self.rl.render_list_users(self.data)

            # then
            self.hr.render_list_users.assert_called()
            self.jr.render_list_users.assert_not_called()

    def test_render_user(self):
        with self.app.test_request_context('/users/1',
                                           headers={'Accept': 'text/html'}):
            # when
            self.rl.render_user(self.data)

            # then
            self.hr.render_user.assert_called()
            self.jr.render_user.assert_not_called()

    def test_render_options(self):
        with self.app.test_request_context('/options',
                                           headers={'Accept': 'text/html'}):
            # when
            self.rl.render_options(self.data)

            # then
            self.hr.render_options.assert_called()
            self.jr.render_options.assert_not_called()

    def test_render_list_tags(self):
        with self.app.test_request_context('/tags',
                                           headers={'Accept': 'text/html'}):
            # when
            self.rl.render_list_tags(self.data)

            # then
            self.hr.render_list_tags.assert_called()
            self.jr.render_list_tags.assert_not_called()

    def test_render_tag(self):
        with self.app.test_request_context('/tags/1',
                                           headers={'Accept': 'text/html'}):
            # when
            self.rl.render_tag(self.data)

            # then
            self.hr.render_tag.assert_called()
            self.jr.render_tag.assert_not_called()
