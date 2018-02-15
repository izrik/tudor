
from decimal import Decimal

from models.attachment import Attachment
from models.note import Note
from models.option import Option
from models.tag import Tag
from models.task import Task
from models.user import User
from tests.persistence_t.in_memory_persistence_layer.in_memory_test_base \
    import InMemoryTestBase


# copied from ../test_db_interaction.py, with removals


class DatabaseInteractionTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_adding_task_does_not_create_id(self):
        # given
        task = Task('summary')
        # precondition
        self.assertIsNone(task.id)
        # when
        self.pl.add(task)
        # then
        self.assertIsNone(task.id)

    def test_committing_task_creates_id(self):
        # given
        task = Task('summary')
        self.pl.add(task)
        # precondition
        self.assertIsNone(task.id)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(task.id)

    def test_committing_task_with_same_id_raises(self):
        # given
        task = Task('summary')
        task.id = 1
        self.pl.add(task)
        self.pl.commit()
        # precondition
        self.assertEqual(1, task.id)
        # when
        task2 = Task('task2')
        task2.id = 1
        self.pl.add(task2)
        # then
        self.assertRaises(Exception, self.pl.commit)

    def test_adding_task_does_not_affect_order_num(self):
        # given
        task = Task('summary')
        # precondition
        self.assertEqual(0, task.order_num)
        # when
        self.pl.add(task)
        # then
        self.assertEqual(0, task.order_num)

    def test_committing_task_does_not_affect_order_num(self):
        # given
        task = Task('summary')
        self.pl.add(task)
        # precondition
        self.assertEqual(0, task.order_num)
        # when
        self.pl.commit()
        # then
        self.assertEqual(0, task.order_num)

    def test_committing_task_with_same_order_num_is_allowed(self):
        # given
        task = Task('summary')
        task.order_num = 1
        self.pl.add(task)
        self.pl.commit()
        # precondition
        self.assertEqual(1, task.order_num)
        # when
        task2 = Task('task2')
        task2.order_num = 1
        self.pl.add(task2)
        self.pl.commit()
        # then
        self.assertEqual(1, task.order_num)
        self.assertEqual(1, task2.order_num)

    def test_adding_task_with_null_order_num_does_not_affect_order_num(self):
        # given
        task = Task('summary')
        task.order_num = None
        # precondition
        self.assertIsNone(task.order_num)
        # when
        self.pl.add(task)
        # then
        self.assertIsNone(task.order_num)

    def test_committing_task_with_null_order_num_makes_non_null(self):
        # given
        task = Task('summary')
        task.order_num = None
        self.pl.add(task)
        # precondition
        self.assertIsNone(task.order_num)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(task.order_num)

    def test_committing_task_with_null_order_num_makes_non_null_2(self):
        # given
        task = Task('summary')
        self.pl.add(task)
        task.order_num = None
        # precondition
        self.assertIsNone(task.order_num)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(task.order_num)

    def test_changing_order_num_of_already_committed_task_doesnt_affect(self):
        # given
        task = Task('summary')
        self.pl.add(task)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(task.order_num)
        # when
        task.order_num = None
        # then
        self.assertIsNone(task.order_num)

    def test_changing_commit_null_order_num_of_commed_task_raises(self):
        # given
        task = Task('summary')
        self.pl.add(task)
        self.pl.commit()
        task.order_num = None
        # precondition
        self.assertIsNone(task.order_num)
        # when
        self.assertRaises(Exception, self.pl.commit)

    def test_adding_tag_does_not_create_id(self):
        # given
        tag = Tag('value')
        # precondition
        self.assertIsNone(tag.id)
        # when
        self.pl.add(tag)
        # then
        self.assertIsNone(tag.id)

    def test_committing_tag_creates_id(self):
        # given
        tag = Tag('value')
        self.pl.add(tag)
        # precondition
        self.assertIsNone(tag.id)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(tag.id)

    def test_committing_tag_with_same_id_raises(self):
        # given
        tag = Tag('summary')
        tag.id = 1
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertEqual(1, tag.id)
        # when
        tag2 = Tag('tag2')
        tag2.id = 1
        self.pl.add(tag2)
        # then
        self.assertRaises(Exception, self.pl.commit)

    def test_adding_note_does_not_create_id(self):
        # given
        note = Note('note')
        # precondition
        self.assertIsNone(note.id)
        # when
        self.pl.add(note)
        # then
        self.assertIsNone(note.id)

    def test_committing_note_creates_id(self):
        # given
        note = Note('note')
        self.pl.add(note)
        # precondition
        self.assertIsNone(note.id)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(note.id)

    def test_committing_note_with_same_id_raises(self):
        # given
        note = Note('summary')
        note.id = 1
        self.pl.add(note)
        self.pl.commit()
        # precondition
        self.assertEqual(1, note.id)
        # when
        note2 = Note('note2')
        note2.id = 1
        self.pl.add(note2)
        # then
        self.assertRaises(Exception, self.pl.commit)

    def test_adding_attachment_does_not_create_id(self):
        # given
        attachment = Attachment('attachment')
        # precondition
        self.assertIsNone(attachment.id)
        # when
        self.pl.add(attachment)
        # then
        self.assertIsNone(attachment.id)

    def test_committing_attachment_creates_id(self):
        # given
        attachment = Attachment('attachment')
        self.pl.add(attachment)
        # precondition
        self.assertIsNone(attachment.id)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(attachment.id)

    def test_committing_attachment_with_same_id_raises(self):
        # given
        attachment = Attachment('summary')
        attachment.id = 1
        self.pl.add(attachment)
        self.pl.commit()
        # precondition
        self.assertEqual(1, attachment.id)
        # when
        attachment2 = Attachment('attachment2')
        attachment2.id = 1
        self.pl.add(attachment2)
        # then
        self.assertRaises(Exception, self.pl.commit)

    def test_adding_user_does_not_create_id(self):
        # given
        user = User('name@example.com')
        # precondition
        self.assertIsNone(user.id)
        # when
        self.pl.add(user)
        # then
        self.assertIsNone(user.id)

    def test_committing_user_creates_id(self):
        # given
        user = User('name@example.com')
        self.pl.add(user)
        # precondition
        self.assertIsNone(user.id)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(user.id)

    def test_committing_user_with_same_id_raises(self):
        # given
        user = User('summary')
        user.id = 1
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertEqual(1, user.id)
        # when
        user2 = User('user2')
        user2.id = 1
        self.pl.add(user2)
        # then
        self.assertRaises(Exception, self.pl.commit)

    def test_committing_option_with_same_key_raises(self):
        # given
        option = Option('key', 'value')
        self.pl.add(option)
        self.pl.commit()
        # precondition
        self.assertEqual('key', option.key)
        # when
        option2 = Option('key', 'value2')
        self.pl.add(option2)
        # then
        self.assertRaises(Exception, self.pl.commit)

    def test_rollback_reverts_changes(self):
        tag = Tag('tag', description='a')
        self.pl.add(tag)
        self.pl.commit()
        tag.description = 'b'
        # precondition
        self.assertEqual('b', tag.description)
        # when
        self.pl.rollback()
        # then
        tag2 = self.pl.get_tag_by_value('tag')
        self.assertIsNotNone(tag2)
        self.assertEqual('a', tag2.description)
        self.assertEqual('a', tag.description)

    def test_rollback_reverts_changes_to_collections(self):
        # given:
        task = Task('task')
        tag1 = Tag('tag1')
        tag2 = Tag('tag2')
        tag3 = Tag('tag3')
        task.tags.add(tag1)
        task.tags.add(tag2)
        self.pl.add(task)
        self.pl.add(tag1)
        self.pl.add(tag2)
        self.pl.add(tag3)
        self.pl.commit()

        # precondition:
        self.assertIn(tag1, task.tags)
        self.assertIn(tag2, task.tags)
        self.assertNotIn(tag3, task.tags)
        self.assertIn(task, tag1.tasks)
        self.assertIn(task, tag2.tasks)
        self.assertNotIn(task, tag3.tasks)

        task.tags.discard(tag1)
        task.tags.add(tag3)

        # precondition:
        self.assertNotIn(tag1, task.tags)
        self.assertIn(tag2, task.tags)
        self.assertIn(tag3, task.tags)
        self.assertNotIn(task, tag1.tasks)
        self.assertIn(task, tag2.tasks)
        self.assertIn(task, tag3.tasks)

        # when:
        self.pl.rollback()

        # then:
        self.assertIn(tag1, task.tags)
        self.assertIn(tag2, task.tags)
        self.assertNotIn(tag3, task.tags)
        self.assertIn(task, tag1.tasks)
        self.assertIn(task, tag2.tasks)
        self.assertNotIn(task, tag3.tasks)

    def test_rollback_does_not_revert_changes_on_unadded_new_objects(self):
        tag = Tag('tag', description='a')
        tag.description = 'b'
        # precondition
        self.assertEqual('b', tag.description)
        # when
        self.pl.rollback()
        # then
        self.assertEqual('b', tag.description)

    def test_rollback_reverts_changes_after_before_object_added(self):
        tag = Tag('tag', description='a')
        self.assertEqual('a', tag.description)
        self.pl.add(tag)
        tag.description = 'b'
        # precondition
        self.assertEqual('b', tag.description)
        # when
        self.pl.rollback()
        # then
        self.assertEqual('a', tag.description)

    def test_rollback_does_not_revert_changes_made_before_object_added(self):
        tag = Tag('tag', description='a')
        self.assertEqual('a', tag.description)
        tag.description = 'b'
        self.pl.add(tag)
        # precondition
        self.assertEqual('b', tag.description)
        # when
        self.pl.rollback()
        # then
        self.assertEqual('b', tag.description)

    def test_changes_to_objects_are_tracked_automatically(self):
        tag = Tag('tag', description='a')
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertEqual('a', tag.description)
        # when
        tag.description = 'b'
        # then
        self.assertEqual('b', tag.description)
        # when
        self.pl.commit()
        # then
        self.assertEqual('b', tag.description)
        # when
        self.pl.rollback()
        # then
        self.assertEqual('b', tag.description)

    def test_adding_tag_to_task_also_adds_task_to_tag(self):
        # given
        task = Task('task')
        tag = Tag('tag', description='a')
        self.pl.add(task)
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertNotIn(tag, task.tags)
        self.assertNotIn(task, tag.tasks)
        # when
        task.tags.add(tag)
        # then
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)
        # when
        self.pl.commit()
        # then
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)
        # when
        self.pl.rollback()
        # then
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

    def test_adding_child_also_sets_parent(self):
        # given
        parent = Task('parent')
        child = Task('child')
        self.pl.add(parent)
        self.pl.add(child)
        self.pl.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        parent.children.append(child)
        self.pl.commit()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)
        # when
        self.pl.rollback()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)

    def test_adding_child_also_sets_parent_id(self):
        # given
        parent = Task('parent')
        child = Task('child')
        self.pl.add(parent)
        self.pl.add(child)
        self.pl.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        parent.children.append(child)
        self.pl.commit()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)
        # when
        self.pl.rollback()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)

    def test_setting_parent_also_sets_parent_id(self):
        # given
        parent = Task('parent')
        child = Task('child')
        self.pl.add(parent)
        self.pl.add(child)
        self.pl.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        child.parent = parent
        self.pl.commit()
        # then
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)
        # when
        self.pl.rollback()
        # then
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)

    def test_setting_parent_also_adds_child(self):
        # given
        parent = Task('parent')
        child = Task('child')
        self.pl.add(parent)
        self.pl.add(child)
        self.pl.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        child.parent = parent
        self.pl.commit()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)
        # when
        self.pl.rollback()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)

    def test_inconsistent_parent_parent_and_children_last_one_wins_1(self):
        # given
        p1 = Task('p1')
        p2 = Task('p2')
        p3 = Task('p3')
        child = Task('child')
        self.pl.add(p1)
        self.pl.add(p2)
        self.pl.add(p3)
        self.pl.add(child)
        self.pl.commit()
        # precondition
        self.assertNotIn(child, p1.children)
        self.assertNotIn(child, p2.children)
        self.assertNotIn(child, p3.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(p1.id)
        self.assertIsNotNone(p2.id)
        self.assertIsNotNone(p3.id)
        self.assertIsNotNone(child.id)
        # when
        p3.children.append(child)
        child.parent = p2
        self.pl.commit()
        # then
        self.assertIn(child, p2.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p2, child.parent)
        self.assertEqual(p2.id, child.parent_id)
        # when
        self.pl.rollback()
        # then
        self.assertIn(child, p2.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p2, child.parent)
        self.assertEqual(p2.id, child.parent_id)

    def test_inconsistent_parent_parent_and_children_last_one_wins_2(self):
        # given
        p1 = Task('p1')
        p2 = Task('p2')
        p3 = Task('p3')
        child = Task('child')
        self.pl.add(p1)
        self.pl.add(p2)
        self.pl.add(p3)
        self.pl.add(child)
        self.pl.commit()
        # precondition
        self.assertNotIn(child, p1.children)
        self.assertNotIn(child, p2.children)
        self.assertNotIn(child, p3.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(p1.id)
        self.assertIsNotNone(p2.id)
        self.assertIsNotNone(p3.id)
        self.assertIsNotNone(child.id)
        # when
        child.parent = p2
        p3.children.append(child)
        self.pl.commit()
        # then
        self.assertIn(child, p3.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p3, child.parent)
        self.assertEqual(p3.id, child.parent_id)
        # when
        self.pl.rollback()
        # then
        self.assertIn(child, p3.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p3, child.parent)
        self.assertEqual(p3.id, child.parent_id)

    def test_decimal_expected_cost_not_converted_to_str(self):
        # given
        task = Task('task', expected_cost=Decimal('123.45'))
        self.assertIsInstance(task.expected_cost, Decimal)
        self.pl.add(task)
        self.assertIsInstance(task.expected_cost, Decimal)
        self.pl.commit()
        self.assertIsInstance(task.expected_cost, Decimal)

    def test_adding_task_dependee_also_adds_other_task_dependant(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()
        # precondition
        self.assertNotIn(t1, t2.dependees)
        self.assertNotIn(t1, t2.dependants)
        self.assertNotIn(t2, t1.dependees)
        self.assertNotIn(t2, t1.dependants)
        # when
        t1.dependees.add(t2)
        # then
        self.assertNotIn(t1, t2.dependees)
        self.assertIn(t1, t2.dependants)
        self.assertIn(t2, t1.dependees)
        self.assertNotIn(t2, t1.dependants)
        # when
        self.pl.commit()
        # then
        self.assertNotIn(t1, t2.dependees)
        self.assertIn(t1, t2.dependants)
        self.assertIn(t2, t1.dependees)
        self.assertNotIn(t2, t1.dependants)
        # when
        self.pl.rollback()
        # then
        self.assertNotIn(t1, t2.dependees)
        self.assertIn(t1, t2.dependants)
        self.assertIn(t2, t1.dependees)
        self.assertNotIn(t2, t1.dependants)

    def test_adding_task_after_also_adds_other_task_before(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()
        # precondition
        self.assertNotIn(t1, t2.dependees)
        self.assertNotIn(t1, t2.dependants)
        self.assertNotIn(t2, t1.dependees)
        self.assertNotIn(t2, t1.dependants)
        # when
        t1.prioritize_after.add(t2)
        # then
        self.assertNotIn(t1, t2.prioritize_after)
        self.assertIn(t1, t2.prioritize_before)
        self.assertIn(t2, t1.prioritize_after)
        self.assertNotIn(t2, t1.prioritize_before)
        # when
        self.pl.commit()
        # then
        self.assertNotIn(t1, t2.prioritize_after)
        self.assertIn(t1, t2.prioritize_before)
        self.assertIn(t2, t1.prioritize_after)
        self.assertNotIn(t2, t1.prioritize_before)
        # when
        self.pl.rollback()
        # then
        self.assertNotIn(t1, t2.prioritize_after)
        self.assertIn(t1, t2.prioritize_before)
        self.assertIn(t2, t1.prioritize_after)
        self.assertNotIn(t2, t1.prioritize_before)

    def test_adding_user_to_task_also_adds_task_to_user(self):
        # given
        task = Task('task')
        user = User('name@example.com')
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertNotIn(user, task.users)
        self.assertNotIn(task, user.tasks)
        # when
        task.users.add(user)
        # then
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # when
        self.pl.commit()
        # then
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # when
        self.pl.rollback()
        # then
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

    def test_setting_id_before_adding_succeeds(self):
        # given
        task = Task('task')
        task.id = 1
        # precondition
        self.assertEqual(1, task.id)
        # when
        self.pl.add(task)
        # then
        self.assertEqual(1, task.id)
        # when
        self.pl.commit()
        # then
        self.assertEqual(1, task.id)
        # when
        self.pl.commit()
        # then
        self.assertEqual(1, task.id)
        # when
        self.pl.rollback()
        # then
        self.assertEqual(1, task.id)

    def test_conflicting_id_when_committing_raises_exception(self):
        # given
        t1 = Task('t1')
        t1.id = 1
        self.pl.add(t1)
        t2 = Task('t1')
        t2.id = 1
        self.pl.add(t2)
        # precondition
        self.assertEqual(1, t1.id)
        self.assertEqual(1, t2.id)
        # expect
        self.assertRaises(Exception, self.pl.commit)

    def test_commit_changed_tag_values_conflict_raises(self):
        # given
        self.t1 = Tag('t1')
        self.pl.add(self.t1)
        self.t2 = Tag('t2')
        self.pl.add(self.t2)
        self.pl.commit()
        self.t2.value = 't1'
        # expect
        self.assertRaises(Exception, self.pl.commit)

    def test_commit_new_tag_values_conflict_raises(self):
        # given
        self.t1 = Tag('t1')
        self.pl.add(self.t1)
        self.pl.commit()
        t3 = Tag('t1')
        self.pl.add(t3)
        # expect
        self.assertRaises(Exception, self.pl.commit)

    def test_commit_changed_user_emails_conflict_raises(self):
        # given
        self.user1 = User('user1')
        self.pl.add(self.user1)
        self.user2 = User('user2')
        self.pl.add(self.user2)
        self.pl.commit()
        self.user2.email = 'user1'
        # expect
        self.assertRaises(Exception, self.pl.commit)

    def test_commit_new_user_emails_conflict_raises(self):
        # given
        self.user1 = User('user1')
        self.pl.add(self.user1)
        self.pl.commit()
        user3 = User('user1')
        self.pl.add(user3)
        # expect
        self.assertRaises(Exception, self.pl.commit)
