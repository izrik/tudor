from in_memory_persistence_layer import InMemoryPersistenceLayer
from logic_layer import LogicLayer
from tudor import generate_app


def generate_ll(db_uri='sqlite://', use_in_mem_pl=True, upload_folder=None,
                allowed_extensions=None):
    if use_in_mem_pl:
        pl = InMemoryPersistenceLayer()
        if upload_folder is None:
            upload_folder = '/tmp/tudor/uploads'
        if allowed_extensions is None:
            allowed_extensions = 'txt,pdf,png,jpg,jpeg,gif'
        ll = LogicLayer(upload_folder, allowed_extensions, pl)
        return ll
    else:
        app = generate_app(db_uri=db_uri)
        return app.ll
