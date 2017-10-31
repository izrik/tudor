
from models.attachment import Attachment
from tests.in_memory_persistence_layer.in_memory_test_base import \
    InMemoryTestBase


# copied from ../test_get_attachments.py, with removals


class GetAttachmentsTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.a1 = Attachment('a1.txt')
        self.pl.add(self.a1)
        self.a2 = Attachment('a2.txt')
        self.pl.add(self.a2)
        self.pl.commit()

    def test_get_attachments_without_params_returns_all_attachments(self):
        # when
        results = self.pl.get_attachments()
        # then
        self.assertEqual({self.a1, self.a2}, set(results))

    def test_count_attachments_without_params_returns_all_attachments(self):
        # expect
        self.assertEqual(2, self.pl.count_attachments())

    def test_get_attachments_attachment_id_in_filters_only_matching_atts(self):
        # when
        results = self.pl.get_attachments(attachment_id_in=[self.a1.id])
        # then
        self.assertEqual({self.a1}, set(results))
        # when
        results = self.pl.get_attachments(attachment_id_in=[self.a2.id])
        # then
        self.assertEqual({self.a2}, set(results))
        # when
        results = self.pl.get_attachments(
            attachment_id_in=[self.a1.id, self.a2.id])
        # then
        self.assertEqual({self.a1, self.a2}, set(results))

    def test_get_attachments_att_id_in_unmatching_ids_do_not_filter(self):
        # given
        next_id = max([self.a1.id, self.a2.id]) + 1
        # when
        results = self.pl.get_attachments(
            attachment_id_in=[self.a1.id, self.a2.id, next_id])
        # then
        self.assertEqual({self.a1, self.a2}, set(results))

    def test_get_attachments_attachment_id_in_empty_yields_no_atts(self):
        # when
        results = self.pl.get_attachments(attachment_id_in=[])
        # then
        self.assertEqual(set(), set(results))

    def test_count_attachments_att_id_in_filters_only_matching_atts(self):
        # expect
        self.assertEqual(1, self.pl.count_attachments(
            attachment_id_in=[self.a1.id]))
        # expect
        self.assertEqual(1, self.pl.count_attachments(
            attachment_id_in=[self.a2.id]))
        # expect
        self.assertEqual(2, self.pl.count_attachments(
            attachment_id_in=[self.a1.id, self.a2.id]))

    def test_count_attachments_att_id_in_unmatching_ids_do_not_filter(self):
        # given
        next_id = max([self.a1.id, self.a2.id]) + 1
        # when
        results = self.pl.count_attachments(
            attachment_id_in=[self.a1.id, self.a2.id, next_id])
        # then
        self.assertEqual(2, results)

    def test_count_attachments_attachment_id_in_empty_yields_no_atts(self):
        # expect
        self.assertEqual(0, self.pl.count_attachments(attachment_id_in=[]))
