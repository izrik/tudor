
from models.attachment import Attachment
from models.note import Note
from models.option import Option
from models.tag import Tag
from models.task import Task
from models.user import User
from tests.persistence_t.in_memory_persistence_layer.in_memory_test_base \
    import InMemoryTestBase


# copied from ../test_deletion.py, with removals


class DeletionTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_deleting_task_reduces_count(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        # precondition
        self.assertEqual(1, self.pl.count_tasks())
        # when
        self.pl.delete(task)
        self.pl.commit()
        # then
        self.assertEqual(0, self.pl.count_tasks())

    def test_deleting_tag_reduces_count(self):
        # given
        tag = Tag('tag')
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertEqual(1, self.pl.count_tags())
        # when
        self.pl.delete(tag)
        self.pl.commit()
        # then
        self.assertEqual(0, self.pl.count_tags())

    def test_deleting_attachment_reduces_count(self):
        # given
        attachment = Attachment('attachment')
        self.pl.add(attachment)
        self.pl.commit()
        # precondition
        self.assertEqual(1, self.pl.count_attachments())
        # when
        self.pl.delete(attachment)
        self.pl.commit()
        # then
        self.assertEqual(0, self.pl.count_attachments())

    def test_deleting_note_reduces_count(self):
        # given
        note = Note('note')
        self.pl.add(note)
        self.pl.commit()
        # precondition
        self.assertEqual(1, self.pl.count_notes())
        # when
        self.pl.delete(note)
        self.pl.commit()
        # then
        self.assertEqual(0, self.pl.count_notes())

    def test_deleting_user_reduces_count(self):
        # given
        user = User('user')
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertEqual(1, self.pl.count_users())
        # when
        self.pl.delete(user)
        self.pl.commit()
        # then
        self.assertEqual(0, self.pl.count_users())

    def test_deleting_option_reduces_count(self):
        # given
        option = Option('key', 'value')
        self.pl.add(option)
        self.pl.commit()
        # precondition
        self.assertEqual(1, self.pl.count_options())
        # when
        self.pl.delete(option)
        self.pl.commit()
        # then
        self.assertEqual(0, self.pl.count_options())

    def test_deleting_task_removes_all_children(self):
        # given
        parent = Task('parent')
        c1 = Task('c1')
        c2 = Task('c2')
        c3 = Task('c3')
        parent.children.append(c1)
        parent.children.append(c2)
        parent.children.append(c3)
        self.pl.add(parent)
        self.pl.add(c1)
        self.pl.add(c2)
        self.pl.add(c3)
        self.pl.commit()

        # precondition
        self.assertIn(c1, parent.children)
        self.assertIn(c2, parent.children)
        self.assertIn(c3, parent.children)

        # when
        self.pl.delete(parent)
        self.pl.commit()

        # then
        self.assertNotIn(c1, parent.children)
        self.assertNotIn(c2, parent.children)
        self.assertNotIn(c3, parent.children)
        self.assertEqual(0, len(parent.children))

    def test_deleting_parent_task_nullifies_parent_and_parent_id(self):
        # given
        parent = Task('parent')
        c1 = Task('c1')
        c2 = Task('c2')
        c3 = Task('c3')
        parent.children.append(c1)
        parent.children.append(c2)
        parent.children.append(c3)
        self.pl.add(parent)
        self.pl.add(c1)
        self.pl.add(c2)
        self.pl.add(c3)
        self.pl.commit()

        # precondition
        self.assertIs(parent, c1.parent)
        self.assertIs(parent, c2.parent)
        self.assertIs(parent, c3.parent)

        # when
        self.pl.delete(parent)
        self.pl.commit()

        # then
        self.assertIsNone(c1.parent)
        self.assertIsNone(c2.parent)
        self.assertIsNone(c3.parent)
        self.assertIsNone(c1.parent_id)
        self.assertIsNone(c2.parent_id)
        self.assertIsNone(c3.parent_id)

    def test_deleting_task_removes_task_from_tag(self):
        # given
        task = Task('task')
        tag = Tag('tag')
        task.tags.append(tag)
        self.pl.add(task)
        self.pl.add(tag)
        self.pl.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertNotIn(task, tag.tasks)

    def test_deleting_task_removes_tag_from_task(self):
        # given
        task = Task('task')
        tag = Tag('tag')
        task.tags.append(tag)
        self.pl.add(task)
        self.pl.add(tag)
        self.pl.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertNotIn(tag, task.tags)

    def test_deleting_tag_removes_tag_from_task(self):
        # given
        task = Task('task')
        tag = Tag('tag')
        task.tags.append(tag)
        self.pl.add(task)
        self.pl.add(tag)
        self.pl.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.delete(tag)
        self.pl.commit()

        # then
        self.assertNotIn(tag, task.tags)

    def test_deleting_tag_removes_task_from_tag(self):
        # given
        task = Task('task')
        tag = Tag('tag')
        task.tags.append(tag)
        self.pl.add(task)
        self.pl.add(tag)
        self.pl.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.delete(tag)
        self.pl.commit()

        # then
        self.assertNotIn(task, tag.tasks)

    def test_deleting_task_removes_task_from_user(self):
        # given
        task = Task('task')
        user = User('user')
        task.users.append(user)
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertNotIn(task, user.tasks)

    def test_deleting_task_removes_user_from_task(self):
        # given
        task = Task('task')
        user = User('user')
        task.users.append(user)
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertNotIn(user, task.users)

    def test_deleting_user_removes_user_from_task(self):
        # given
        task = Task('task')
        user = User('user')
        task.users.append(user)
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.delete(user)
        self.pl.commit()

        # then
        self.assertNotIn(user, task.users)

    def test_deleting_user_removes_task_from_user(self):
        # given
        task = Task('task')
        user = User('user')
        task.users.append(user)
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.delete(user)
        self.pl.commit()

        # then
        self.assertNotIn(task, user.tasks)

    def test_deleting_dependee_removes_dependee_from_dependant(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.dependees.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.dependees)
        self.assertIn(t1, t2.dependants)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t2, t1.dependees)

    def test_deleting_dependee_removes_dependant(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.dependees.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.dependees)
        self.assertIn(t1, t2.dependants)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t1, t2.dependants)

    def test_deleting_dependant_removes_dependant_from_dependee(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.dependants.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.dependants)
        self.assertIn(t1, t2.dependees)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t2, t1.dependants)

    def test_deleting_dependant_removes_dependee(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.dependants.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.dependants)
        self.assertIn(t1, t2.dependees)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t1, t2.dependees)

    def test_deleting_pbefore_removes_pbefore_from_pafter(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.prioritize_before.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_before)
        self.assertIn(t1, t2.prioritize_after)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t2, t1.prioritize_before)

    def test_deleting_pbefore_removes_pafter(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.prioritize_before.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_before)
        self.assertIn(t1, t2.prioritize_after)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t1, t2.prioritize_after)

    def test_deleting_pafter_removes_pafter_from_pbefore(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.prioritize_after.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_after)
        self.assertIn(t1, t2.prioritize_before)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t2, t1.prioritize_after)

    def test_deleting_pafter_removes_pbefore(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.prioritize_after.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_after)
        self.assertIn(t1, t2.prioritize_before)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t1, t2.prioritize_before)

    def test_deleting_task_removes_all_notes(self):
        # given
        task = Task('task')
        n1 = Note('n1')
        n2 = Note('n2')
        n3 = Note('n3')
        task.notes.append(n1)
        task.notes.append(n2)
        task.notes.append(n3)
        self.pl.add(task)
        self.pl.add(n1)
        self.pl.add(n2)
        self.pl.add(n3)
        self.pl.commit()

        # precondition
        self.assertIn(n1, task.notes)
        self.assertIn(n2, task.notes)
        self.assertIn(n3, task.notes)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertNotIn(n1, task.notes)
        self.assertNotIn(n2, task.notes)
        self.assertNotIn(n3, task.notes)
        self.assertEqual(0, len(task.notes))

    def test_deleting_task_of_notes_nullifies_task_and_task_id(self):
        # given
        task = Task('task')
        n1 = Note('n1')
        n2 = Note('n2')
        n3 = Note('n3')
        task.notes.append(n1)
        task.notes.append(n2)
        task.notes.append(n3)
        self.pl.add(task)
        self.pl.add(n1)
        self.pl.add(n2)
        self.pl.add(n3)
        self.pl.commit()

        # precondition
        self.assertIs(task, n1.task)
        self.assertIs(task, n2.task)
        self.assertIs(task, n3.task)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertIsNone(n1.task)
        self.assertIsNone(n2.task)
        self.assertIsNone(n3.task)
        self.assertIsNone(n1.task_id)
        self.assertIsNone(n2.task_id)
        self.assertIsNone(n3.task_id)

    def test_deleting_task_removes_all_attachments(self):
        # given
        task = Task('task')
        a1 = Attachment('a1')
        a2 = Attachment('a2')
        a3 = Attachment('a3')
        task.attachments.append(a1)
        task.attachments.append(a2)
        task.attachments.append(a3)
        self.pl.add(task)
        self.pl.add(a1)
        self.pl.add(a2)
        self.pl.add(a3)
        self.pl.commit()

        # precondition
        self.assertIn(a1, task.attachments)
        self.assertIn(a2, task.attachments)
        self.assertIn(a3, task.attachments)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertNotIn(a1, task.attachments)
        self.assertNotIn(a2, task.attachments)
        self.assertNotIn(a3, task.attachments)
        self.assertEqual(0, len(task.attachments))

    def test_deleting_task_of_atts_nullifies_task_and_task_id(self):
        # given
        task = Task('task')
        a1 = Attachment('a1')
        a2 = Attachment('a2')
        a3 = Attachment('a3')
        task.attachments.append(a1)
        task.attachments.append(a2)
        task.attachments.append(a3)
        self.pl.add(task)
        self.pl.add(a1)
        self.pl.add(a2)
        self.pl.add(a3)
        self.pl.commit()

        # precondition
        self.assertIs(task, a1.task)
        self.assertIs(task, a2.task)
        self.assertIs(task, a3.task)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertIsNone(a1.task)
        self.assertIsNone(a2.task)
        self.assertIsNone(a3.task)
        self.assertIsNone(a1.task_id)
        self.assertIsNone(a2.task_id)
        self.assertIsNone(a3.task_id)


class AddDeleteTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_add_after_add_silently_ignored(self):
        # given
        task = Task('task')
        self.pl.add(task)
        # precondition
        self.assertIn(task, self.pl._added_objects)
        # when
        self.pl.add(task)
        # then
        self.assertIn(task, self.pl._added_objects)

    def test_delete_after_delete_silently_ignored(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        self.pl.delete(task)
        # precondition
        self.assertIn(task, self.pl._deleted_objects)
        # when
        self.pl.delete(task)
        # then
        self.assertIn(task, self.pl._deleted_objects)

    def test_delete_after_add_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        # precondition
        self.assertIn(task, self.pl._added_objects)
        self.assertNotIn(task, self.pl._deleted_objects)
        # when
        self.assertRaises(
            Exception,
            self.pl.delete,
            task)
        # then
        self.assertIn(task, self.pl._added_objects)
        self.assertNotIn(task, self.pl._deleted_objects)

    def test_add_after_delete_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        self.pl.delete(task)
        # precondition
        self.assertNotIn(task, self.pl._added_objects)
        self.assertIn(task, self.pl._deleted_objects)
        # expect
        self.assertRaises(
            Exception,
            self.pl.add,
            task)
        # and
        self.assertNotIn(task, self.pl._added_objects)
        self.assertIn(task, self.pl._deleted_objects)

    def test_add_an_object_already_committed_silently_ignored(self):
        # given
        task = Task('task')
        self.pl.add(task)
        tag = Tag('tag')
        self.pl.add(tag)
        attachment = Attachment('attachment')
        self.pl.add(attachment)
        note = Note('note')
        self.pl.add(note)
        user = User('user')
        self.pl.add(user)
        option = Option('key', 'value')
        self.pl.add(option)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(task.id)
        task2 = self.pl.get_task(task.id)
        self.assertIs(task2, task)
        self.assertIsNotNone(tag.id)
        tag2 = self.pl.get_tag(tag.id)
        self.assertIs(tag2, tag)
        self.assertIsNotNone(attachment.id)
        attachment2 = self.pl.get_attachment(attachment.id)
        self.assertIs(attachment2, attachment)
        self.assertIsNotNone(note.id)
        note2 = self.pl.get_note(note.id)
        self.assertIs(note2, note)
        self.assertIsNotNone(user.id)
        user2 = self.pl.get_user(user.id)
        self.assertIs(user2, user)
        self.assertIsNotNone(option.id)
        option2 = self.pl.get_option(option.id)
        self.assertIs(option2, option)
        # when
        self.pl.add(task)
        # then
        self.assertNotIn(task, self.pl._added_objects)
        # when
        self.pl.add(tag)
        # then
        self.assertNotIn(tag, self.pl._added_objects)
        # when
        self.pl.add(attachment)
        # then
        self.assertNotIn(attachment, self.pl._added_objects)
        # when
        self.pl.add(note)
        # then
        self.assertNotIn(note, self.pl._added_objects)
        # when
        self.pl.add(user)
        # then
        self.assertNotIn(user, self.pl._added_objects)
        # when
        self.pl.add(option)
        # then
        self.assertNotIn(option, self.pl._added_objects)
        # then
        self.assertEqual(0, len(self.pl._added_objects))
