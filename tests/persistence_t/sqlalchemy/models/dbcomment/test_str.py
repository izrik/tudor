#!/usr/bin/env python

import unittest

from tests.util import generate_test_app


class CommentStrTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_test_app().pl

    def test_generates_str_string(self):
        # given
        comment = self.pl.DbComment(content='content')
        comment.id = 123
        #when
        r = str(comment)
        # then
        fmt = 'DbComment(\'content\', comment id=123, id=[{}])'
        expected = fmt.format(id(comment))
        self.assertEqual(expected, r)

    # TODO: test other contents, other ids, None
    # TODO: test when the content is > 20 in length
