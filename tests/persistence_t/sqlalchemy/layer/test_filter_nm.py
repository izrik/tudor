from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class FilterNMTest(PersistenceLayerTestBase):
    def setUp_data(self):
        self.t1 = self.pl.create_task('t1')
        self.t2 = self.pl.create_task('t2')
        self.tag1 = self.pl.create_tag('red')
        self.tag2 = self.pl.create_tag('blue')
        self.u1 = self.pl.DbUser(email='a@b')
        self.u2 = self.pl.DbUser(email='c@d')
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.tag1)
        self.pl.add(self.tag2)
        self.pl.add(self.u1)
        self.pl.add(self.u2)
        self.pl.commit()

        self.t1.tags.append(self.tag1)
        self.t2.tags.append(self.tag2)
        self.t1.users.append(self.u1)
        self.t2.users.append(self.u2)
        self.pl.commit()

    def test_get_tasks_filtered_by_tag_id(self):
        self.setUp_data()
        result = list(self.pl.get_tasks(tag_id=self.tag1.id))
        self.assertEqual(len(result), 1)

    def test_get_tasks_filtered_by_user_id(self):
        self.setUp_data()
        result = list(self.pl.get_tasks(user_id=self.u2.id))
        self.assertEqual(len(result), 1)

    def test_get_tags_filtered_by_task_id(self):
        self.setUp_data()
        result = list(self.pl.get_tags(task_id=self.t1.id))
        self.assertEqual(len(result), 1)

    def test_get_users_filtered_by_task_id(self):
        self.setUp_data()
        result = list(self.pl.get_users(task_id=self.t2.id))
        self.assertEqual(len(result), 1)

    def test_count_tasks_with_tag_id(self):
        self.setUp_data()
        self.assertEqual(self.pl.count_tasks(tag_id=self.tag1.id), 1)
