#!/usr/bin/env python

import unittest

from persistence.in_memory.models.note import Note


class NoteStrTest(unittest.TestCase):
    def test_generates_str_string(self):
        # given
        note = Note(content='content')
        note.id = 123
        #when
        r = str(note)
        # then
        fmt = 'Note(\'content\', note id=123, id=[{}])'
        expected = fmt.format(id(note))
        self.assertEqual(expected, r)

    # TODO: test other contents, other ids, None
    # TODO: test when the content is > 20 in length
