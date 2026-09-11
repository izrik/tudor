from persistence.sqlalchemy.layer import RecordNotFound
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class AssociationSettersTest(PersistenceLayerTestBase):
    def setUp_data(self):
        self.t1 = self.pl.create_task('t1')
        self.t2 = self.pl.create_task('t2')
        self.tag = self.pl.create_tag('red')
        self.u = self.pl.DbUser(email='a@b')
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.tag)
        self.pl.add(self.u)
        self.pl.commit()

    def test_add_tag_to_task(self):
        self.setUp_data()
        self.pl.add_tag_to_task(self.t1.id, self.tag.id)
        self.assertIn(self.tag, self.t1.tags)

    def test_add_tag_to_task_is_idempotent(self):
        self.setUp_data()
        self.pl.add_tag_to_task(self.t1.id, self.tag.id)
        self.pl.add_tag_to_task(self.t1.id, self.tag.id)
        self.assertEqual(list(self.t1.tags).count(self.tag), 1)

    def test_remove_tag_from_task(self):
        self.setUp_data()
        self.pl.add_tag_to_task(self.t1.id, self.tag.id)
        self.pl.remove_tag_from_task(self.t1.id, self.tag.id)
        self.assertNotIn(self.tag, self.t1.tags)

    def test_add_tag_to_unknown_task_raises(self):
        self.setUp_data()
        with self.assertRaises(RecordNotFound):
            self.pl.add_tag_to_task(999, self.tag.id)

    def test_add_user_to_task(self):
        self.setUp_data()
        self.pl.add_user_to_task(self.t1.id, self.u.id)
        self.assertIn(self.u, self.t1.users)

    def test_add_dependency(self):
        self.setUp_data()
        self.pl.add_dependency(self.t1.id, self.t2.id)
        self.assertIn(self.t2, self.t1.dependees)

    def test_remove_dependency(self):
        self.setUp_data()
        self.pl.add_dependency(self.t1.id, self.t2.id)
        self.pl.remove_dependency(self.t1.id, self.t2.id)
        self.assertNotIn(self.t2, self.t1.dependees)

    def test_add_priority(self):
        self.setUp_data()
        self.pl.add_priority(self.t1.id, self.t2.id)
        self.assertIn(self.t1, self.t2.prioritize_before)

    def test_remove_priority(self):
        self.setUp_data()
        self.pl.add_priority(self.t1.id, self.t2.id)
        self.pl.remove_priority(self.t1.id, self.t2.id)
        self.assertNotIn(self.t1, self.t2.prioritize_before)
