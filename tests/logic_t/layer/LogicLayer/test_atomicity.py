import unittest
from unittest.mock import patch

from tests.logic_t.layer.LogicLayer.util import generate_ll


def fail_on_call(real, n):
    """Wrap a PL method so that its nth call raises instead."""
    calls = []

    def wrapper(*args, **kwargs):
        calls.append(args)
        if len(calls) == n:
            raise RuntimeError('injected failure')
        return real(*args, **kwargs)
    return wrapper


class LogicLayerAtomicityTest(unittest.TestCase):
    """Operations that make several PL writes must leave nothing behind if
    they fail part way through."""

    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.admin = self.pl.create_user('admin@example.org', None, True)
        self.pl.add(self.admin)
        self.pl.commit()

    def new_task(self, summary, **kwargs):
        return self.ll.create_new_task(summary=summary,
                                       current_user=self.admin, **kwargs)

    def test_create_new_task_failure_leaves_no_task(self):
        # when
        with patch.object(self.pl, 'add_user_to_task',
                          side_effect=RuntimeError()):
            with self.assertRaises(RuntimeError):
                self.new_task('t')
        # then
        self.assertEqual(0, self.pl.count_tasks())

    def test_do_add_tag_to_task_failure_leaves_no_new_tag(self):
        # given
        task = self.new_task('t')
        # when
        with patch.object(self.pl, 'add_tag_to_task',
                          side_effect=RuntimeError()):
            with self.assertRaises(RuntimeError):
                self.ll.do_add_tag_to_task(task, 'new-tag', self.admin)
        # then
        self.assertIsNone(self.pl.get_tag_by_value('new-tag'))

    def test_convert_task_to_tag_failure_changes_nothing(self):
        # given
        grandparent = self.new_task('gp')
        parent = self.new_task('p', parent_id=grandparent.id)
        child = self.new_task('c', parent_id=parent.id)
        # when
        with patch.object(self.pl, 'delete', side_effect=RuntimeError()):
            with self.assertRaises(RuntimeError):
                self.ll.convert_task_to_tag(parent.id, self.admin)
        # then no tag was created
        self.assertIsNone(self.pl.get_tag_by_value('p'))
        # and the tasks are unchanged
        self.assertEqual(grandparent.id,
                         self.pl.get_task(parent.id).parent_id)
        self.assertEqual(parent.id, self.pl.get_task(child.id).parent_id)

    def test_purge_all_deleted_tasks_failure_purges_nothing(self):
        # given
        self.new_task('t1', is_deleted=True)
        self.new_task('t2', is_deleted=True)
        # when
        with patch.object(self.pl, 'delete',
                          side_effect=fail_on_call(self.pl.delete, 2)):
            with self.assertRaises(RuntimeError):
                self.ll.purge_all_deleted_tasks(self.admin)
        # then
        self.assertEqual(2, self.pl.count_tasks(is_deleted=True))

    def test_clone_children_failure_clones_nothing(self):
        # given
        original = self.new_task('original')
        self.new_task('c1', parent_id=original.id)
        self.new_task('c2', parent_id=original.id)
        copy = self.new_task('copy')
        # when
        with patch.object(self.pl, 'add_user_to_task',
                          side_effect=fail_on_call(self.pl.add_user_to_task,
                                                   2)):
            with self.assertRaises(RuntimeError):
                self.ll.clone_task_children_recursive(original.id, copy.id,
                                                      self.admin)
        # then
        self.assertEqual(0, self.pl.count_tasks(parent_id=copy.id))
