import unittest

from models.attachment import Attachment
from tests.persistence_layer.util import generate_pl


class GetAttachmentTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_get_attachment_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_attachment, None)

    def test_get_attachment_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_attachment(1))

    def test_get_attachment_existing_yields_that_attachment(self):
        # given
        attachment = Attachment('attachment')
        self.pl.add(attachment)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(attachment.id)
        # when
        result = self.pl.get_attachment(attachment.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(attachment, result)

    def test_get_db_attachment_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl._get_db_attachment, None)

    def test_get_db_attachment_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl._get_db_attachment(1))

    def test_get_db_attachment_existing_yields_that_dbattachment(self):
        # given
        dbattachment = self.pl.DbAttachment('attachment')
        self.pl.db.session.add(dbattachment)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbattachment.id)
        # when
        result = self.pl._get_db_attachment(dbattachment.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(dbattachment, result)
