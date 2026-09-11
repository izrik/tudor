#!/usr/bin/env python

import unittest

from tests.util import generate_test_app


class TaskStrTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_test_app().pl

    def test_generates_str_string(self):
        # given
        task = self.pl.DbTask(summary='summary')
        task.id = 123
        #when
        r = str(task)
        # then
        fmt = 'DbTask(\'summary\', task id=123, id=[{}])'
        expected = fmt.format(id(task))
        self.assertEqual(expected, r)

    # TODO: test other summaries, other ids, None
