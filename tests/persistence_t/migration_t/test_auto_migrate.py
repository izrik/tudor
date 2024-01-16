import contextlib
import re
from unittest.mock import Mock, call

import pytest

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
        if sql == 'do the thing;':
            return
        m = re.search("value = '([\\d.]+)'", sql)
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
    pl.execute.assert_called_with(
        "update option set value = '0.2' where key = '__version__';")
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
    assert call('do the thing;') in pl.execute.mock_calls
    set_version = "update option set value = '0.2' " \
                  "where key = '__version__';"
    assert call(set_version) in pl.execute.mock_calls
    pl.commit.assert_called()
