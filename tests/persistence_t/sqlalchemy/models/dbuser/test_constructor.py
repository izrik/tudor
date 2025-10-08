import unittest

from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class DbUserConstructorTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()
