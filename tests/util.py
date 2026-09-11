from io import StringIO

from sqlalchemy import event

from tudor import generate_app


def generate_test_app(db_uri='sqlite://', upload_folder=None,
                      allowed_extensions=None):
    """Return an app with an empty database and an app context pushed.

    The autouse fixture in tests/conftest.py pops the context after each
    test.
    """
    if upload_folder is None:
        upload_folder = '/tmp/tudor/uploads'
    if allowed_extensions is None:
        allowed_extensions = 'txt,pdf,png,jpg,jpeg,gif'
    key = (db_uri, upload_folder, allowed_extensions)
    app = _apps.get(key)
    is_new_app = app is None
    if is_new_app:
        # Building the app compiles every route (~50ms), so do it once per
        # process and reset the schema for each test instead.
        app = generate_app(db_uri=db_uri, upload_folder=upload_folder,
                           allowed_extensions=allowed_extensions)
        _apps[key] = app
    ctx = app.app_context()
    ctx.push()
    _pushed_contexts.append(ctx)
    db = app.pl.db
    if is_new_app and db_uri.startswith('sqlite'):
        event.listen(db.engine, 'connect', _enable_sqlite_foreign_keys)
    db.session.remove()
    db.drop_all()
    db.create_all()
    return app


def pop_app_contexts():
    while _pushed_contexts:
        _pushed_contexts.pop().pop()


def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    # Postgres always enforces foreign keys; SQLite only does when asked.
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()


_apps = {}
_pushed_contexts = []


class MockFileObject(object):
    def __init__(self, filename, content=None):
        self.filename = filename
        self.content = content
        self._s = StringIO(content)
        self.save_calls = []

    def save(self, filepath):
        self.save_calls.append(filepath)

    def read(self, *args, **kwargs):
        return self._s.read(*args, **kwargs)
