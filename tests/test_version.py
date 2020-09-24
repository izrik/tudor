import unittest

from unittest.mock import Mock

from tudor import generate_app


class VersionTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(vl=Mock(), ll=Mock(), pl=Mock(),
                                flask_configs={'LOGIN_DISABLED': True},
                                secret_key='12345', disable_admin_check=True)

    def test_version_number_is_correct(self):
        # expect
        self.assertEqual('0.5', self.app.Options.get_version())
