from in_memory_persistence_layer import InMemoryPersistenceLayer


class InMemoryTestBase(object):
    def generate_pl(self, db_uri='sqlite://'):
        pl = InMemoryPersistenceLayer()
        return pl
