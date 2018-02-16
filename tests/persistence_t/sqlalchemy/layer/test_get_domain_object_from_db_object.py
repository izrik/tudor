from persistence.in_memory.models.task import Task
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class GetDomainFromDbTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_none_yields_none(self):
        # expect
        self.assertIsNone(self.pl._get_domain_object_from_db_object(None))

    def test_cache_none_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl._get_domain_object_from_db_object_in_cache,
            None)

    def test_not_db_object_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl._get_domain_object_from_db_object,
            1)
        # expect
        self.assertRaises(
            Exception,
            self.pl._get_domain_object_from_db_object,
            Task('task'))

    def test_cached_not_db_object_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl._get_domain_object_from_db_object_in_cache,
            1)
        # expect
        self.assertRaises(
            Exception,
            self.pl._get_domain_object_from_db_object_in_cache,
            Task('task'))
