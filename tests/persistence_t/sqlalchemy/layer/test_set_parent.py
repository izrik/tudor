from persistence.sqlalchemy.layer import RecordNotFound
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class SetParentTest(PersistenceLayerTestBase):
    def setUp_data(self):
        self.t1 = self.pl.create_task('t1')
        self.t2 = self.pl.create_task('t2')
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.commit()

    def test_set_parent_to_task(self):
        self.setUp_data()
        self.pl.set_parent(self.t2.id, self.t1.id)
        self.assertEqual(self.t2.parent_id, self.t1.id)

    def test_set_parent_to_none(self):
        self.setUp_data()
        self.pl.set_parent(self.t2.id, self.t1.id)
        self.pl.set_parent(self.t2.id, None)
        self.assertIsNone(self.t2.parent_id)

    def test_set_parent_unknown_task_raises(self):
        self.setUp_data()
        with self.assertRaises(RecordNotFound):
            self.pl.set_parent(999, self.t1.id)
