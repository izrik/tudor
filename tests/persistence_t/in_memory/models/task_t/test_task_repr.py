#!/usr/bin/env python

import unittest

from persistence.in_memory.models.task import IMTask


class TaskReprTest(unittest.TestCase):
    def test_generates_repr_string(self):
        # given
        task = IMTask(summary='summary')
        task.id = 123
        #when
        r = repr(task)
        # then
        self.assertEqual('IMTask(\'summary\', id=123)', r)

    # TODO: test other summaries, other ids, None
