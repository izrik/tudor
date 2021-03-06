
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class DbOnlyDeletionTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_deleting_task_reduces_count(self):
        # given
        task = self.pl.create_task('task')
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
        tag = self.pl.create_tag('tag')
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
        attachment = self.pl.create_attachment('attachment')
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
        note = self.pl.create_note('note')
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
        user = self.pl.create_user('user')
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
        option = self.pl.create_option('key', 'value')
        self.pl.add(option)
        self.pl.commit()
        # precondition
        self.assertEqual(1, self.pl.count_options())
        # when
        self.pl.delete(option)
        self.pl.commit()
        # then
        self.assertEqual(0, self.pl.count_options())

    def test_db_only_deleting_task_removes_all_children(self):
        # given
        parent = self.pl.DbTask('parent')
        c1 = self.pl.DbTask('c1')
        c2 = self.pl.DbTask('c2')
        c3 = self.pl.DbTask('c3')
        parent.children.append(c1)
        parent.children.append(c2)
        parent.children.append(c3)
        self.pl.db.session.add(parent)
        self.pl.db.session.add(c1)
        self.pl.db.session.add(c2)
        self.pl.db.session.add(c3)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(c1, parent.children)
        self.assertIn(c2, parent.children)
        self.assertIn(c3, parent.children)

        # when
        self.pl.db.session.delete(parent)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(c1, parent.children)
        self.assertNotIn(c2, parent.children)
        self.assertNotIn(c3, parent.children)
        self.assertEqual(0, len(parent.children.all()))

    def test_db_only_deleting_parent_task_nullifies_parent_and_parent_id(self):
        # given
        parent = self.pl.DbTask('parent')
        c1 = self.pl.DbTask('c1')
        c2 = self.pl.DbTask('c2')
        c3 = self.pl.DbTask('c3')
        parent.children.append(c1)
        parent.children.append(c2)
        parent.children.append(c3)
        self.pl.db.session.add(parent)
        self.pl.db.session.add(c1)
        self.pl.db.session.add(c2)
        self.pl.db.session.add(c3)
        self.pl.db.session.commit()

        # precondition
        self.assertIs(parent, c1.parent)
        self.assertIs(parent, c2.parent)
        self.assertIs(parent, c3.parent)

        # when
        self.pl.db.session.delete(parent)
        self.pl.db.session.commit()

        # then
        self.assertIsNone(c1.parent)
        self.assertIsNone(c2.parent)
        self.assertIsNone(c3.parent)
        self.assertIsNone(c1.parent_id)
        self.assertIsNone(c2.parent_id)
        self.assertIsNone(c3.parent_id)

    def test_db_only_deleting_task_removes_task_from_tag(self):
        # given
        task = self.pl.DbTask('task')
        tag = self.pl.DbTag('tag')
        task.tags.append(tag)
        self.pl.db.session.add(task)
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(task, tag.tasks)

    def test_notice_db_only_deleting_task_does_not_remove_tag_from_task(self):
        # given
        task = self.pl.DbTask('task')
        tag = self.pl.DbTag('tag')
        task.tags.append(tag)
        self.pl.db.session.add(task)
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertIn(tag, task.tags)

    def test_db_only_deleting_tag_removes_tag_from_task(self):
        # given
        task = self.pl.DbTask('task')
        tag = self.pl.DbTag('tag')
        task.tags.append(tag)
        self.pl.db.session.add(task)
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.db.session.delete(tag)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(tag, task.tags)

    def test_notice_db_only_deleting_tag_does_not_remove_task_from_tag(self):
        # given
        task = self.pl.DbTask('task')
        tag = self.pl.DbTag('tag')
        task.tags.append(tag)
        self.pl.db.session.add(task)
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.db.session.delete(tag)
        self.pl.db.session.commit()

        # then
        self.assertIn(task, tag.tasks)

    def test_db_only_deleting_task_removes_task_from_user(self):
        # given
        task = self.pl.DbTask('task')
        user = self.pl.DbUser('user')
        task.users.append(user)
        self.pl.db.session.add(task)
        self.pl.db.session.add(user)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(task, user.tasks)

    def test_notice_db_only_deleting_task_does_not_remove_user_from_task(self):
        # given
        task = self.pl.DbTask('task')
        user = self.pl.DbUser('user')
        task.users.append(user)
        self.pl.db.session.add(task)
        self.pl.db.session.add(user)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertIn(user, task.users)

    def test_db_only_deleting_user_removes_user_from_task(self):
        # given
        task = self.pl.DbTask('task')
        user = self.pl.DbUser('user')
        task.users.append(user)
        self.pl.db.session.add(task)
        self.pl.db.session.add(user)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.db.session.delete(user)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(user, task.users)

    def test_notice_db_only_deleting_user_does_not_remove_task_from_user(self):
        # given
        task = self.pl.DbTask('task')
        user = self.pl.DbUser('user')
        task.users.append(user)
        self.pl.db.session.add(task)
        self.pl.db.session.add(user)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.db.session.delete(user)
        self.pl.db.session.commit()

        # then
        self.assertIn(task, user.tasks)

    def test_db_only_deleting_dependee_removes_dependee_from_dependant(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.dependees.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.dependees)
        self.assertIn(t1, t2.dependants)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(t2, t1.dependees)

    def test_notice_db_only_deleting_dependee_does_not_remove_dependant(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.dependees.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.dependees)
        self.assertIn(t1, t2.dependants)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertIn(t1, t2.dependants)

    def test_db_only_deleting_dependant_removes_dependant_from_dependee(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.dependants.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.dependants)
        self.assertIn(t1, t2.dependees)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(t2, t1.dependants)

    def test_notice_db_only_deleting_dependant_does_not_remove_dependee(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.dependants.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.dependants)
        self.assertIn(t1, t2.dependees)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertIn(t1, t2.dependees)

    def test_db_only_deleting_pbefore_removes_pbefore_from_pafter(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.prioritize_before.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_before)
        self.assertIn(t1, t2.prioritize_after)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(t2, t1.prioritize_before)

    def test_notice_db_only_deleting_pbefore_does_not_remove_pafter(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.prioritize_before.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_before)
        self.assertIn(t1, t2.prioritize_after)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertIn(t1, t2.prioritize_after)

    def test_db_only_deleting_pafter_removes_pafter_from_pbefore(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.prioritize_after.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_after)
        self.assertIn(t1, t2.prioritize_before)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(t2, t1.prioritize_after)

    def test_notice_db_only_deleting_pafter_does_not_remove_pbefore(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.prioritize_after.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_after)
        self.assertIn(t1, t2.prioritize_before)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertIn(t1, t2.prioritize_before)

    def test_db_only_deleting_task_removes_all_notes(self):
        # given
        task = self.pl.DbTask('task')
        n1 = self.pl.DbNote('n1')
        n2 = self.pl.DbNote('n2')
        n3 = self.pl.DbNote('n3')
        task.notes.append(n1)
        task.notes.append(n2)
        task.notes.append(n3)
        self.pl.db.session.add(task)
        self.pl.db.session.add(n1)
        self.pl.db.session.add(n2)
        self.pl.db.session.add(n3)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(n1, task.notes)
        self.assertIn(n2, task.notes)
        self.assertIn(n3, task.notes)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(n1, task.notes)
        self.assertNotIn(n2, task.notes)
        self.assertNotIn(n3, task.notes)
        self.assertEqual(0, len(task.notes.all()))

    def test_db_only_deleting_task_of_notes_nullifies_task_and_task_id(self):
        # given
        task = self.pl.DbTask('task')
        n1 = self.pl.DbNote('n1')
        n2 = self.pl.DbNote('n2')
        n3 = self.pl.DbNote('n3')
        task.notes.append(n1)
        task.notes.append(n2)
        task.notes.append(n3)
        self.pl.db.session.add(task)
        self.pl.db.session.add(n1)
        self.pl.db.session.add(n2)
        self.pl.db.session.add(n3)
        self.pl.db.session.commit()

        # precondition
        self.assertIs(task, n1.task)
        self.assertIs(task, n2.task)
        self.assertIs(task, n3.task)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertIsNone(n1.task)
        self.assertIsNone(n2.task)
        self.assertIsNone(n3.task)
        self.assertIsNone(n1.task_id)
        self.assertIsNone(n2.task_id)
        self.assertIsNone(n3.task_id)

    def test_db_only_deleting_task_removes_all_attachments(self):
        # given
        task = self.pl.DbTask('task')
        n1 = self.pl.DbAttachment('n1')
        n2 = self.pl.DbAttachment('n2')
        n3 = self.pl.DbAttachment('n3')
        task.attachments.append(n1)
        task.attachments.append(n2)
        task.attachments.append(n3)
        self.pl.db.session.add(task)
        self.pl.db.session.add(n1)
        self.pl.db.session.add(n2)
        self.pl.db.session.add(n3)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(n1, task.attachments)
        self.assertIn(n2, task.attachments)
        self.assertIn(n3, task.attachments)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(n1, task.attachments)
        self.assertNotIn(n2, task.attachments)
        self.assertNotIn(n3, task.attachments)
        self.assertEqual(0, len(task.attachments.all()))

    def test_db_only_deleting_task_of_atts_nullifies_task_and_task_id(self):
        # given
        task = self.pl.DbTask('task')
        n1 = self.pl.DbAttachment('n1')
        n2 = self.pl.DbAttachment('n2')
        n3 = self.pl.DbAttachment('n3')
        task.attachments.append(n1)
        task.attachments.append(n2)
        task.attachments.append(n3)
        self.pl.db.session.add(task)
        self.pl.db.session.add(n1)
        self.pl.db.session.add(n2)
        self.pl.db.session.add(n3)
        self.pl.db.session.commit()

        # precondition
        self.assertIs(task, n1.task)
        self.assertIs(task, n2.task)
        self.assertIs(task, n3.task)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertIsNone(n1.task)
        self.assertIsNone(n2.task)
        self.assertIsNone(n3.task)
        self.assertIsNone(n1.task_id)
        self.assertIsNone(n2.task_id)
        self.assertIsNone(n3.task_id)


class DeletionTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_deleting_task_removes_all_children(self):
        # given
        parent = self.pl.create_task('parent')
        c1 = self.pl.create_task('c1')
        c2 = self.pl.create_task('c2')
        c3 = self.pl.create_task('c3')
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
        self.assertEqual(0, parent.children.count())

    def test_deleting_parent_task_nullifies_parent_and_parent_id(self):
        # given
        parent = self.pl.create_task('parent')
        c1 = self.pl.create_task('c1')
        c2 = self.pl.create_task('c2')
        c3 = self.pl.create_task('c3')
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
        task = self.pl.create_task('task')
        tag = self.pl.create_tag('tag')
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
        task = self.pl.create_task('task')
        tag = self.pl.create_tag('tag')
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
        task = self.pl.create_task('task')
        tag = self.pl.create_tag('tag')
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
        task = self.pl.create_task('task')
        tag = self.pl.create_tag('tag')
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
        task = self.pl.create_task('task')
        user = self.pl.create_user('user')
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
        task = self.pl.create_task('task')
        user = self.pl.create_user('user')
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
        task = self.pl.create_task('task')
        user = self.pl.create_user('user')
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
        task = self.pl.create_task('task')
        user = self.pl.create_user('user')
        task.users.append(user)
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertIn(user, list(task.users))
        self.assertIn(task, list(user.tasks))

        # when
        self.pl.delete(user)
        self.pl.commit()

        # then
        self.assertNotIn(task, list(user.tasks))

    def test_deleting_dependee_removes_dependee_from_dependant(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
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
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
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
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
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
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
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
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
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
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
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
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
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
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
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
        task = self.pl.create_task('task')
        n1 = self.pl.create_note('n1')
        n2 = self.pl.create_note('n2')
        n3 = self.pl.create_note('n3')
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
        self.assertEqual(0, task.notes.count())

    def test_deleting_task_of_notes_nullifies_task_and_task_id(self):
        # given
        task = self.pl.create_task('task')
        n1 = self.pl.create_note('n1')
        n2 = self.pl.create_note('n2')
        n3 = self.pl.create_note('n3')
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
        task = self.pl.create_task('task')
        a1 = self.pl.create_attachment('a1')
        a2 = self.pl.create_attachment('a2')
        a3 = self.pl.create_attachment('a3')
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
        self.assertEqual(0, task.attachments.count())

    def test_deleting_task_of_atts_nullifies_task_and_task_id(self):
        # given
        task = self.pl.create_task('task')
        a1 = self.pl.create_attachment('a1')
        a2 = self.pl.create_attachment('a2')
        a3 = self.pl.create_attachment('a3')
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


class AddDeleteTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    # def test_add_after_add_silently_ignored(self):
    #     # given
    #     task = self.pl.create_task('task')
    #     self.pl.add(task)
    #     # precondition
    #     self.assertIn(task, self.pl._added_objects)
    #     # when
    #     self.pl.add(task)
    #     # then
    #     self.assertIn(task, self.pl._added_objects)

    # def test_delete_after_delete_silently_ignored(self):
    #     # given
    #     task = self.pl.create_task('task')
    #     self.pl.add(task)
    #     self.pl.commit()
    #     self.pl.delete(task)
    #     # precondition
    #     self.assertIn(task, self.pl._deleted_objects)
    #     # when
    #     self.pl.delete(task)
    #     # then
    #     self.assertIn(task, self.pl._deleted_objects)
    #
    # def test_delete_after_add_raises(self):
    #     # given
    #     task = self.pl.create_task('task')
    #     self.pl.add(task)
    #     # precondition
    #     self.assertIn(task, self.pl._added_objects)
    #     self.assertNotIn(task, self.pl._deleted_objects)
    #     # when
    #     self.assertRaises(
    #         Exception,
    #         self.pl.delete,
    #         task)
    #     # then
    #     self.assertIn(task, self.pl._added_objects)
    #     self.assertNotIn(task, self.pl._deleted_objects)
    #
    # def test_add_after_delete_raises(self):
    #     # given
    #     task = self.pl.create_task('task')
    #     self.pl.add(task)
    #     self.pl.commit()
    #     self.pl.delete(task)
    #     # precondition
    #     self.assertNotIn(task, self.pl._added_objects)
    #     self.assertIn(task, self.pl._deleted_objects)
    #     # expect
    #     self.assertRaises(
    #         Exception,
    #         self.pl.add,
    #         task)
    #     # and
    #     self.assertNotIn(task, self.pl._added_objects)
    #     self.assertIn(task, self.pl._deleted_objects)

    # def test_add_an_object_already_committed_silently_ignored(self):
    #     # given
    #     task = self.pl.create_task('task')
    #     self.pl.add(task)
    #     tag = self.pl.create_tag('tag')
    #     self.pl.add(tag)
    #     attachment = self.pl.create_attachment('attachment')
    #     self.pl.add(attachment)
    #     note = self.pl.create_note('note')
    #     self.pl.add(note)
    #     user = self.pl.create_user('user')
    #     self.pl.add(user)
    #     option = self.pl.create_option('key', 'value')
    #     self.pl.add(option)
    #     self.pl.commit()
    #     # precondition
    #     self.assertIsNotNone(task.id)
    #     task2 = self.pl.get_task(task.id)
    #     self.assertIs(task2, task)
    #     self.assertIsNotNone(tag.id)
    #     tag2 = self.pl.get_tag(tag.id)
    #     self.assertIs(tag2, tag)
    #     self.assertIsNotNone(attachment.id)
    #     attachment2 = self.pl.get_attachment(attachment.id)
    #     self.assertIs(attachment2, attachment)
    #     self.assertIsNotNone(note.id)
    #     note2 = self.pl.get_note(note.id)
    #     self.assertIs(note2, note)
    #     self.assertIsNotNone(user.id)
    #     user2 = self.pl.get_user(user.id)
    #     self.assertIs(user2, user)
    #     self.assertIsNotNone(option.id)
    #     option2 = self.pl.get_option(option.id)
    #     self.assertIs(option2, option)
    #     # when
    #     self.pl.add(task)
    #     # then
    #     self.assertNotIn(task, self.pl._added_objects)
    #     # when
    #     self.pl.add(tag)
    #     # then
    #     self.assertNotIn(tag, self.pl._added_objects)
    #     # when
    #     self.pl.add(attachment)
    #     # then
    #     self.assertNotIn(attachment, self.pl._added_objects)
    #     # when
    #     self.pl.add(note)
    #     # then
    #     self.assertNotIn(note, self.pl._added_objects)
    #     # when
    #     self.pl.add(user)
    #     # then
    #     self.assertNotIn(user, self.pl._added_objects)
    #     # when
    #     self.pl.add(option)
    #     # then
    #     self.assertNotIn(option, self.pl._added_objects)
    #     # then
    #     self.assertEqual(0, len(self.pl._added_objects))


class DbDeletionTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    # def test_delete_of_db_only_object_gets_dbobj_from_db(self):
    #     dbtask = self.pl.DbTask('task')
    #     self.pl.db.session.add(dbtask)
    #     self.pl.db.session.commit()
    #
    #     task = self.pl.create_task('task')
    #     task.id = dbtask.id
    #
    #     # precondition
    #     self.assertEqual(0, len(self.pl._db_by_domain))
    #     self.assertEqual(0, len(self.pl._domain_by_db))
    #     self.assertEqual(0, len(self.pl._added_objects))
    #     self.assertEqual(0, len(self.pl._deleted_objects))
    #
    #     # when
    #     self.pl.delete(task)
    #     self.pl.commit()
    #
    #     # then nothing raised
    #     self.assertTrue(True)

    def test_delete_object_not_in_db_raises(self):

        # given
        task = self.pl.create_task('task')
        task.id = 1

        # expect
        self.assertRaises(Exception, self.pl.delete, task)

    # def test_rollback_of_deleted_objects(self):
    #
    #     # given
    #     task = self.pl.create_task('task')
    #     self.pl.add(task)
    #     task.description = 'a'
    #     self.pl.commit()
    #     self.pl.delete(task)
    #     task.description = 'b'
    #
    #     # precondition
    #     self.assertIn(task, self.pl._deleted_objects)
    #     self.assertEqual('b', task.description)
    #
    #     # when
    #     self.pl.rollback()
    #
    #     # then
    #     self.assertNotIn(task, self.pl._deleted_objects)
    #     self.assertEqual('a', task.description)
