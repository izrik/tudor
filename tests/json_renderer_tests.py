#!/usr/bin/env python

import unittest
import json

from render.json_renderer import JsonRenderer
from tudor import generate_app


class JsonRendererTest(unittest.TestCase):
    def setUp(self):
        self.jr = JsonRenderer()
        self.app = generate_app(db_uri='sqlite://')
        self.Task = self.app.ds.Task
        self.Tag = self.app.ds.Tag
        self.User = self.app.ds.User
        self.Option = self.app.ds.Option

    def test_render_index(self):
        # given
        t1 = self.Task(summary='sum')
        t1.id = 123
        t2 = self.Task(summary='summ')
        t2.id = 456
        tag = self.Tag('tag1')
        tag.id = 789
        data = {
            'tasks_h': [t1, t2],
            'all_tags': [tag]
        }
        with self.app.test_request_context(
                '/', headers={'Accept': 'application/json'}):
            # when
            result = self.jr.render_index(data)

            # then
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(2, len(result))

            body, code = result
            self.assertEqual(200, code)
            self.assertIsNotNone(body)
            self.assertIsInstance(body, basestring)

            parsed = json.loads(body)
            self.assertIsNotNone(parsed)
            self.assertEqual(
                {
                    'tasks': [
                        {
                            'summary': 'sum',
                            'href': '/task/123'
                        },
                        {
                            'summary': 'summ',
                            'href': '/task/456'
                        },
                    ],
                    'tags': [
                        {
                            'name': 'tag1',
                            'href': '/tags/789'
                        }
                    ]
                },
                parsed)

    def test_render_deadlines(self):
        # given
        t1 = self.Task(summary='sum', deadline='2016-12-31')
        t1.id = 123
        t2 = self.Task(summary='summ', deadline='2016-12-30')
        t2.id = 456
        data = {
            'deadline_tasks': [t1, t2],
        }
        with self.app.test_request_context(
                '/deadlines', headers={'Accept': 'application/json'}):
            # when
            result = self.jr.render_deadlines(data)

            # then
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(2, len(result))

            body, code = result
            self.assertEqual(200, code)
            self.assertIsNotNone(body)
            self.assertIsInstance(body, basestring)

            parsed = json.loads(body)
            self.assertIsNotNone(parsed)
            self.assertEqual(
                [
                    {
                        'summary': 'sum',
                        'href': '/api/v1.0/tasks/123',
                        'deadline': 'Sat, 31 Dec 2016 00:00:00 GMT'
                    },
                    {
                        'summary': 'summ',
                        'href': '/api/v1.0/tasks/456',
                        'deadline': 'Fri, 30 Dec 2016 00:00:00 GMT'
                    },
                ],
                parsed)

    def test_render_deadlines_tasks_not_reordered(self):
        # given
        t1 = self.Task(summary='sum', deadline='2016-12-31')
        t1.id = 123
        t2 = self.Task(summary='summ', deadline='2016-12-30')
        t2.id = 456
        data = {
            'deadline_tasks': [t2, t1],
        }
        with self.app.test_request_context(
                '/deadlines', headers={'Accept': 'application/json'}):
            # when
            result = self.jr.render_deadlines(data)

            # then
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(2, len(result))

            body, code = result
            self.assertEqual(200, code)
            self.assertIsNotNone(body)
            self.assertIsInstance(body, basestring)

            parsed = json.loads(body)
            self.assertIsNotNone(parsed)
            self.assertEqual(
                [
                    {
                        'summary': 'summ',
                        'href': '/api/v1.0/tasks/456',
                        'deadline': 'Fri, 30 Dec 2016 00:00:00 GMT'
                    },
                    {
                        'summary': 'sum',
                        'href': '/api/v1.0/tasks/123',
                        'deadline': 'Sat, 31 Dec 2016 00:00:00 GMT'
                    },
                ],
                parsed)

    def test_render_list_tasks(self):
        # given
        t1 = self.Task(summary='sum')
        t1.id = 123
        t2 = self.Task(summary='summ')
        t2.id = 456
        tasks = [t1, t2]
        with self.app.test_request_context(
                '/tasks', headers={'Accept': 'application/json'}):
            # when
            result = self.jr.render_list_tasks(tasks)

            # then
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(2, len(result))

            body, code = result
            self.assertEqual(200, code)
            self.assertIsNotNone(body)
            self.assertIsInstance(body, basestring)

            parsed = json.loads(body)
            self.assertIsNotNone(parsed)
            self.assertEqual(
                [
                    {
                        'summary': 'sum',
                        'href': '/api/v1.0/tasks/123',
                    },
                    {
                        'summary': 'summ',
                        'href': '/api/v1.0/tasks/456',
                    },
                ],
                parsed)

    def test_render_task(self):
        # given
        t1 = self.Task(summary='sum')
        t1.id = 123
        data = {
            'task': t1,
            'descendents': []
        }
        with self.app.test_request_context(
                '/task/123', headers={'Accept': 'application/json'}):
            # when
            result = self.jr.render_task(data)

            # then
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(2, len(result))

            body, code = result
            self.assertEqual(200, code)
            self.assertIsNotNone(body)
            self.assertIsInstance(body, basestring)

            parsed = json.loads(body)
            self.assertIsNotNone(parsed)
            self.assertEqual(123, parsed['id'])
            self.assertEqual('sum', parsed['summary'])
            self.assertEqual('', parsed['description'])
            self.assertEqual(False, parsed['is_done'])
            self.assertEqual(False, parsed['is_deleted'])
            self.assertEqual(None, parsed['order_num'])
            self.assertEqual(None, parsed['deadline'])
            self.assertEqual(None, parsed['parent'])
            self.assertEqual(None, parsed['expected_duration_minutes'])
            self.assertEqual(None, parsed['expected_cost'])
            self.assertEqual([], parsed['tags'])
            self.assertEqual([], parsed['users'])

    def test_render_task_with_parent(self):
        # given
        t1 = self.Task(summary='sum')
        t1.id = 123
        t2 = self.Task(summary='summ')
        t2.id = 456
        t1.parent_id = t2.id
        data = {
            'task': t1,
            'descendents': []
        }
        with self.app.test_request_context(
                '/task/123', headers={'Accept': 'application/json'}):
            # when
            result = self.jr.render_task(data)

            # then
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(2, len(result))

            body, code = result
            self.assertEqual(200, code)
            self.assertIsNotNone(body)
            self.assertIsInstance(body, basestring)

            parsed = json.loads(body)
            self.assertIsNotNone(parsed)
            self.assertEqual(123, parsed['id'])
            self.assertEqual('sum', parsed['summary'])
            self.assertEqual('', parsed['description'])
            self.assertEqual(False, parsed['is_done'])
            self.assertEqual(False, parsed['is_deleted'])
            self.assertEqual(None, parsed['order_num'])
            self.assertEqual(None, parsed['deadline'])
            self.assertEqual('/api/v1.0/tasks/456', parsed['parent'])
            self.assertEqual(None, parsed['expected_duration_minutes'])
            self.assertEqual(None, parsed['expected_cost'])
            self.assertEqual([], parsed['tags'])
            self.assertEqual([], parsed['users'])

    def test_render_list_users(self):
        # given
        u1 = self.User('user1@example.org')
        u1.id = 123
        u2 = self.User('user2@example.com')
        u2.id = 456
        data = [u1, u2]
        with self.app.test_request_context(
                '/users', headers={'Accept': 'application/json'}):
            # when
            result = self.jr.render_list_users(data)

            # then
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(2, len(result))

            body, code = result
            self.assertEqual(200, code)
            self.assertIsNotNone(body)
            self.assertIsInstance(body, basestring)

            parsed = json.loads(body)
            self.assertIsNotNone(parsed)
            self.assertEqual(
                [
                    {
                        'href': '/users/123',
                        'id': 123,
                        'email': 'user1@example.org'
                    },
                    {
                        'href': '/users/456',
                        'id': 456,
                        'email': 'user2@example.com'
                    }
                ],
                parsed)

    def test_render_user(self):
        # given
        u1 = self.User('user1@example.org', is_admin=True)
        u1.id = 123
        data = u1
        with self.app.test_request_context(
                '/users', headers={'Accept': 'application/json'}):
            # when
            result = self.jr.render_user(data)

            # then
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(2, len(result))

            body, code = result
            self.assertEqual(200, code)
            self.assertIsNotNone(body)
            self.assertIsInstance(body, basestring)

            parsed = json.loads(body)
            self.assertIsNotNone(parsed)
            self.assertEqual(
                {
                    'is_admin': True,
                    'id': 123,
                    'email': 'user1@example.org'
                },
                parsed)

    def test_render_options(self):
        # given
        opt1 = self.Option('key1', 'value1')
        opt2 = self.Option('key2', 'value2')
        opt3 = self.Option('key3', 'value3')
        data = [opt1, opt2, opt3]
        with self.app.test_request_context(
                '/users', headers={'Accept': 'application/json'}):
            # when
            result = self.jr.render_options(data)

            # then
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(2, len(result))

            body, code = result
            self.assertEqual(200, code)
            self.assertIsNotNone(body)
            self.assertIsInstance(body, basestring)

            parsed = json.loads(body)
            self.assertIsNotNone(parsed)
            self.assertEqual(
                [
                    {
                        'key': 'key1',
                        'value': 'value1'
                    },
                    {
                        'key': 'key2',
                        'value': 'value2'
                    },
                    {
                        'key': 'key3',
                        'value': 'value3'
                    },
                ],
                parsed)

    def test_render_list_tags(self):
        # given
        t1 = self.Tag('value1', 'desc1')
        t1.id = 123
        t2 = self.Tag('value2', 'desc2')
        t2.id = 456
        t3 = self.Tag('value3', 'desc3')
        t3.id = 789
        data = [t1, t2, t3]
        with self.app.test_request_context(
                '/users', headers={'Accept': 'application/json'}):
            # when
            result = self.jr.render_list_tags(data)

            # then
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(2, len(result))

            body, code = result
            self.assertEqual(200, code)
            self.assertIsNotNone(body)
            self.assertIsInstance(body, basestring)

            parsed = json.loads(body)
            self.assertIsNotNone(parsed)
            self.assertEqual(
                [
                    {
                        'href': '/tags/123',
                        'value': 'value1',
                    },
                    {
                        'href': '/tags/456',
                        'value': 'value2',
                    },
                    {
                        'href': '/tags/789',
                        'value': 'value3',
                    },
                ],
                parsed)

    def test_render_tag(self):
        # given
        t1 = self.Tag('value1', 'desc1')
        t1.id = 123
        t2 = self.Task('sum2')
        t2.id = 456
        t3 = self.Task('sum3')
        t3.id = 789
        data = {
            'tag': t1,
            'tasks': [t2, t3]
        }
        with self.app.test_request_context(
                '/users', headers={'Accept': 'application/json'}):
            # when
            result = self.jr.render_tag(data)

            # then
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(2, len(result))

            body, code = result
            self.assertEqual(200, code)
            self.assertIsNotNone(body)
            self.assertIsInstance(body, basestring)

            parsed = json.loads(body)
            self.assertIsNotNone(parsed)
            self.assertEqual(
                {
                    'id': 123,
                    'value': 'value1',
                    'description': 'desc1',
                    'tasks': [
                        '/api/v1.0/tasks/456',
                        '/api/v1.0/tasks/789',
                    ]
                },
                parsed)
