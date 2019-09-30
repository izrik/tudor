#!/usr/bin/env python

import unittest
from unittest.mock import Mock

from logic.layer import LogicLayer
from persistence.in_memory.layer import InMemoryPersistenceLayer


class GetUsersTest(unittest.TestCase):
    def setUp(self):
        upload_folder = '/tmp/tudor/uploads'
        allowed_extensions = 'txt,pdf,png,jpg,jpeg,gif'
        self.pl = Mock(spec=InMemoryPersistenceLayer)
        self.data = object()
        self.pl.get_users.return_value = self.data
        self.ll = LogicLayer(upload_folder, allowed_extensions, self.pl)

    def test_returns_results_from_pl(self):
        # expect
        self.assertIs(self.data, self.ll.get_users())
