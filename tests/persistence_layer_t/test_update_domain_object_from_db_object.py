import unittest

from tests.persistence_layer_t.util import generate_pl


class UpdateDomainObjectFromDbObjectTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_domobj_none_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl._update_domain_object_from_db_object,
            None)
