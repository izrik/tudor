import re
from sqlalchemy import text

# The key, in the option table, under which the schema version is stored.
SCHEMA_VERSION_KEY = '__schema_version__'
# What that key was called before it was renamed to say what it is. Read
# for the benefit of databases that pre-date the rename; never written.
LEGACY_SCHEMA_VERSION_KEY = '__version__'

# A migration script is named for its position in the sequence, with an
# optional description after it: 0018-add-comment-author.sql
_SCRIPT_RE = re.compile(r'^(\d+)(?:-[^.]*)?\.sql$')
# Scripts from before the renumbering look like a version number,
# v0.18.sql, but the minor part was only ever a sequence number.
_LEGACY_SCRIPT_RE = re.compile(r'^v0+\.(\d+)\.sql$')
# ... and so was the value stored in the database, e.g. '0.18'.
_LEGACY_VERSION_RE = re.compile(r'^0+\.(\d+)$')


def parse_schema_version(value):
    """Return the sequence number of a schema version read from the db.

    Databases written before the renumbering hold a two-part value such
    as '0.17', whose minor part is the position in the sequence.
    """
    if value is None:
        return 0
    value = str(value).strip()
    if not value:
        return 0
    m = _LEGACY_VERSION_RE.match(value)
    if m:
        return int(m.group(1))
    if value.isdigit():
        return int(value)
    raise ValueError(f'Unrecognized schema version: {value!r}')


def get_migration_scripts(_fs=None):
    """Return the available migration scripts, lowest version first.

    Each element is a (version, path) pair. The sequence may have gaps;
    all that matters is the order.
    """
    if _fs is None:
        _fs = Filesystem()
    migrations_dir = _fs.path_join(_fs.path_dirname(__file__), 'migrations')
    scripts = []
    for fname in _fs.listdir(migrations_dir):
        m = _SCRIPT_RE.match(fname) or _LEGACY_SCRIPT_RE.match(fname)
        if m:
            path = _fs.path_join(migrations_dir, fname)
            scripts.append((int(m.group(1)), path))
    scripts.sort()
    return scripts


def get_highest_migration_version(_fs=None):
    """Return the schema version the migration scripts add up to."""
    scripts = get_migration_scripts(_fs=_fs)
    return scripts[-1][0] if scripts else 0


def get_current_schema_version(pl):
    """Return the schema version recorded in the database."""
    option = pl.get_schema_version()
    if option is None:
        return 0
    return parse_schema_version(option.value)


def set_schema_version(pl, version):
    """Record the schema version, under the current key and no other."""
    pl.execute(text("delete from option where key in "
                    f"('{SCHEMA_VERSION_KEY}', "
                    f"'{LEGACY_SCHEMA_VERSION_KEY}');"))
    pl.execute(text("insert into option (key, value) "
                    f"values ('{SCHEMA_VERSION_KEY}', '{version}');"))
    pl.commit()


def auto_migrate(pl, desired_version=None, *, _fs=None, _print=None):
    """Bring the database schema up to desired_version.

    Every script newer than the recorded version and no newer than the
    desired one is run, in order. The recorded version is advanced after
    each script, so an interrupted run resumes where it left off.
    """
    if _fs is None:
        _fs = Filesystem()
    if _print is None:
        _print = print

    scripts = get_migration_scripts(_fs=_fs)
    if desired_version is None:
        desired_version = scripts[-1][0] if scripts else 0
    else:
        desired_version = parse_schema_version(desired_version)

    option = pl.get_schema_version()
    current_version = parse_schema_version(option.value) if option else 0
    if option is None or option.key != SCHEMA_VERSION_KEY:
        # Either the database has never been stamped with a version, or
        # it still holds one under the key's old name.
        set_schema_version(pl, current_version)

    for version, filename in scripts:
        if version <= current_version or version > desired_version:
            continue
        # Run the script. If there's an error, fail fast.
        with _fs.open(filename) as f:
            script = f.read()
        _print(f'Running migration script {_fs.path_basename(filename)}')
        pl.execute(text(script))
        set_schema_version(pl, version)
        current_version = version


class Filesystem:
    def path_basename(self, *args, **kwargs):
        import os
        return os.path.basename(*args, **kwargs)

    def path_dirname(self, *args, **kwargs):
        import os
        return os.path.dirname(*args, **kwargs)

    def path_join(self, *args, **kwargs):
        import os.path
        return os.path.join(*args, **kwargs)

    def listdir(self, *args, **kwargs):
        import os
        return os.listdir(*args, **kwargs)

    def open(self, *args, **kwargs):
        return open(*args, **kwargs)
