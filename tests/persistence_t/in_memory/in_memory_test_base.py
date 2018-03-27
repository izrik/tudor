import unittest

from persistence.in_memory.layer import InMemoryPersistenceLayer


class InMemoryTestBase(unittest.TestCase):
    def generate_pl(self, db_uri='sqlite://'):
        pl = InMemoryPersistenceLayer()
        return pl
