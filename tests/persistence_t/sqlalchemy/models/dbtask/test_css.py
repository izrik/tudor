#!/usr/bin/env python

import unittest

from tests.util import generate_test_app


class TaskCssTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_test_app().pl

    def test_normal_gives_correct_css_class(self):
        # given
        t1 = self.pl.DbTask('t1')

        # when
        result = t1.get_css_class()

        # then
        self.assertEqual('', result)

    def test_done_gives_correct_css_class(self):
        # given
        t1 = self.pl.DbTask('t1', is_done=True)

        # when
        result = t1.get_css_class()

        # then
        self.assertEqual('done-not-deleted', result)

    def test_deleted_gives_correct_css_class(self):
        # given
        t1 = self.pl.DbTask('t1', is_deleted=True)

        # when
        result = t1.get_css_class()

        # then
        self.assertEqual('not-done-deleted', result)

    def test_done_deleted_gives_correct_css_class(self):
        # given
        t1 = self.pl.DbTask('t1', is_done=True, is_deleted=True)

        # when
        result = t1.get_css_class()

        # then
        self.assertEqual('done-deleted', result)

    def test_normal_gives_correct_css_attr(self):
        # given
        t1 = self.pl.DbTask('t1')

        # when
        result = t1.get_css_class_attr()

        # then
        self.assertEqual('', result)

    def test_done_gives_correct_css_attr(self):
        # given
        t1 = self.pl.DbTask('t1', is_done=True)

        # when
        result = t1.get_css_class_attr()

        # then
        self.assertEqual(' class="done-not-deleted" ', result)

    def test_deleted_gives_correct_css_attr(self):
        # given
        t1 = self.pl.DbTask('t1', is_deleted=True)

        # when
        result = t1.get_css_class_attr()

        # then
        self.assertEqual(' class="not-done-deleted" ', result)

    def test_done_deleted_gives_correct_css_attr(self):
        # given
        t1 = self.pl.DbTask('t1', is_done=True, is_deleted=True)

        # when
        result = t1.get_css_class_attr()

        # then
        self.assertEqual(' class="done-deleted" ', result)
