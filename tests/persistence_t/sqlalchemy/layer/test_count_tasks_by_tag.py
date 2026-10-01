from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class CountTasksByTagTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()
        self.tag1 = self.pl.create_tag('tag1')
        self.tag2 = self.pl.create_tag('tag2')
        self.tag3 = self.pl.create_tag('tag3')
        self.user = self.pl.create_user('user@example.org')
        self.other = self.pl.create_user('other@example.org')
        self.public = self.pl.create_task('public', is_public=True)
        self.mine = self.pl.create_task('mine')
        self.theirs = self.pl.create_task('theirs')
        self.done = self.pl.create_task('done', is_public=True, is_done=True)
        self.deleted = self.pl.create_task('deleted', is_public=True,
                                           is_deleted=True)
        self.public.tags.extend([self.tag1, self.tag2])
        self.public.users.extend([self.user, self.other])
        self.mine.tags.append(self.tag1)
        self.mine.users.append(self.user)
        self.theirs.tags.append(self.tag1)
        self.theirs.users.append(self.other)
        self.done.tags.append(self.tag2)
        self.deleted.tags.append(self.tag2)
        for obj in [self.tag1, self.tag2, self.tag3, self.user, self.other,
                    self.public, self.mine, self.theirs, self.done,
                    self.deleted]:
            self.pl.add(obj)
        self.pl.commit()

    def test_empty_tag_ids_returns_empty_dict(self):
        # expect
        self.assertEqual({}, self.pl.count_tasks_by_tag([]))

    def test_counts_all_tasks_including_done_and_deleted(self):
        # when
        result = self.pl.count_tasks_by_tag(
            [self.tag1.id, self.tag2.id, self.tag3.id])
        # then
        self.assertEqual({self.tag1.id: 3, self.tag2.id: 3}, result)

    def test_only_counts_requested_tags(self):
        # when
        result = self.pl.count_tasks_by_tag([self.tag2.id])
        # then
        self.assertEqual({self.tag2.id: 3}, result)

    def test_is_public_only_counts_public_tasks(self):
        # when
        result = self.pl.count_tasks_by_tag([self.tag1.id, self.tag2.id],
                                            is_public=True)
        # then
        self.assertEqual({self.tag1.id: 1, self.tag2.id: 3}, result)

    def test_is_public_or_users_contains_counts_each_task_once(self):
        # when
        result = self.pl.count_tasks_by_tag(
            [self.tag1.id, self.tag2.id],
            is_public_or_users_contains=self.user)
        # then
        self.assertEqual({self.tag1.id: 2, self.tag2.id: 3}, result)
