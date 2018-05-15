import os
import unittest

from mock import Mock

from persistence.in_memory.layer import InMemoryPersistenceLayer
from tudor import make_task_public, make_task_private, Config, \
    get_config_from_command_line, generate_app


class VersionTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(vl=Mock(), ll=Mock(), pl=Mock(),
                                flask_configs={'LOGIN_DISABLED': True},
                                secret_key='12345', disable_admin_check=True)

    def test_version_number_is_correct(self):
        # expect
        self.assertEqual('0.1', self.app.Options.get_version())
