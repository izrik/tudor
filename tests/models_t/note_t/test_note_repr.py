#!/usr/bin/env python

import unittest

from persistence.in_memory.models.note import Note


class NoteReprTest(unittest.TestCase):
    def test_generates_repr_string(self):
        # given
        note = Note(content='content')
        note.id = 123
        #when
        r = repr(note)
        # then
        self.assertEqual('Note(\'content\', id=123)', r)

    # TODO: test other contents, other ids, None
    # TODO: test when the content is > 20 in length
