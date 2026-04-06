
from models.object_types import ObjectTypes
from tests.persistence_t.in_memory.in_memory_test_base import InMemoryTestBase


# not copied from any other file


class GetObjectTypeTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_get_object_type_task_returns_task(self):
        # given
        task = self.pl.create_task('task1')
        # when
        result = self.pl._get_object_type(task)
        # then
        self.assertEqual(ObjectTypes.Task, result)

    def test_get_object_type_tag_returns_tag(self):
        # given
        tag = self.pl.create_tag('tag1')
        # when
        result = self.pl._get_object_type(tag)
        # then
        self.assertEqual(ObjectTypes.Tag, result)

    def test_get_object_type_attachment_returns_attachment(self):
        # given
        attachment = self.pl.create_attachment('attachment1')
        # when
        result = self.pl._get_object_type(attachment)
        # then
        self.assertEqual(ObjectTypes.Attachment, result)

    def test_get_object_type_comment_returns_comment(self):
        # given
        comment = self.pl.create_comment('comment1')
        # when
        result = self.pl._get_object_type(comment)
        # then
        self.assertEqual(ObjectTypes.Comment, result)

    def test_get_object_type_user_returns_user(self):
        # given
        user = self.pl.create_user('user1')
        # when
        result = self.pl._get_object_type(user)
        # then
        self.assertEqual(ObjectTypes.User, result)

    def test_get_object_type_option_returns_option(self):
        # given
        option = self.pl.create_option('key', 'value')
        # when
        result = self.pl._get_object_type(option)
        # then
        self.assertEqual(ObjectTypes.Option, result)

    def test_get_object_type_non_domain_object_raises(self):
        # expect
        with self.assertRaises(Exception) as cm:
            self.pl._get_object_type('something')
        # then
        self.assertEqual('Not a domain object: something, str',
                         str(cm.exception))


class GetNextObjectIdsTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_get_next_task_id_no_tasks_returns_one(self):
        # precondition
        self.assertEqual(0, len(self.pl._tasks))
        # when
        result = self.pl._get_next_task_id()
        # then
        self.assertEqual(1, result)

    def test_get_next_task_id_some_tasks_returns_max_plus_one(self):
        # given
        task = self.pl.create_task('task')
        task.id = 3
        self.pl.add(task)
        self.pl.commit()
        # precondition
        self.assertEqual(1, len(self.pl._tasks))
        self.assertEqual(3, self.pl._tasks[0].id)
        # when
        result = self.pl._get_next_task_id()
        # then
        self.assertEqual(4, result)

    def test_get_next_tag_id_no_tags_returns_one(self):
        # precondition
        self.assertEqual(0, len(self.pl._tags))
        # when
        result = self.pl._get_next_tag_id()
        # then
        self.assertEqual(1, result)

    def test_get_next_tag_id_some_tags_returns_max_plus_one(self):
        # given
        tag = self.pl.create_tag('tag')
        tag.id = 3
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertEqual(1, len(self.pl._tags))
        self.assertEqual(3, self.pl._tags[0].id)
        # when
        result = self.pl._get_next_tag_id()
        # then
        self.assertEqual(4, result)

    def test_get_next_attachment_id_no_attachments_returns_one(self):
        # precondition
        self.assertEqual(0, len(self.pl._attachments))
        # when
        result = self.pl._get_next_attachment_id()
        # then
        self.assertEqual(1, result)

    def test_get_next_attachment_id_some_attachments_return_max_plus_one(self):
        # given
        attachment = self.pl.create_attachment('attachment')
        attachment.id = 3
        self.pl.add(attachment)
        self.pl.commit()
        # precondition
        self.assertEqual(1, len(self.pl._attachments))
        self.assertEqual(3, self.pl._attachments[0].id)
        # when
        result = self.pl._get_next_attachment_id()
        # then
        self.assertEqual(4, result)

    def test_get_next_comment_id_no_comments_returns_one(self):
        # precondition
        self.assertEqual(0, len(self.pl._comments))
        # when
        result = self.pl._get_next_comment_id()
        # then
        self.assertEqual(1, result)

    def test_get_next_comment_id_some_comments_returns_max_plus_one(self):
        # given
        comment = self.pl.create_comment('comment')
        comment.id = 3
        self.pl.add(comment)
        self.pl.commit()
        # precondition
        self.assertEqual(1, len(self.pl._comments))
        self.assertEqual(3, self.pl._comments[0].id)
        # when
        result = self.pl._get_next_comment_id()
        # then
        self.assertEqual(4, result)

    def test_get_next_user_id_no_users_returns_one(self):
        # precondition
        self.assertEqual(0, len(self.pl._users))
        # when
        result = self.pl._get_next_user_id()
        # then
        self.assertEqual(1, result)

    def test_get_next_user_id_some_users_returns_max_plus_one(self):
        # given
        user = self.pl.create_user('user')
        user.id = 3
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertEqual(1, len(self.pl._users))
        self.assertEqual(3, self.pl._users[0].id)
        # when
        result = self.pl._get_next_user_id()
        # then
        self.assertEqual(4, result)


class GetNextIdTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        task = self.pl.create_task('task')
        task.id = 3
        self.pl.add(task)
        tag = self.pl.create_tag('tag')
        tag.id = 5
        self.pl.add(tag)
        attachment = self.pl.create_attachment('attachment')
        attachment.id = 7
        self.pl.add(attachment)
        comment = self.pl.create_comment('comment')
        comment.id = 9
        self.pl.add(comment)
        user = self.pl.create_user('user')
        user.id = 11
        self.pl.add(user)
        self.pl.commit()

    def test_get_next_id_task_returns_max_task_id_plus_one(self):
        # when
        result = self.pl._get_next_id(ObjectTypes.Task)
        # then
        self.assertEqual(4, result)

    def test_get_next_id_tag_returns_max_tag_id_plus_one(self):
        # when
        result = self.pl._get_next_id(ObjectTypes.Tag)
        # then
        self.assertEqual(6, result)

    def test_get_next_id_attachment_returns_max_attachment_id_plus_one(self):
        # when
        result = self.pl._get_next_id(ObjectTypes.Attachment)
        # then
        self.assertEqual(8, result)

    def test_get_next_id_comment_returns_max_comment_id_plus_one(self):
        # when
        result = self.pl._get_next_id(ObjectTypes.Comment)
        # then
        self.assertEqual(10, result)

    def test_get_next_id_user_returns_max_user_id_plus_one(self):
        # when
        result = self.pl._get_next_id(ObjectTypes.User)
        # then
        self.assertEqual(12, result)

    def test_get_next_id_non_domain_object_raises(self):
        # expect
        with self.assertRaises(Exception) as cm:
            self.pl._get_next_id(str)
        # then
        self.assertEqual('Unknown object type: <class \'str\'>',
                         str(cm.exception))
