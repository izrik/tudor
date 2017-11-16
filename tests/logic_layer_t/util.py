from in_memory_persistence_layer import InMemoryPersistenceLayer
from logic_layer import LogicLayer
from tudor import generate_app


def generate_ll(db_uri='sqlite://', use_in_mem_pl=False):
    if use_in_mem_pl:
        pl = InMemoryPersistenceLayer()
        ll = LogicLayer('/tmp/tudor/uploads', 'txt,pdf,png,jpg,jpeg,gif', pl)
        return ll
    else:
        app = generate_app(db_uri=db_uri)
        return app.ll
