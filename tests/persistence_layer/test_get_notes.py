import unittest

from models.note import Note
from tests.persistence_layer.util import generate_pl


class GetNotesTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()
        self.n1 = Note('n1')
        self.pl.add(self.n1)
        self.n2 = Note('n2')
        self.pl.add(self.n2)
        self.pl.commit()

    def test_get_notes_without_params_returns_all_notes(self):
        # when
        results = self.pl.get_notes()
        # then
        self.assertEqual({self.n1, self.n2}, set(results))

    def test_count_notes_without_params_returns_all_notes(self):
        # expect
        self.assertEqual(2, self.pl.count_notes())

    def test_get_notes_note_id_in_filters_only_matching_notes(self):
        # when
        results = self.pl.get_notes(note_id_in=[self.n1.id])
        # then
        self.assertEqual({self.n1}, set(results))
        # when
        results = self.pl.get_notes(note_id_in=[self.n2.id])
        # then
        self.assertEqual({self.n2}, set(results))
        # when
        results = self.pl.get_notes(note_id_in=[self.n1.id, self.n2.id])
        # then
        self.assertEqual({self.n1, self.n2}, set(results))

    def test_get_notes_note_id_in_unmatching_ids_do_not_filter(self):
        # given
        next_id = max([self.n1.id, self.n2.id]) + 1
        # when
        results = self.pl.get_notes(
            note_id_in=[self.n1.id, self.n2.id, next_id])
        # then
        self.assertEqual({self.n1, self.n2}, set(results))

    def test_get_notes_note_id_in_empty_yields_no_notes(self):
        # when
        results = self.pl.get_notes(note_id_in=[])
        # then
        self.assertEqual(set(), set(results))

    def test_count_notes_note_id_in_filters_only_matching_notes(self):
        # expect
        self.assertEqual(1, self.pl.count_notes(note_id_in=[self.n1.id]))
        # expect
        self.assertEqual(1, self.pl.count_notes(note_id_in=[self.n2.id]))
        # expect
        self.assertEqual(2, self.pl.count_notes(
            note_id_in=[self.n1.id, self.n2.id]))

    def test_count_notes_note_id_in_unmatching_ids_do_not_filter(self):
        # given
        next_id = max([self.n1.id, self.n2.id]) + 1
        # when
        results = self.pl.count_notes(
            note_id_in=[self.n1.id, self.n2.id, next_id])
        # then
        self.assertEqual(2, results)

    def test_count_notes_note_id_in_empty_yields_no_notes(self):
        # expect
        self.assertEqual(0, self.pl.count_notes(note_id_in=[]))
