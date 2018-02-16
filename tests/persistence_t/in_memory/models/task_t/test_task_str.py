#!/usr/bin/env python

import unittest

from persistence.in_memory.models.task import Task


class TaskStrTest(unittest.TestCase):
    def test_generates_str_string(self):
        # given
        task = Task(summary='summary')
        task.id = 123
        #when
        r = str(task)
        # then
        fmt = 'Task(\'summary\', task id=123, id=[{}])'
        expected = fmt.format(id(task))
        self.assertEqual(expected, r)

    # TODO: test other summaries, other ids, None
