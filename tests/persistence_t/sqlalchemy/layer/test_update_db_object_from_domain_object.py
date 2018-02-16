import unittest

from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class UpdateDbObjectFromDomainObjectTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_domobj_none_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl._update_db_object_from_domain_object,
            None)
