import unittest

from tests.persistence_layer.util import generate_pl


class DbNoteConstructorTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()

    def test_none_lazy_is_allowed(self):
        # when
        note = self.pl.DbNote('note', lazy={})
        # then
        self.assertIsInstance(note, self.pl.DbNote)

    def test_empty_lazy_is_allowed(self):
        # when
        note = self.pl.DbNote('note', lazy={})
        # then
        self.assertIsInstance(note, self.pl.DbNote)

    def test_non_empty_lazy_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.DbNote, 'note', lazy={'id': 1})