
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class GetNoteTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()

    def test_get_note_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_note, None)

    def test_get_note_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_note(1))

    def test_get_note_existing_yields_that_note(self):
        # given
        note = self.pl.create_note('note')
        self.pl.add(note)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(note.id)
        # when
        result = self.pl.get_note(note.id)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(note.id, result.id)

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
        self.assertEqual(dbnote.id, result.id)
