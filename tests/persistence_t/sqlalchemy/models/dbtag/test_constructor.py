import unittest

from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class DbTagConstructorTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()
