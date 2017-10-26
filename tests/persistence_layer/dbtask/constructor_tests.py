import unittest

from tests.persistence_layer.util import generate_pl


class DbTaskConstructorTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()

    def test_none_lazy_is_allowed(self):
        # when
        task = self.pl.DbTask('task', lazy={})
        # then
        self.assertIsInstance(task, self.pl.DbTask)

    def test_empty_lazy_is_allowed(self):
        # when
        task = self.pl.DbTask('task', lazy={})
        # then
        self.assertIsInstance(task, self.pl.DbTask)

    def test_non_empty_lazy_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.DbTask, 'task', lazy={'id': 1})