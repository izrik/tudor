def auto_migrate(pl, desired_version, *, _fs=None, _print=None):
    if _fs is None:
        _fs = Filesystem()
    if _print is None:
        _print = print
    from packaging.version import parse
    desired_version_t = list(parse(desired_version).release)
    if desired_version_t[0] != 0:
        raise ValueError('Non-zero major version not supported')
    if len(desired_version_t) != 2:
        raise ValueError('Version must have two parts')
    current_version = pl.get_schema_version()
    if current_version:
        current_version = current_version.value
    if not current_version:
        current_version = '0.0'
        # create the value
        pl.execute("insert into option (key, value) "
                   "values ('__version__', '0.0');")
        pl.commit()

    current_version_t = list(parse(current_version).release)
    if current_version_t[0] != 0:
        raise ValueError('Non-zero major version not supported')
    if len(current_version_t) != 2:
        raise ValueError('Version must have two parts')
    while current_version_t < desired_version_t:
        current_version_t[1] += 1
        current_version = '.'.join(str(_) for _ in current_version_t)
        migration_dir = _fs.path_join(_fs.path_dirname(__file__), 'migrations')
        filename = _fs.path_join(migration_dir, f'v{current_version}.sql')
        if _fs.path_exists(filename):
            # run the script. if there's an error, fail fast.
            with _fs.open(filename) as f:
                script = f.read()
                _print(f'Running migration script for v{current_version}')
                pl.session.execute(script)
                pl.session.commit()
        else:
            _print(f'No migration script found for v{current_version}')
            pl.execute("update option "
                       f"set value = '{current_version}' "
                       "where key = '__version__';")
            pl.commit()

    current_version = pl.get_schema_version().value
    if current_version != desired_version:
        # set the value
        pl.execute("update option "
                   f"set value = '{desired_version}' "
                   "where key = '__version__';")
        pl.commit()


class Filesystem:
    def path_dirname(self, *args, **kwargs):
        import os
        return os.path.dirname(*args, **kwargs)

    def path_exists(self, *args, **kwargs):
        import os
        return os.path.exists(*args, **kwargs)

    def path_join(self, *args, **kwargs):
        import os.path
        return os.path.join(*args, **kwargs)

    def open(self, *args, **kwargs):
        return open(*args, **kwargs)
