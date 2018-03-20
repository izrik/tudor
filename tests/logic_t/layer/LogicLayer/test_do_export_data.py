#!/usr/bin/env python

import unittest

from tests.logic_t.layer.LogicLayer.util import generate_ll


class ExportDataTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_exports_data(self):
        # given
        types_to_export = {'tasks', 'tags', 'notes', 'attachments', 'users',
                           'options'}
        task = self.pl.create_task('task')
        self.pl.add(task)
        tag = self.pl.create_tag('tag')
        self.pl.add(tag)
        note = self.pl.create_note('note')
        self.pl.add(note)
        att = self.pl.create_attachment('attachment')
        self.pl.add(att)
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        option = self.pl.create_option('key', 'value')
        self.pl.add(option)
        self.pl.commit()
        # when
        result = self.ll.do_export_data(types_to_export)
        # then
        self.assertEqual(result, {
            'tasks': [{
                'id': task.id,
                'summary': 'task',
                'description': '',
                'is_done': False,
                'is_deleted': False,
                'deadline': None,
                'expected_duration_minutes': None,
                'expected_cost': None,
                'order_num': 0,
                'parent': None,
                'is_public': False,
                'children': [],
                'dependees': [],
                'dependants': [],
                'prioritize_before': [],
                'prioritize_after': [],
                'tags': [],
                'users': [],
                'notes': [],
                'attachments': [],

            }],
            'tags': [{
                'id': tag.id,
                'value': 'tag',
                'description': None,
                'tasks': [],
            }],
            'notes': [{
                'id': note.id,
                'content': 'note',
                'timestamp': None,
                'task': None,
            }],
            'attachments': [{
                'id': note.id,
                'timestamp': None,
                'path': 'attachment',
                'filename': None,
                'description': None,
                'task': None,
            }],
            'users': [{
                'id': user.id,
                'email': 'user@example.com',
                'is_admin': False,
                'hashed_password': None,
                'tasks': [],
            }],
            'options': [{
                'key': 'key',
                'value': 'value'
            }],
        })
