
from models.attachment import Attachment
from models.note import Note
from models.option import Option
from models.tag import Tag
from models.task import Task
from models.user import User
from tests.in_memory_persistence_layer_t.in_memory_test_base import \
    InMemoryTestBase


# not copied from any other file


class GetObjectTypeTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_get_object_type_task_returns_task(self):
        # given
        task = Task('task1')
        # when
        result = self.pl._get_object_type(task)
        # then
        self.assertEqual(Task, result)

    def test_get_object_type_tag_returns_tag(self):
        # given
        tag = Tag('tag1')
        # when
        result = self.pl._get_object_type(tag)
        # then
        self.assertEqual(Tag, result)

    def test_get_object_type_attachment_returns_attachment(self):
        # given
        attachment = Attachment('attachment1')
        # when
        result = self.pl._get_object_type(attachment)
        # then
        self.assertEqual(Attachment, result)

    def test_get_object_type_note_returns_note(self):
        # given
        note = Note('note1')
        # when
        result = self.pl._get_object_type(note)
        # then
        self.assertEqual(Note, result)

    def test_get_object_type_user_returns_user(self):
        # given
        user = User('user1')
        # when
        result = self.pl._get_object_type(user)
        # then
        self.assertEqual(User, result)

    def test_get_object_type_option_returns_option(self):
        # given
        option = Option('key', 'value')
        # when
        result = self.pl._get_object_type(option)
        # then
        self.assertEqual(Option, result)

    def test_get_object_type_non_domain_object_raises(self):
        # expect
        with self.assertRaises(Exception) as cm:
            self.pl._get_object_type('something')
        # then
        self.assertEqual('Unknown object type: something, str',
                         cm.exception.message)


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
        task = Task('task')
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
        tag = Tag('tag')
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
        attachment = Attachment('attachment')
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

    def test_get_next_note_id_no_notes_returns_one(self):
        # precondition
        self.assertEqual(0, len(self.pl._notes))
        # when
        result = self.pl._get_next_note_id()
        # then
        self.assertEqual(1, result)

    def test_get_next_note_id_some_notes_returns_max_plus_one(self):
        # given
        note = Note('note')
        note.id = 3
        self.pl.add(note)
        self.pl.commit()
        # precondition
        self.assertEqual(1, len(self.pl._notes))
        self.assertEqual(3, self.pl._notes[0].id)
        # when
        result = self.pl._get_next_note_id()
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
        user = User('user')
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
        task = Task('task')
        task.id = 3
        self.pl.add(task)
        tag = Tag('tag')
        tag.id = 5
        self.pl.add(tag)
        attachment = Attachment('attachment')
        attachment.id = 7
        self.pl.add(attachment)
        note = Note('note')
        note.id = 9
        self.pl.add(note)
        user = User('user')
        user.id = 11
        self.pl.add(user)
        self.pl.commit()

    def test_get_next_id_task_returns_max_task_id_plus_one(self):
        # when
        result = self.pl._get_next_id(Task)
        # then
        self.assertEqual(4, result)

    def test_get_next_id_tag_returns_max_tag_id_plus_one(self):
        # when
        result = self.pl._get_next_id(Tag)
        # then
        self.assertEqual(6, result)

    def test_get_next_id_attachment_returns_max_attachment_id_plus_one(self):
        # when
        result = self.pl._get_next_id(Attachment)
        # then
        self.assertEqual(8, result)

    def test_get_next_id_note_returns_max_note_id_plus_one(self):
        # when
        result = self.pl._get_next_id(Note)
        # then
        self.assertEqual(10, result)

    def test_get_next_id_user_returns_max_user_id_plus_one(self):
        # when
        result = self.pl._get_next_id(User)
        # then
        self.assertEqual(12, result)

    def test_get_next_id_non_domain_object_raises(self):
        # expect
        with self.assertRaises(Exception) as cm:
            self.pl._get_next_id(str)
        # then
        self.assertEqual('Unknown object type: str', cm.exception.message)
