import contextlib
import re
from unittest.mock import Mock

import pytest

from models.option_base import OptionBase
from persistence.migration import (LEGACY_SCHEMA_VERSION_KEY,
                                   SCHEMA_VERSION_KEY, auto_migrate)


def mock_pl(version=None, key=SCHEMA_VERSION_KEY):
    """A persistence layer that remembers what's in the option table."""
    pl = Mock()
    pl.options = {} if version is None else {key: version}
    pl.scripts_run = []

    def get_schema_version():
        for k in (SCHEMA_VERSION_KEY, LEGACY_SCHEMA_VERSION_KEY):
            if k in pl.options:
                return OptionBase(k, pl.options[k])
        return None

    pl.get_schema_version.side_effect = get_schema_version

    def execute(stmt):
        sql = ' '.join(str(stmt).split())
        if sql.startswith('delete from option'):
            for k in re.findall(r"'([^']*)'", sql):
                pl.options.pop(k, None)
            return
        m = re.match(r"insert into option \(key, value\) "
                     r"values \('([^']*)', '([^']*)'\);", sql)
        if m:
            pl.options[m.group(1)] = m.group(2)
            return
        pl.scripts_run.append(sql)

    pl.execute.side_effect = execute
    return pl


def mock_fs(scripts=None):
    """A filesystem holding the given {filename: contents} scripts."""
    if scripts is None:
        scripts = {}
    fs = Mock()
    fs.path_join.side_effect = lambda *parts: '/'.join(parts)
    fs.path_dirname.side_effect = lambda path: path.rsplit('/', 1)[0]
    fs.path_basename.side_effect = lambda path: path.rsplit('/', 1)[-1]
    fs.listdir.side_effect = lambda d: list(scripts)

    @contextlib.contextmanager
    def _open(path):
        f = Mock()
        f.read.return_value = scripts[path.rsplit('/', 1)[-1]]
        yield f

    fs.open.side_effect = _open
    return fs


def test_no_scripts_at_all():
    # given
    pl = mock_pl('3')
    fs = mock_fs()
    _print = Mock()
    # when
    auto_migrate(pl, 3, _fs=fs, _print=_print)
    # then
    assert pl.scripts_run == []
    assert pl.options == {SCHEMA_VERSION_KEY: '3'}


def test_already_up_to_date():
    # given
    pl = mock_pl('2')
    fs = mock_fs({'0001-one.sql': 'do one;', '0002-two.sql': 'do two;'})
    _print = Mock()
    # when
    auto_migrate(pl, 2, _fs=fs, _print=_print)
    # then
    assert pl.scripts_run == []
    assert pl.options == {SCHEMA_VERSION_KEY: '2'}


def test_runs_the_scripts_above_the_current_version():
    # given
    pl = mock_pl('1')
    fs = mock_fs({'0001-one.sql': 'do one;', '0002-two.sql': 'do two;',
                  '0003-three.sql': 'do three;'})
    _print = Mock()
    # when
    auto_migrate(pl, 3, _fs=fs, _print=_print)
    # then
    assert pl.scripts_run == ['do two;', 'do three;']
    assert pl.options == {SCHEMA_VERSION_KEY: '3'}
    pl.commit.assert_called()


def test_runs_the_scripts_in_order_regardless_of_listing_order():
    # given
    pl = mock_pl()
    fs = mock_fs({'0010-ten.sql': 'do ten;', '0002-two.sql': 'do two;',
                  '0100-hundred.sql': 'do a hundred;'})
    _print = Mock()
    # when
    auto_migrate(pl, 100, _fs=fs, _print=_print)
    # then
    assert pl.scripts_run == ['do two;', 'do ten;', 'do a hundred;']
    assert pl.options == {SCHEMA_VERSION_KEY: '100'}


def test_stops_at_the_desired_version():
    # given
    pl = mock_pl('1')
    fs = mock_fs({'0002-two.sql': 'do two;', '0003-three.sql': 'do three;'})
    _print = Mock()
    # when
    auto_migrate(pl, 2, _fs=fs, _print=_print)
    # then
    assert pl.scripts_run == ['do two;']
    assert pl.options == {SCHEMA_VERSION_KEY: '2'}


def test_defaults_to_the_highest_available_version():
    # given
    pl = mock_pl('1')
    fs = mock_fs({'0002-two.sql': 'do two;', '0003-three.sql': 'do three;'})
    _print = Mock()
    # when
    auto_migrate(pl, _fs=fs, _print=_print)
    # then
    assert pl.scripts_run == ['do two;', 'do three;']
    assert pl.options == {SCHEMA_VERSION_KEY: '3'}


