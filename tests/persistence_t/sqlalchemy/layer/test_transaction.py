from models.tag import Tag
from models.task import Task
from models.user import User
from persistence.sqlalchemy.layer import RecordNotFound
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class TransactionTest(PersistenceLayerTestBase):
    def assert_committed(self, task_id):
        # A rollback discards anything that was only flushed.
        self.pl.db.session.rollback()
        self.assertIsNotNone(self.pl.get_task(task_id))

    def test_block_commits_on_exit(self):
        # when
        with self.pl.transaction():
            task = Task(summary='t')
            self.pl.save(task)
        # then
        self.assert_committed(task.id)

    def test_save_inside_block_assigns_id_immediately(self):
        with self.pl.transaction():
            # when
            task = Task(summary='t')
            self.pl.save(task)
            # then
            self.assertIsNotNone(task.id)

    def test_exception_rolls_back_every_write_in_block(self):
        # given
        user = User(email='name@example.org')
        self.pl.save(user)
        # when
        with self.assertRaises(RuntimeError):
            with self.pl.transaction():
                task = Task(summary='t')
                tag = Tag(value='x')
                self.pl.save(task, tag)
                self.pl.add_user_to_task(task.id, user.id)
                self.pl.add_tag_to_task(task.id, tag.id)
                raise RuntimeError()
        # then
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        # and writes from before the block are untouched
        self.assertIsNotNone(self.pl.get_user(user.id))

    def test_legacy_commit_inside_block_is_deferred(self):
        # when
        with self.assertRaises(RuntimeError):
            with self.pl.transaction():
                self.pl.add(self.pl.create_tag('x'))
                self.pl.commit()
                raise RuntimeError()
        # then
        self.assertIsNone(self.pl.get_tag_by_value('x'))

    def test_nested_blocks_commit_only_at_outermost(self):
        # when
        with self.assertRaises(RuntimeError):
            with self.pl.transaction():
                with self.pl.transaction():
                    self.pl.save(Task(summary='inner'))
                raise RuntimeError()
        # then
        self.assertEqual(0, self.pl.count_tasks())

    def test_writes_after_a_rolled_back_block_commit_normally(self):
        # given
        with self.assertRaises(RuntimeError):
            with self.pl.transaction():
                self.pl.save(Task(summary='t1'))
                raise RuntimeError()
        # when
        task = Task(summary='t2')
        self.pl.save(task)
        # then
        self.assert_committed(task.id)


class SaveDeleteRollbackTest(PersistenceLayerTestBase):
    def test_failed_save_rolls_back_earlier_objects(self):
        # given
        good = Task(summary='good')
        bad = Task(summary='bad', id=9999)
        # when
        with self.assertRaises(RecordNotFound):
            self.pl.save(good, bad)
        # then
        self.assertEqual(0, self.pl.count_tasks())

    def test_failed_delete_rolls_back_earlier_deletes(self):
        # given
        task = Task(summary='t')
        self.pl.save(task)
        missing = Task(summary='missing', id=9999)
        # when
        with self.assertRaises(RecordNotFound):
            self.pl.delete(task, missing)
        # then
        self.assertIsNotNone(self.pl.get_task(task.id))
