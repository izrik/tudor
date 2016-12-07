#!/usr/bin/env python

import unittest
import json

from datetime import datetime

from flask import Response

from api.json import JsonApi
from tudor import generate_app
from render.json_renderer import JsonRenderer


class JsonApiTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.jr = JsonRenderer()
        self.ll = self.app.ll
        self.db = self.app.ds.db
        self.db.create_all()
        self.api = JsonApi(self.jr, self.ll, self.db)
        self.Task = self.app.ds.Task
        self.Tag = self.app.ds.Tag
        self.User = self.app.ds.User
        self.Option = self.app.ds.Option
        self.TaskUserLink = self.app.ds.TaskUserLink

    def test_get_index(self):
        with self.app.test_request_context(
                '/', headers={'Accept': 'application/json'}):
            result = self.api.index()
            self.assertEqual(({
                       'tasks': '/api/v1.0/tasks/',
                       'tags': '/api/v1.0/tags/',
                   }, 200),
                result)

    def test_list_tasks(self):

        # given
        t1 = self.Task(summary='sum1', description='desc1')
        t2 = self.Task(summary='sum2', description='desc2')
        t3 = self.Task(summary='sum3', description='desc3')
        self.db.session.add(t1)
        self.db.session.add(t2)
        self.db.session.add(t3)
        u = self.User('user@example.com')
        self.db.session.add(u)
        self.db.session.commit()
        tul = self.TaskUserLink(t1.id, u.id)
        self.db.session.add(tul)
        tul = self.TaskUserLink(t2.id, u.id)
        self.db.session.add(tul)
        tul = self.TaskUserLink(t3.id, u.id)
        self.db.session.add(tul)
        self.db.session.commit()

        with self.app.test_request_context(
                '/api/v1.0/tasks/', headers={'Accept': 'application/json'}):
            # when
            result = self.api.list_tasks(u)

            # then it returns a json representation of the tasks and 200 status
            # code
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)

            body, code = result
            self.assertEqual(200, code)

            self.assertIsNotNone(body)
            self.assertIsInstance(body, basestring)

            parsed = json.loads(body)
            self.assertEqual([
                {
                    'summary': t1.summary,
                    'href': '/api/v1.0/tasks/{}'.format(t1.id)
                },
                {
                    'summary': t2.summary,
                    'href': '/api/v1.0/tasks/{}'.format(t2.id)
                },
                {
                    'summary': t3.summary,
                    'href': '/api/v1.0/tasks/{}'.format(t3.id)
                },
            ], parsed)

    def test_create_tasks(self):

        # given
        data = {
            'summary': 'summary',
            'description': 'description',
            'is_done': False,
            'is_deleted': False,
            'order_num': 789,
            'deadline': datetime(2016, 12, 31),
            'expected_duration_minutes': 123,
            'expected_cost': 456,
        }
        u = self.User('user@example.com')
        self.db.session.add(u)
        self.db.session.commit()

        with self.app.test_request_context(
                '/', headers={'Accept': 'application/json'}):
            # when
            result = self.api.create_task(u, data)

            # then it returns a json representation of the new tasks, along
            # with Location header and 201 status code
            self.assertIsNotNone(result)
            self.assertIsInstance(result, Response)

            self.assertIn('Location', result.headers)
            self.assertRegexpMatches(result.headers['Location'],
                                     '/api/v1.0/tasks/\d+')

            code = result.status_code
            self.assertEqual(201, code)

            body = result.data
            self.assertIsNotNone(body)
            self.assertIsInstance(body, basestring)

            parsed = json.loads(body)
            self.assertIsNotNone(parsed)
            self.assertIn('id', parsed)
            self.assertEqual('summary', parsed['summary'])
            self.assertEqual('description', parsed['description'])
            self.assertEqual(False, parsed['is_done'])
            self.assertEqual(False, parsed['is_deleted'])
            self.assertEqual(789, parsed['order_num'])
            self.assertEqual('2016-12-31 00:00:00', parsed['deadline'])
            self.assertEqual(None, parsed['parent'])
            self.assertEqual(123, parsed['expected_duration_minutes'])
            self.assertEqual('456.00', parsed['expected_cost'])
            self.assertEqual([], parsed['tags'])
            self.assertEqual(['/users/{}'.format(u.id)], parsed['users'])

            # then the new task is present in the database
            t = self.Task.query.get(parsed['id'])
            self.assertIsNotNone(t)
            self.assertEqual('summary', t.summary)
            self.assertEqual('description', t.description)
            self.assertEqual(False, t.is_done)
            self.assertEqual(False, t.is_deleted)
            self.assertEqual(789, t.order_num)
            self.assertEqual(datetime(2016, 12, 31), t.deadline)
            self.assertEqual(None, t.parent)
            self.assertEqual(123, t.expected_duration_minutes)
            self.assertEqual(456.00, t.expected_cost)
            self.assertEqual([], t.tags.all())
            self.assertEqual(1, t.users.count())
            self.assertIs(u, t.users.first().user)

    def test_create_tasks_with_nulls(self):
        # given
        data = {
            'summary': 'summary'
        }
        u = self.User('user@example.com')
        self.db.session.add(u)
        self.db.session.commit()

        with self.app.test_request_context(
                '/', headers={'Accept': 'application/json'}):
            # when
            result = self.api.create_task(u, data)

            # then it returns a json representation of the new tasks, along
            # with Location header and 201 status code
            self.assertIsNotNone(result)
            self.assertIsInstance(result, Response)

            self.assertIn('Location', result.headers)
            self.assertRegexpMatches(result.headers['Location'],
                                     '/api/v1.0/tasks/\d+')

            code = result.status_code
            self.assertEqual(201, code)

            body = result.data
            self.assertIsNotNone(body)
            self.assertIsInstance(body, basestring)

            parsed = json.loads(body)
            self.assertIsNotNone(parsed)
            self.assertIn('id', parsed)
            self.assertEqual('summary', parsed['summary'])
            self.assertEqual('', parsed['description'])
            self.assertEqual(False, parsed['is_done'])
            self.assertEqual(False, parsed['is_deleted'])
            self.assertEqual(0, parsed['order_num'])
            self.assertEqual(None, parsed['deadline'])
            self.assertEqual(None, parsed['parent'])
            self.assertEqual(None, parsed['expected_duration_minutes'])
            self.assertEqual(None, parsed['expected_cost'])
            self.assertEqual([], parsed['tags'])
            self.assertEqual(['/users/{}'.format(u.id)], parsed['users'])

            # then the new task is present in the database
            t = self.Task.query.get(parsed['id'])
            self.assertIsNotNone(t)
            self.assertEqual('summary', t.summary)
            self.assertEqual('', t.description)
            self.assertEqual(False, t.is_done)
            self.assertEqual(False, t.is_deleted)
            self.assertEqual(0, t.order_num)
            self.assertEqual(None, t.deadline)
            self.assertEqual(None, t.parent)
            self.assertEqual(None, t.expected_duration_minutes)
            self.assertEqual(None, t.expected_cost)
            self.assertEqual([], t.tags.all())
            self.assertEqual(1, t.users.count())
            self.assertIs(u, t.users.first().user)

    def test_update_tasks(self):
        # given
        data = {
            'summary': 'summary',
            'description': 'description',
            'is_done': True,
            'is_deleted': True,
            'order_num': 789,
            'deadline': datetime(2016, 12, 31),
            'expected_duration_minutes': 123,
            'expected_cost': 456,
        }
        t1 = self.Task(summary='summ', description='desc')
        self.db.session.add(t1)
        u = self.User('user@example.com')
        self.db.session.add(u)
        self.db.session.commit()
        tul = self.TaskUserLink(t1.id, u.id)
        self.db.session.add(tul)
        self.db.session.commit()

        # preconditions

        t2 = self.Task.query.get(t1.id)
        self.assertIsNotNone(t2)
        self.assertEqual('summ', t2.summary)
        self.assertEqual('desc', t2.description)
        self.assertEqual(False, t2.is_done)
        self.assertEqual(False, t2.is_deleted)
        self.assertEqual(0, t2.order_num)
        self.assertEqual(None, t2.deadline)
        self.assertEqual(None, t2.parent)
        self.assertEqual(None, t2.expected_duration_minutes)
        self.assertEqual(None, t2.expected_cost)
        self.assertEqual([], t2.tags.all())
        self.assertEqual(1, t2.users.count())
        self.assertIs(u, t2.users.first().user)

        with self.app.test_request_context(
                '/', headers={'Accept': 'application/json'}):
            # when
            result = self.api.update_task(u, t1.id, data)

            # then it returns a json representation of the new tasks, along
            # with Location header and 200 status code
            self.assertIsNotNone(result)
            self.assertIsInstance(result, Response)

            self.assertIn('Location', result.headers)
            self.assertRegexpMatches(result.headers['Location'],
                                     '/api/v1.0/tasks/\d+')

            code = result.status_code
            self.assertEqual(200, code)

            body = result.data
            self.assertIsNotNone(body)
            self.assertIsInstance(body, basestring)

            parsed = json.loads(body)
            self.assertIsNotNone(parsed)
            self.assertIn('id', parsed)
            self.assertEqual('summary', parsed['summary'])
            self.assertEqual('description', parsed['description'])
            self.assertEqual(True, parsed['is_done'])
            self.assertEqual(True, parsed['is_deleted'])
            self.assertEqual(789, parsed['order_num'])
            self.assertEqual('2016-12-31 00:00:00', parsed['deadline'])
            self.assertEqual(None, parsed['parent'])
            self.assertEqual(123, parsed['expected_duration_minutes'])
            self.assertEqual('456.00', parsed['expected_cost'])
            self.assertEqual([], parsed['tags'])
            self.assertEqual(['/users/{}'.format(u.id)], parsed['users'])

            # then the new task is present in the database
            t = self.Task.query.get(parsed['id'])
            self.assertIsNotNone(t)
            self.assertEqual('summary', t.summary)
            self.assertEqual('description', t.description)
            self.assertEqual(True, t.is_done)
            self.assertEqual(True, t.is_deleted)
            self.assertEqual(789, t.order_num)
            self.assertEqual(datetime(2016, 12, 31), t.deadline)
            self.assertEqual(None, t.parent)
            self.assertEqual(123, t.expected_duration_minutes)
            self.assertEqual(456.00, t.expected_cost)
            self.assertEqual([], t.tags.all())
            self.assertEqual(1, t.users.count())
            self.assertIs(u, t.users.first().user)
