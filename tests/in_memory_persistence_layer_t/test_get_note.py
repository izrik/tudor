
from models.note import Note
from tests.in_memory_persistence_layer_t.in_memory_test_base import \
    InMemoryTestBase


# copied from ../test_get_note.py, with removals


class GetNoteTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
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