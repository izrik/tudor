
from decimal import Decimal

from persistence.in_memory.models.note import Note
from persistence.in_memory.models.user import User
from persistence.in_memory.models.option import Option
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class DatabaseInteractionTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_adding_task_does_not_create_id(self):
        # given
        task = self.pl.create_task('summary')
        # precondition
        self.assertIsNone(task.id)
        # when
        self.pl.add(task)
        # then
        self.assertIsNone(task.id)

    def test_committing_task_creates_id(self):
        # given
        task = self.pl.create_task('summary')
        self.pl.add(task)
        # precondition
        self.assertIsNone(task.id)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(task.id)

    def test_committing_task_with_same_id_raises(self):
        # given
        task = self.pl.create_task('summary')
        task.id = 1
        self.pl.add(task)
        self.pl.commit()
        # precondition
        self.assertEqual(1, task.id)
        # when
        task2 = self.pl.create_task('task2')
        task2.id = 1
        self.pl.add(task2)
        # then
        self.assertRaises(Exception, self.pl.commit)

    def test_adding_task_does_not_affect_order_num(self):
        # given
        task = self.pl.create_task('summary')
        # precondition
        self.assertEqual(0, task.order_num)
        # when
        self.pl.add(task)
        # then
        self.assertEqual(0, task.order_num)

    def test_committing_task_does_not_affect_order_num(self):
        # given
        task = self.pl.create_task('summary')
        self.pl.add(task)
        # precondition
        self.assertEqual(0, task.order_num)
        # when
        self.pl.commit()
        # then
        self.assertEqual(0, task.order_num)

    def test_committing_task_with_same_order_num_is_allowed(self):
        # given
        task = self.pl.create_task('summary')
        task.order_num = 1
        self.pl.add(task)
        self.pl.commit()
        # precondition
        self.assertEqual(1, task.order_num)
        # when
        task2 = self.pl.create_task('task2')
        task2.order_num = 1
        self.pl.add(task2)
        self.pl.commit()
        # then
        self.assertEqual(1, task.order_num)
        self.assertEqual(1, task2.order_num)

    def test_adding_task_with_null_order_num_does_not_affect_order_num(self):
        # given
        task = self.pl.create_task('summary')
        task.order_num = None
        # precondition
        self.assertIsNone(task.order_num)
        # when
        self.pl.add(task)
        # then
        self.assertIsNone(task.order_num)

    def test_committing_task_with_null_order_num_makes_non_null(self):
        # given
        task = self.pl.create_task('summary')
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
        task = self.pl.create_task('summary')
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
        task = self.pl.create_task('summary')
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
        task = self.pl.create_task('summary')
        self.pl.add(task)
        self.pl.commit()
        task.order_num = None
        # precondition
        self.assertIsNone(task.order_num)
        # when
        self.assertRaises(Exception, self.pl.commit)

    def test_adding_tag_does_not_create_id(self):
        # given
        tag = self.pl.create_tag('value')
        # precondition
        self.assertIsNone(tag.id)
        # when
        self.pl.add(tag)
        # then
        self.assertIsNone(tag.id)

    def test_committing_tag_creates_id(self):
        # given
        tag = self.pl.create_tag('value')
        self.pl.add(tag)
        # precondition
        self.assertIsNone(tag.id)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(tag.id)

    def test_committing_tag_with_same_id_raises(self):
        # given
        tag = self.pl.create_tag('summary')
        tag.id = 1
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertEqual(1, tag.id)
        # when
        tag2 = self.pl.create_tag('tag2')
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
        attachment = self.pl.create_attachment('attachment')
        # precondition
        self.assertIsNone(attachment.id)
        # when
        self.pl.add(attachment)
        # then
        self.assertIsNone(attachment.id)

    def test_committing_attachment_creates_id(self):
        # given
        attachment = self.pl.create_attachment('attachment')
        self.pl.add(attachment)
        # precondition
        self.assertIsNone(attachment.id)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(attachment.id)

    def test_committing_attachment_with_same_id_raises(self):
        # given
        attachment = self.pl.create_attachment('summary')
        attachment.id = 1
        self.pl.add(attachment)
        self.pl.commit()
        # precondition
        self.assertEqual(1, attachment.id)
        # when
        attachment2 = self.pl.create_attachment('attachment2')
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
        tag = self.pl.create_tag('tag', description='a')
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
        task = self.pl.create_task('task')
        tag1 = self.pl.create_tag('tag1')
        tag2 = self.pl.create_tag('tag2')
        tag3 = self.pl.create_tag('tag3')
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
        tag = self.pl.create_tag('tag', description='a')
        tag.description = 'b'
        # precondition
        self.assertEqual('b', tag.description)
        # when
        self.pl.rollback()
        # then
        self.assertEqual('b', tag.description)

    def test_rollback_reverts_changes_after_before_object_added(self):
        tag = self.pl.create_tag('tag', description='a')
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
        tag = self.pl.create_tag('tag', description='a')
        self.assertEqual('a', tag.description)
        tag.description = 'b'
        self.pl.add(tag)
        # precondition
        self.assertEqual('b', tag.description)
        # when
        self.pl.rollback()
        # then
        self.assertEqual('b', tag.description)

    def test_rollback_undeletes_deleted_objects(self):
        # given
        task = self.pl.create_task('task')
        self.pl.add(task)
        self.pl.commit()
        self.pl.delete(task)
        # precondition
        self.assertIn(task, self.pl._committed_objects)
        self.assertIn(task, self.pl._deleted_objects)
        # when
        self.pl.rollback()
        # then
        self.assertIn(task, self.pl._committed_objects)
        self.assertNotIn(task, self.pl._deleted_objects)

    def test_changes_to_objects_are_tracked_automatically(self):
        tag = self.pl.create_tag('tag', description='a')
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

    def test_changes_after_get_are_also_tracked(self):
        # given
        dbtag = self.pl.DbTag('tag', description='a')
        self.pl.db.session.add(dbtag)
        self.pl.db.session.commit()
        tag = self.pl.get_tag_by_value('tag')
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
        self.assertEqual('b', dbtag.description)
        # when
        self.pl.rollback()
        # then
        self.assertEqual('b', tag.description)
        self.assertEqual('b', dbtag.description)

    def test_adding_tag_to_task_also_adds_task_to_tag(self):
        # given
        task = self.pl.create_task('task')
        tag = self.pl.create_tag('tag', description='a')
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
        parent = self.pl.create_task('parent')
        child = self.pl.create_task('child')
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
        parent = self.pl.create_task('parent')
        child = self.pl.create_task('child')
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
        parent = self.pl.create_task('parent')
        child = self.pl.create_task('child')
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
        parent = self.pl.create_task('parent')
        child = self.pl.create_task('child')
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
        p1 = self.pl.create_task('p1')
        p2 = self.pl.create_task('p2')
        p3 = self.pl.create_task('p3')
        child = self.pl.create_task('child')
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
        p1 = self.pl.create_task('p1')
        p2 = self.pl.create_task('p2')
        p3 = self.pl.create_task('p3')
        child = self.pl.create_task('child')
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

    def test_db_only_rollback_reverts_changes(self):
        tag = self.pl.DbTag('tag', description='a')
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()
        tag.description = 'b'
        # precondition
        self.assertEqual('b', tag.description)
        # when
        self.pl.db.session.rollback()
        # then
        tag2 = self.pl.DbTag.query.filter_by(value='tag').first()
        self.assertIsNotNone(tag2)
        self.assertEqual('a', tag2.description)
        self.assertEqual('a', tag.description)

    def test_db_only_rollback_reverts_changes_to_collections(self):
        # given:
        task = self.pl.DbTask('task')
        tag1 = self.pl.DbTag('tag1')
        tag2 = self.pl.DbTag('tag2')
        tag3 = self.pl.DbTag('tag3')
        task.tags.append(tag1)
        task.tags.append(tag2)
        self.pl.db.session.add(task)
        self.pl.db.session.add(tag1)
        self.pl.db.session.add(tag2)
        self.pl.db.session.add(tag3)
        self.pl.db.session.commit()

        # precondition:
        self.assertIn(tag1, task.tags)
        self.assertIn(tag2, task.tags)
        self.assertNotIn(tag3, task.tags)
        self.assertIn(task, tag1.tasks)
        self.assertIn(task, tag2.tasks)
        self.assertNotIn(task, tag3.tasks)

        task.tags.remove(tag1)
        task.tags.append(tag3)

        # precondition:
        self.assertNotIn(tag1, task.tags)
        self.assertIn(tag2, task.tags)
        self.assertIn(tag3, task.tags)
        self.assertNotIn(task, tag1.tasks)
        self.assertIn(task, tag2.tasks)
        self.assertIn(task, tag3.tasks)

        # when:
        self.pl.db.session.rollback()

        # then:
        self.assertIn(tag1, task.tags)
        self.assertIn(tag2, task.tags)
        self.assertNotIn(tag3, task.tags)
        self.assertIn(task, tag1.tasks)
        self.assertIn(task, tag2.tasks)
        self.assertNotIn(task, tag3.tasks)

    def test_db_only_rollback_does_not_reverts_changes_on_unadded_objs(self):
        tag = self.pl.DbTag('tag', description='a')
        tag.description = 'b'
        # precondition
        self.assertEqual('b', tag.description)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertEqual('b', tag.description)

    def test_db_only_changes_to_objects_are_tracked_automatically(self):
        tag = self.pl.DbTag('tag', description='a')
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()
        # precondition
        self.assertEqual('a', tag.description)
        # when
        tag.description = 'b'
        # then
        self.assertEqual('b', tag.description)
        # when
        self.pl.db.session.commit()
        # then
        self.assertEqual('b', tag.description)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertEqual('b', tag.description)

    def test_db_only_adding_tag_to_task_also_adds_task_to_tag(self):
        # given
        task = self.pl.DbTask('task')
        tag = self.pl.DbTag('tag', description='a')
        self.pl.db.session.add(task)
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(tag, task.tags)
        self.assertNotIn(task, tag.tasks)
        # when
        task.tags.append(tag)
        # then
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)
        # when
        self.pl.db.session.commit()
        # then
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

    def test_db_only_adding_child_also_sets_parent(self):
        # given
        parent = self.pl.DbTask('parent')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(parent)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        parent.children.append(child)
        self.pl.db.session.commit()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)

    def test_db_only_adding_child_also_sets_parent_id(self):
        # given
        parent = self.pl.DbTask('parent')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(parent)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        parent.children.append(child)
        self.pl.db.session.commit()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)

    def test_db_only_setting_parent_also_sets_parent_id(self):
        # given
        parent = self.pl.DbTask('parent')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(parent)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        child.parent = parent
        self.pl.db.session.commit()
        # then
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)

    def test_db_only_setting_parent_also_adds_child(self):
        # given
        parent = self.pl.DbTask('parent')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(parent)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        child.parent = parent
        self.pl.db.session.commit()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)

    def test_db_only_setting_parent_id_also_sets_parent(self):
        # given
        parent = self.pl.DbTask('parent')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(parent)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        child.parent_id = parent.id
        self.pl.db.session.commit()
        # then
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)

    def test_db_only_setting_parent_id_also_adds_child(self):
        # given
        parent = self.pl.DbTask('parent')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(parent)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        child.parent_id = parent.id
        self.pl.db.session.commit()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)

    def test_db_only_inconsistent_parent_always_overrides_parent_id(self):
        # given
        p1 = self.pl.DbTask('p1')
        p2 = self.pl.DbTask('p2')
        p3 = self.pl.DbTask('p3')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(p1)
        self.pl.db.session.add(p2)
        self.pl.db.session.add(p3)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
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
        child.parent_id = p1.id
        self.pl.db.session.commit()
        # then
        self.assertIn(child, p2.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p2, child.parent)
        self.assertEqual(p2.id, child.parent_id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, p2.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p2, child.parent)
        self.assertEqual(p2.id, child.parent_id)

    def test_db_only_inconsistent_parent_children_overrides_parent_id(self):
        # given
        p1 = self.pl.DbTask('p1')
        p2 = self.pl.DbTask('p2')
        p3 = self.pl.DbTask('p3')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(p1)
        self.pl.db.session.add(p2)
        self.pl.db.session.add(p3)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
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
        child.parent_id = p1.id
        self.pl.db.session.commit()
        # then
        self.assertIn(child, p3.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p3, child.parent)
        self.assertEqual(p3.id, child.parent_id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, p3.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p3, child.parent)
        self.assertEqual(p3.id, child.parent_id)

    def test_db_only_incon_parent_parent_and_children_last_one_wins_1(self):
        # given
        p1 = self.pl.DbTask('p1')
        p2 = self.pl.DbTask('p2')
        p3 = self.pl.DbTask('p3')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(p1)
        self.pl.db.session.add(p2)
        self.pl.db.session.add(p3)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
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
        self.pl.db.session.commit()
        # then
        self.assertIn(child, p2.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p2, child.parent)
        self.assertEqual(p2.id, child.parent_id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, p2.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p2, child.parent)
        self.assertEqual(p2.id, child.parent_id)

    def test_db_only_incon_parent_parent_and_children_last_one_wins_2(self):
        # given
        p1 = self.pl.DbTask('p1')
        p2 = self.pl.DbTask('p2')
        p3 = self.pl.DbTask('p3')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(p1)
        self.pl.db.session.add(p2)
        self.pl.db.session.add(p3)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
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
        self.pl.db.session.commit()
        # then
        self.assertIn(child, p3.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p3, child.parent)
        self.assertEqual(p3.id, child.parent_id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, p3.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p3, child.parent)
        self.assertEqual(p3.id, child.parent_id)

    def test_db_only_decimal_expected_cost_not_converted_to_str(self):
        # given
        task = self.pl.DbTask('task', expected_cost=Decimal('123.45'))
        self.assertIsInstance(task.expected_cost, Decimal)
        self.pl.db.session.add(task)
        self.assertIsInstance(task.expected_cost, Decimal)
        self.pl.db.session.commit()
        self.assertIsInstance(task.expected_cost, Decimal)

    def test_decimal_expected_cost_not_converted_to_str(self):
        # given
        task = self.pl.create_task('task', expected_cost=Decimal('123.45'))
        self.assertIsInstance(task.expected_cost, Decimal)
        self.pl.add(task)
        self.assertIsInstance(task.expected_cost, Decimal)
        self.pl.commit()
        self.assertIsInstance(task.expected_cost, Decimal)

    def test_adding_task_dependee_also_adds_other_task_dependant(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
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
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
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
        task = self.pl.create_task('task')
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
        task = self.pl.create_task('task')
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
        t1 = self.pl.create_task('t1')
        t1.id = 1
        self.pl.add(t1)
        t2 = self.pl.create_task('t1')
        t2.id = 1
        self.pl.add(t2)
        # precondition
        self.assertEqual(1, t1.id)
        self.assertEqual(1, t2.id)
        # expect
        self.assertRaises(Exception, self.pl.commit)

    def test_commit_changed_tag_values_conflict_raises(self):
        # given
        self.t1 = self.pl.create_tag('t1')
        self.pl.add(self.t1)
        self.t2 = self.pl.create_tag('t2')
        self.pl.add(self.t2)
        self.pl.commit()
        self.t2.value = 't1'
        # expect
        self.assertRaises(Exception, self.pl.commit)

    def test_commit_new_tag_values_conflict_raises(self):
        # given
        self.t1 = self.pl.create_tag('t1')
        self.pl.add(self.t1)
        self.pl.commit()
        t3 = self.pl.create_tag('t1')
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
