
from tests.persistence_t.in_memory.in_memory_test_base import InMemoryTestBase


# copied from ../test_get_attachment.py, with removals


class GetAttachmentTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_get_attachment_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_attachment, None)

    def test_get_attachment_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_attachment(1))

    def test_get_attachment_existing_yields_that_attachment(self):
        # given
        attachment = self.pl.create_attachment('attachment')
        self.pl.add(attachment)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(attachment.id)
        # when
        result = self.pl.get_attachment(attachment.id)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(attachment.id, result.id)
