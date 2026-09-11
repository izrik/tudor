from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class FilterGraphTest(PersistenceLayerTestBase):
    def setUp_data(self):
        self.a = self.pl.create_task('a')
        self.b = self.pl.create_task('b')
        self.c = self.pl.create_task('c')
        self.pl.add(self.a)
        self.pl.add(self.b)
        self.pl.add(self.c)
        self.pl.commit()
        # a depends on b
        self.a.dependees.append(self.b)
        # c is prioritized before a
        self.a.prioritize_before.append(self.c)
        self.pl.commit()

    def test_dependee_of(self):
        self.setUp_data()
        result = list(self.pl.get_tasks(dependee_of=self.a.id))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.b.id)

    def test_dependant_of(self):
        self.setUp_data()
        result = list(self.pl.get_tasks(dependant_of=self.b.id))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.a.id)

    def test_prioritized_before(self):
        self.setUp_data()
        result = list(self.pl.get_tasks(prioritized_before=self.a.id))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.c.id)

    def test_prioritized_after(self):
        self.setUp_data()
        result = list(self.pl.get_tasks(prioritized_after=self.c.id))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.a.id)
