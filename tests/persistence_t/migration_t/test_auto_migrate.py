import contextlib
import re
from unittest.mock import Mock, call

import pytest
from sqlalchemy import text

from persistence.migration import auto_migrate
from models.option_base import OptionBase


def mock_pl(version=None):
    if version is None:
        version = '0.1'

    pl = Mock()
    pl.version = version

    def get_schema_version():
        return OptionBase('__version__', pl.version)

    pl.get_schema_version.side_effect = get_schema_version

    def execute(sql):
        sql_str = str(sql)
        if sql_str == 'do the thing;':
            return
        m = re.search("value = '([\\d.]+)'", sql_str)
        if m:
            pl.version = m.group(1)
            return
        raise Exception('Unrecognized sql')

    pl.session.execute.side_effect = execute
    return pl


def mock_fs():
    fs = Mock()
    fs.path_exists.return_value = False
    return fs


def test_upgrade_script_not_present():
    # given
    pl = mock_pl()
    fs = mock_fs()
    _print = Mock()
    # when
    auto_migrate(pl, '0.2', _fs=fs, _print=_print)
    # then
    pl.get_schema_version.assert_called()
    executed = [str(c.args[0]) for c in pl.execute.call_args_list]
    assert "update option set value = '0.2' where key = '__version__';" in executed
    pl.commit.assert_called()


def test_invalid_desired_version_1():
    # given
    pl = mock_pl()
    fs = mock_fs()
    _print = Mock()
    # expect
    with pytest.raises(ValueError) as exc:
        auto_migrate(pl, '0.2.1', _fs=fs, _print=_print)
    # and
    assert str(exc.value) == 'Version must have two parts'


def test_invalid_desired_version_2():
    # given
    pl = mock_pl()
    fs = mock_fs()
    _print = Mock()
    # expect
    with pytest.raises(ValueError) as exc:
        auto_migrate(pl, '1.2', _fs=fs, _print=_print)
    # and
    assert str(exc.value) == 'Non-zero major version not supported'


def test_invalid_current_version_1():
    # given
    pl = mock_pl('0.1.1')
    fs = mock_fs()
    _print = Mock()
    # expect
    with pytest.raises(ValueError) as exc:
        auto_migrate(pl, '0.2', _fs=fs, _print=_print)
    # and
    assert str(exc.value) == 'Version must have two parts'


def test_invalid_current_version_2():
    # given
    pl = mock_pl('1.2')
    fs = mock_fs()
    _print = Mock()
    # expect
    with pytest.raises(ValueError) as exc:
        auto_migrate(pl, '0.2', _fs=fs, _print=_print)
    # and
    assert str(exc.value) == 'Non-zero major version not supported'


def test_upgrade_script_present():
    # given
    pl = mock_pl()
    fs = mock_fs()

    def path_exists(path):
        return path.endswith('/v0.2.sql')

    fs.path_exists.side_effect = path_exists

    @contextlib.contextmanager
    def _open(path):
        f = Mock()
        f.read.return_value = 'do the thing;'
        yield f

    fs.open.side_effect = _open
    _print = Mock()
    # when
    auto_migrate(pl, '0.2', _fs=fs, _print=_print)
    # then
    pl.get_schema_version.assert_called()
    assert pl.execute.call_count == 2
    executed = [str(c.args[0]) for c in pl.execute.call_args_list]
    assert 'do the thing;' in executed
    assert "update option set value = '0.2' where key = '__version__';" in executed
    pl.commit.assert_called()
