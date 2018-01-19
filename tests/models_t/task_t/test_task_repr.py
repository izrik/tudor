#!/usr/bin/env python

import unittest

from models.task import Task


class TaskReprTest(unittest.TestCase):
    def test_generates_repr_string(self):
        # given
        task = Task(summary='summary')
        task.id = 123
        #when
        r = repr(task)
        # then
        self.assertEqual('Task(\'summary\', id=123)', r)

    # TODO: test other summaries, other ids, None
