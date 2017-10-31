
from models.attachment import Attachment
from models.note import Note
from models.option import Option
from models.tag import Tag
from models.task import Task
from models.user import User
from tests.in_memory_persistence_layer.in_memory_test_base import \
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
        # given
        option = Option('key', 'value')
        # expect
        with self.assertRaises(Exception) as cm:
            self.pl._get_object_type('something')
        # then
        self.assertEqual('Unknown object type: something, str',
                         cm.exception.message)
