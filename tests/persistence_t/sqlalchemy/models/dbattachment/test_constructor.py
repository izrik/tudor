import unittest

from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class DbAttachmentConstructorTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()
