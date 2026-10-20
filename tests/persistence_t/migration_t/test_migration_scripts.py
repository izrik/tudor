import os

import pytest

from persistence.migration import (get_highest_migration_version,
                                   get_migration_scripts,
                                   parse_schema_version)
from tests.persistence_t.migration_t.test_auto_migrate import mock_fs


@pytest.mark.parametrize('value, expected', [
    (None, 0),
    ('', 0),
    ('  ', 0),
    ('0', 0),
    # values stored by versions of Tudor that numbered the schema 0.x
    ('0.0', 0),
    ('0.1', 1),
    ('0.10', 10),
    ('0.17', 17),
    # the plain sequence that replaced them
    ('18', 18),
    ('100', 100),
    (18, 18),
])
def test_parse_schema_version(value, expected):
    assert parse_schema_version(value) == expected


@pytest.mark.parametrize('value', ['banana', '1.2', '1.2.3', '0.1.1', 'v0.1'])
def test_parse_schema_version_rejects_nonsense(value):
    with pytest.raises(ValueError):
        parse_schema_version(value)


def test_get_migration_scripts_sorts_numerically_not_lexically():
    # given
    fs = mock_fs({'0100-hundred.sql': '', '0020-twenty.sql': '',
                  '0003-three.sql': ''})
    # when
    scripts = get_migration_scripts(_fs=fs)
    # then
    assert [v for v, _ in scripts] == [3, 20, 100]


def test_get_migration_scripts_ignores_other_files():
    # given
    fs = mock_fs({'.place_holder': '', 'notes.txt': '', 'readme.sql': '',
                  '0003-three.sql': ''})
    # when
    scripts = get_migration_scripts(_fs=fs)
    # then
    assert [v for v, _ in scripts] == [3]


def test_get_highest_migration_version_with_no_scripts():
    assert get_highest_migration_version(_fs=mock_fs()) == 0


def test_the_scripts_in_the_repo_are_all_recognized():
    # given
    migrations_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))),
        'persistence', 'migrations')
    on_disk = {f for f in os.listdir(migrations_dir) if f.endswith('.sql')}
    # when
    scripts = get_migration_scripts()
    # then every .sql file in the directory is one we know how to apply
    assert {os.path.basename(p) for _, p in scripts} == on_disk
    # and no two of them claim the same place in the sequence
    versions = [v for v, _ in scripts]
    assert len(set(versions)) == len(versions)
    # and the highest of them is the version a new database gets
    assert get_highest_migration_version() == max(versions)
