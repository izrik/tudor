#!/usr/bin/env python

import unittest
from mock import Mock

from tudor import generate_app
from view_layer import ViewLayer


class RouteTest(unittest.TestCase):
    def setUp(self):
        def ds_factory(app):
            return object()
        vl = Mock(spec=ViewLayer)
        ll = Mock()
        self.app = generate_app(vl=vl, ll=ll, configs={'LOGIN_DISABLED': True})
        self.client = self.app.test_client()
        self.vl = vl

    def test_index(self):
        self.vl.index = Mock(return_value=('', 200))
        resp = self.client.get('/')
        self.assertEqual(200, resp.status_code)
        self.vl.index.assert_called()
