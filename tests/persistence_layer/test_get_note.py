import unittest

from models.note import Note
from tests.persistence_layer.util import generate_pl


class GetNoteTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_get_note_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_note, None)

    def test_get_note_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_note(1))

    def test_get_note_existing_yields_that_note(self):
        # given
        note = Note('note')
        self.pl.add(note)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(note.id)
        # when
        result = self.pl.get_note(note.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(note, result)

    def test_get_db_note_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl._get_db_note, None)

    def test_get_db_note_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl._get_db_note(1))

    def test_get_db_note_existing_yields_that_dbnote(self):
        # given
        dbnote = self.pl.DbNote('note')
        self.pl.db.session.add(dbnote)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbnote.id)
        # when
        result = self.pl._get_db_note(dbnote.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(dbnote, result)