def test_gaps_in_the_sequence_are_not_reported_as_missing_scripts():
    # given
    pl = mock_pl('1')
    fs = mock_fs({'0007-seven.sql': 'do seven;'})
    _print = Mock()
    # when
    auto_migrate(pl, 7, _fs=fs, _print=_print)
    # then
    assert pl.scripts_run == ['do seven;']
    printed = [c.args[0] for c in _print.call_args_list]
    assert printed == ['Running migration script 0007-seven.sql']


def test_non_sql_files_are_ignored():
    # given
    pl = mock_pl()
    fs = mock_fs({'.place_holder': '', 'README.md': 'hi',
                  '0001-one.sql': 'do one;'})
    _print = Mock()
    # when
    auto_migrate(pl, 1, _fs=fs, _print=_print)
    # then
    assert pl.scripts_run == ['do one;']


def test_non_zero_major_version_is_supported():
    # given a database stamped in the old two-part style
    pl = mock_pl('0.17', key=LEGACY_SCHEMA_VERSION_KEY)
    # and scripts that carry the sequence past where a 0.x version
    # would have had to roll over
    fs = mock_fs({'0018-eighteen.sql': 'do eighteen;',
                  '0100-hundred.sql': 'do a hundred;'})
    _print = Mock()
    # when
    auto_migrate(pl, 100, _fs=fs, _print=_print)
    # then
    assert pl.scripts_run == ['do eighteen;', 'do a hundred;']
    assert pl.options == {SCHEMA_VERSION_KEY: '100'}


def test_legacy_scripts_are_still_recognized():
    # given
    pl = mock_pl('0.16', key=LEGACY_SCHEMA_VERSION_KEY)
    fs = mock_fs({'v0.16.sql': 'do sixteen;', 'v0.17.sql': 'do seventeen;',
                  '0018-eighteen.sql': 'do eighteen;'})
    _print = Mock()
    # when
    auto_migrate(pl, 18, _fs=fs, _print=_print)
    # then
    assert pl.scripts_run == ['do seventeen;', 'do eighteen;']
    assert pl.options == {SCHEMA_VERSION_KEY: '18'}


def test_legacy_version_key_is_renamed():
    # given
    pl = mock_pl('0.14', key=LEGACY_SCHEMA_VERSION_KEY)
    fs = mock_fs({'0015-fifteen.sql': 'do fifteen;'})
    _print = Mock()
    # when
    auto_migrate(pl, 15, _fs=fs, _print=_print)
    # then the old key is gone and only the new one remains
    assert pl.options == {SCHEMA_VERSION_KEY: '15'}


def test_legacy_version_key_is_renamed_even_with_nothing_to_run():
    # given
    pl = mock_pl('0.15', key=LEGACY_SCHEMA_VERSION_KEY)
    fs = mock_fs({'0015-fifteen.sql': 'do fifteen;'})
    _print = Mock()
    # when
    auto_migrate(pl, 15, _fs=fs, _print=_print)
    # then
    assert pl.scripts_run == []
    assert pl.options == {SCHEMA_VERSION_KEY: '15'}


def test_unstamped_database_is_stamped_and_migrated_from_zero():
    # given
    pl = mock_pl()
    fs = mock_fs({'0001-one.sql': 'do one;', '0002-two.sql': 'do two;'})
    _print = Mock()
    # when
    auto_migrate(pl, 2, _fs=fs, _print=_print)
    # then
    assert pl.scripts_run == ['do one;', 'do two;']
    assert pl.options == {SCHEMA_VERSION_KEY: '2'}


def test_version_is_recorded_after_each_script():
    # given a script that fails part-way through the run
    pl = mock_pl()
    fs = mock_fs({'0001-one.sql': 'do one;', '0002-two.sql': 'explode;'})
    _print = Mock()

    def execute(stmt):
        if str(stmt) == 'explode;':
            raise Exception('nope')
        return pl.execute.side_effect_orig(stmt)

    pl.execute.side_effect_orig = pl.execute.side_effect
    pl.execute.side_effect = execute
    # when
    with pytest.raises(Exception):
        auto_migrate(pl, 2, _fs=fs, _print=_print)
    # then the work that did succeed has been recorded
    assert pl.options == {SCHEMA_VERSION_KEY: '1'}


def test_unrecognized_current_version():
    # given
    pl = mock_pl('banana')
    fs = mock_fs()
    _print = Mock()
    # expect
    with pytest.raises(ValueError) as exc:
        auto_migrate(pl, 1, _fs=fs, _print=_print)
    # and
    assert str(exc.value) == "Unrecognized schema version: 'banana'"


def test_unrecognized_desired_version():
    # given
    pl = mock_pl()
    fs = mock_fs()
    _print = Mock()
    # expect
    with pytest.raises(ValueError) as exc:
        auto_migrate(pl, '1.2.3', _fs=fs, _print=_print)
    # and
    assert str(exc.value) == "Unrecognized schema version: '1.2.3'"
