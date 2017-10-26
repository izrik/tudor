import unittest

from tests.persistence_layer.util import generate_pl


class DbAttachmentConstructorTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()

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