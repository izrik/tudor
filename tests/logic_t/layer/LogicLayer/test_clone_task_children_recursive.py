#!/usr/bin/env python

import unittest

from tests.logic_t.layer.LogicLayer.util import generate_ll


class CloneTaskChildrenRecursiveTest(unittest.TestCase):

    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.user = self.pl.create_user('name@example.org', None, False)
        self.pl.add(self.user)
        self.pl.commit()

    def new_task(self, summary, **kwargs):
        return self.ll.create_new_task(summary=summary,
                                       current_user=self.user, **kwargs)

    def tags_of(self, task_id):
        return sorted(tag.value for tag in self.pl.get_tags(task_id=task_id))

    def test_clones_children(self):
        # given
        original = self.new_task('original')
        self.new_task('c1', parent_id=original.id)
        self.new_task('c2', parent_id=original.id)
        copy = self.new_task('copy')

        # when
        self.ll.clone_task_children_recursive(original.id, copy.id, self.user)

        # then
        children = list(self.pl.get_tasks(parent_id=copy.id))
        self.assertEqual({'c1', 'c2'}, {c.summary for c in children})

    def test_clones_grandchildren(self):
        # given
        original = self.new_task('original')
        child = self.new_task('c1', parent_id=original.id)
        self.new_task('gc1', parent_id=child.id)
        copy = self.new_task('copy')

        # when
        self.ll.clone_task_children_recursive(original.id, copy.id, self.user)

        # then
        new_children = list(self.pl.get_tasks(parent_id=copy.id))
        self.assertEqual(1, len(new_children))
        new_grandchildren = list(
            self.pl.get_tasks(parent_id=new_children[0].id))
        self.assertEqual(['gc1'], [gc.summary for gc in new_grandchildren])

    def test_clones_the_tags_of_the_children(self):
        # given
        original = self.new_task('original')
        child = self.new_task('c1', parent_id=original.id)
        self.ll.do_add_tag_to_task_by_id(child.id, 'metaindu', self.user)
        copy = self.new_task('copy')

        # when
        self.ll.clone_task_children_recursive(original.id, copy.id, self.user)

        # then
        children = list(self.pl.get_tasks(parent_id=copy.id))
        self.assertEqual(1, len(children))
        self.assertEqual(['metaindu'], self.tags_of(children[0].id))
        # the original keeps its tag, too
        self.assertEqual(['metaindu'], self.tags_of(child.id))
