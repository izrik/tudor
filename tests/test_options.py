import unittest

from unittest.mock import Mock

from persistence.in_memory.layer import InMemoryPersistenceLayer
from tudor import generate_app


class AppOptionsTest(unittest.TestCase):
    def setUp(self):
        self.pl = Mock(spec=InMemoryPersistenceLayer)
        self.pl.get_option.return_value = None
        self.app = generate_app(vl=Mock(), ll=Mock(), pl=self.pl,
                                flask_configs={'LOGIN_DISABLED': True},
                                secret_key='12345', disable_admin_check=True)
        self.ops = self.app.Options

    def test_get_when_none_returns_none(self):
        # when
        result = self.ops.get('some-key-name')
        # then
        self.assertIsNone(result)

    def test_get_when_none_returns_default_value(self):
        # when
        result = self.ops.get('some-key-name', 'default-value')
        # then
        self.assertEqual('default-value', result)

    def test_get_title_returns_title(self):
        # expect
        self.assertEqual('Tudor', self.ops.get_title())

    # def test_get_revision_returns_revision(self):
    #     # expect
    #     self.assertEqual('unknown', self.ops.get_revision())

    def test_get_version_returns_revision(self):
        # expect
        self.assertEqual('0.9', self.ops.get_version())
