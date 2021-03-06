from logic.layer import LogicLayer
from persistence.in_memory.layer import InMemoryPersistenceLayer
from tudor import generate_app


def generate_ll(db_uri='sqlite://', use_in_mem_pl=True, upload_folder=None,
                allowed_extensions=None):
    if use_in_mem_pl:
        pl = InMemoryPersistenceLayer()
        pl.create_all()
        if upload_folder is None:
            upload_folder = '/tmp/tudor/uploads'
        if allowed_extensions is None:
            allowed_extensions = 'txt,pdf,png,jpg,jpeg,gif'
        ll = LogicLayer(upload_folder, allowed_extensions, pl)
        return ll
    else:
        app = generate_app(db_uri=db_uri)
        app.pl.create_all()
        return app.ll
