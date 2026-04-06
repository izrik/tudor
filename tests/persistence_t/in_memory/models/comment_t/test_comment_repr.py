#!/usr/bin/env python

import unittest

from persistence.in_memory.models.comment import Comment


class CommentReprTest(unittest.TestCase):
    def test_generates_repr_string(self):
        # given
        comment = Comment(content='content')
        comment.id = 123
        #when
        r = repr(comment)
        # then
        self.assertEqual('Comment(\'content\', id=123)', r)

    # TODO: test other contents, other ids, None
    # TODO: test when the content is > 20 in length
