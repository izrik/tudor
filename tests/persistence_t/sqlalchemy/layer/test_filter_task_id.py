from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class FilterByTaskIdTest(PersistenceLayerTestBase):
    def setUp_data(self):
        self.t1 = self.pl.create_task('t1')
        self.t2 = self.pl.create_task('t2')
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.commit()

        self.c1 = self.pl.create_comment('c1')
        self.c1.task = self.t1
        self.c2 = self.pl.create_comment('c2')
        self.c2.task = self.t1
        self.c3 = self.pl.create_comment('c3')
        self.c3.task = self.t2
        self.pl.add(self.c1)
        self.pl.add(self.c2)
        self.pl.add(self.c3)

        self.a1 = self.pl.create_attachment('/a1')
        self.a1.task = self.t1
        self.a2 = self.pl.create_attachment('/a2')
        self.a2.task = self.t2
        self.pl.add(self.a1)
        self.pl.add(self.a2)
        self.pl.commit()

    def test_get_comments_filtered_by_task_id(self):
        self.setUp_data()
        result = list(self.pl.get_comments(task_id=self.t1.id))
        self.assertEqual(len(result), 2)

    def test_count_comments_filtered_by_task_id(self):
        self.setUp_data()
        self.assertEqual(self.pl.count_comments(task_id=self.t1.id), 2)
        self.assertEqual(self.pl.count_comments(task_id=self.t2.id), 1)

    def test_get_attachments_filtered_by_task_id(self):
        self.setUp_data()
        result = list(self.pl.get_attachments(task_id=self.t1.id))
        self.assertEqual(len(result), 1)

    def test_count_attachments_filtered_by_task_id(self):
        self.setUp_data()
        self.assertEqual(self.pl.count_attachments(task_id=self.t1.id), 1)
        self.assertEqual(self.pl.count_attachments(task_id=self.t2.id), 1)
