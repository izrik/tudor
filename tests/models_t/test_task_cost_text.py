#!/usr/bin/env python

import unittest
from decimal import Decimal

from persistence.in_memory.models.task import Task


class TaskCostTextTest(unittest.TestCase):

    def test_no_duration_yields_empty(self):
        # given
        t1 = Task('t1', expected_cost=None)

        # when
        result = t1.get_expected_cost_for_viewing()

        # then
        self.assertEqual('', result)

    def test_single_whole_number(self):
        # given
        t1 = Task('t1', expected_cost=Decimal(1))

        # when
        result = t1.get_expected_cost_for_viewing()

        # then
        self.assertEqual('1.00', result)

    def test_single_cents_digit(self):
        # given
        t1 = Task('t1', expected_cost=Decimal(1.1))

        # when
        result = t1.get_expected_cost_for_viewing()

        # then
        self.assertEqual('1.10', result)

    def test_extra_digits(self):
        # given
        t1 = Task('t1', expected_cost=Decimal(1.1234))

        # when
        result = t1.get_expected_cost_for_viewing()

        # then
        self.assertEqual('1.12', result)

    def test_extra_digits_round_up(self):
        # given
        t1 = Task('t1', expected_cost=Decimal(1.9876))

        # when
        result = t1.get_expected_cost_for_viewing()

        # then
        self.assertEqual('1.99', result)

    def test_export_no_duration_yields_none(self):
        # given
        t1 = Task('t1', expected_cost=None)

        # when
        result = t1.get_expected_cost_for_export()

        # then
        self.assertEqual(None, result)

    def test_export_single_whole_number(self):
        # given
        t1 = Task('t1', expected_cost=Decimal(1))

        # when
        result = t1.get_expected_cost_for_export()

        # then
        self.assertEqual('1.00', result)

    def test_export_single_cents_digit(self):
        # given
        t1 = Task('t1', expected_cost=Decimal(1.1))

        # when
        result = t1.get_expected_cost_for_export()

        # then
        self.assertEqual('1.10', result)

    def test_export_extra_digits(self):
        # given
        t1 = Task('t1', expected_cost=Decimal(1.1234))

        # when
        result = t1.get_expected_cost_for_export()

        # then
        self.assertEqual('1.12', result)

    def test_export_extra_digits_round_up(self):
        # given
        t1 = Task('t1', expected_cost=Decimal(1.9876))

        # when
        result = t1.get_expected_cost_for_export()

        # then
        self.assertEqual('1.99', result)

    def test_export_str_extra_digits(self):
        # given
        t1 = Task('t1', expected_cost='1.1234')

        # when
        result = t1.get_expected_cost_for_export()

        # then
        self.assertEqual('1.12', result)

    def test_export_str_extra_digits_round_up(self):
        # given
        t1 = Task('t1', expected_cost='1.9876')

        # when
        result = t1.get_expected_cost_for_export()

        # then
        self.assertEqual('1.99', result)
