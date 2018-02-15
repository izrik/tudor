from tests.persistence_t.persistence_layer.util import PersistenceLayerTestBase


class UpdateDomainObjectFromDbObjectTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_domobj_none_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl._update_domain_object_from_db_object,
            None)
