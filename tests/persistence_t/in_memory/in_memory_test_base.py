import unittest

from persistence.sqlalchemy.layer import SqlAlchemyPersistenceLayer


class InMemoryTestBase(unittest.TestCase):
    def generate_pl(self, db_uri='sqlite://'):
        pl = InMemoryPersistenceLayer()
        return pl
