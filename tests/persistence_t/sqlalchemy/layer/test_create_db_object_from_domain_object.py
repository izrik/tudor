from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class CreateDbFromDomainTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_none_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_db_object_from_domain_object,
            None)

    def test_not_domain_object_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_db_object_from_domain_object,
            1)
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_db_object_from_domain_object,
            self.pl.DbTask('task'))

    def test_already_cached_raises(self):
        # given
        dbtask = self.pl.DbTask('task')
        self.pl.db.session.add(dbtask)
        self.pl.db.session.commit()
        task = self.pl.get_task(dbtask.id)
        # precondition
        self.assertIn(task, self.pl._db_by_domain)
        self.assertIn(dbtask, self.pl._domain_by_db)
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_db_object_from_domain_object,
            task)
