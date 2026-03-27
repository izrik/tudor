import unittest

from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class DbTaskConstructorTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()
