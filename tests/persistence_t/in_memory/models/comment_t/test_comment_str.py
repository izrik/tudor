#!/usr/bin/env python

import unittest

from persistence.in_memory.models.comment import Comment


class CommentStrTest(unittest.TestCase):
    def test_generates_str_string(self):
        # given
        comment = Comment(content='content')
        comment.id = 123
        #when
        r = str(comment)
        # then
        fmt = 'Comment(\'content\', comment id=123, id=[{}])'
        expected = fmt.format(id(comment))
        self.assertEqual(expected, r)

    # TODO: test other contents, other ids, None
    # TODO: test when the content is > 20 in length
