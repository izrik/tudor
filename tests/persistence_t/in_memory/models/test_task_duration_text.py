#!/usr/bin/env python

import unittest

from persistence.in_memory.models.task import IMTask


class TaskDurationTextTest(unittest.TestCase):

    def test_no_duration_yields_empty(self):
        # given
        t1 = Task('t1', expected_duration_minutes=None)

        # when
        result = t1.get_expected_duration_for_viewing()

        # then
        self.assertEqual('', result)

    def test_single_minute_yields_special_case(self):
        # given
        t1 = Task('t1', expected_duration_minutes=1)

        # when
        result = t1.get_expected_duration_for_viewing()

        # then
        self.assertEqual('1 minute', result)

    def test_minutes_yields_text_0(self):
        # given
        t1 = Task('t1', expected_duration_minutes=0)

        # when
        result = t1.get_expected_duration_for_viewing()

        # then
        self.assertEqual('0 minutes', result)

    def test_minutes_yields_text_2(self):

        # given
        t1 = Task('t1', expected_duration_minutes=2)

        # when
        result = t1.get_expected_duration_for_viewing()

        # then
        self.assertEqual('2 minutes', result)

    def test_minutes_yields_text_3(self):

        # given
        t1 = Task('t1', expected_duration_minutes=3)

        # when
        result = t1.get_expected_duration_for_viewing()

        # then
        self.assertEqual('3 minutes', result)

    def test_minutes_yields_text_4(self):

        # given
        t1 = Task('t1', expected_duration_minutes=4)

        # when
        result = t1.get_expected_duration_for_viewing()

        # then
        self.assertEqual('4 minutes', result)

    def test_minutes_yields_text_12345(self):

        # given
        t1 = Task('t1', expected_duration_minutes=12345)

        # when
        result = t1.get_expected_duration_for_viewing()

        # then
        self.assertEqual('12345 minutes', result)
