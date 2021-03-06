import unittest

from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class DbAttachmentConstructorTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()

    def test_none_lazy_is_allowed(self):
        # when
        attachment = self.pl.DbAttachment('attachment', lazy={})
        # then
        self.assertIsInstance(attachment, self.pl.DbAttachment)

    def test_empty_lazy_is_allowed(self):
        # when
        attachment = self.pl.DbAttachment('attachment', lazy={})
        # then
        self.assertIsInstance(attachment, self.pl.DbAttachment)

    def test_non_empty_lazy_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl.DbAttachment,
            'attachment',
            lazy={'id': 1})
