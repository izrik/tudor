import unittest

from contextlib import nullcontext
from unittest.mock import Mock, MagicMock

from logic.layer import LogicLayer
from models.user_base import UserBase
from persistence.sqlalchemy.layer import SqlAlchemyPersistenceLayer
from tests.util import generate_test_app
from tests.view_t.layer.ViewLayer.util import generate_mock_request
from view.layer import ViewLayer, DefaultRenderer


class TaskNewPostTest(unittest.TestCase):
    def setUp(self):
        self.pl = Mock(spec=SqlAlchemyPersistenceLayer)
        self.ll = Mock(spec=LogicLayer)
        self.ll.transaction.return_value = nullcontext()
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)
        self.admin = Mock(spec=UserBase)

    def test_creates_new_task(self):
        # given
        request = generate_mock_request(method="POST")
        self.ll.get_lowest_order_num.return_value = 0
        # when
        result = self.vl.task_new_post(request, self.admin)
        # then
        self.ll.create_new_task.assert_called()
        self.ll.do_add_tag_to_task.assert_not_called()
        self.r.url_for.assert_called()
        self.r.redirect.assert_called()
        self.assertIs(self.r.redirect.return_value, result)

    def test_tag_in_form_adds_tag(self):
        # given
        request = generate_mock_request(method="POST", form={'tags': 'tag1'})
        self.ll.get_lowest_order_num.return_value = 0
        # when
        result = self.vl.task_new_post(request, self.admin)
        # then
        self.ll.create_new_task.assert_called()
        self.ll.do_add_tag_to_task.assert_called_once_with(
            self.ll.create_new_task.return_value, 'tag1', self.admin)
        self.r.url_for.assert_called()
        self.r.redirect.assert_called()
        self.assertIs(self.r.redirect.return_value, result)

    def test_two_tags_in_form_adds_both_tags(self):
        # given
        request = generate_mock_request(method="POST",
                                        form={'tags': 'tag1,tag2'})
        self.ll.get_lowest_order_num.return_value = 0
        # when
        result = self.vl.task_new_post(request, self.admin)
        # then
        self.ll.create_new_task.assert_called()
        self.ll.do_add_tag_to_task.assert_any_call(
            self.ll.create_new_task.return_value, 'tag1', self.admin)
        self.ll.do_add_tag_to_task.assert_any_call(
            self.ll.create_new_task.return_value, 'tag2', self.admin)
        self.assertEqual(2, self.ll.do_add_tag_to_task.call_count)
        self.r.url_for.assert_called()
        self.r.redirect.assert_called()
        self.assertIs(self.r.redirect.return_value, result)

    def test_creates_task_and_tags_in_one_transaction(self):
        # given
        events = []
        tx = MagicMock()
        tx.__enter__.side_effect = lambda: events.append('begin')
        tx.__exit__.side_effect = lambda *args: events.append('end')
        self.ll.transaction.return_value = tx
        self.ll.create_new_task.side_effect = \
            lambda **kwargs: events.append('create') or Mock()
        self.ll.do_add_tag_to_task.side_effect = \
            lambda *args: events.append('tag')
        request = generate_mock_request(method="POST", form={'tags': 'tag1'})
        self.ll.get_lowest_order_num.return_value = 0
        # when
        self.vl.task_new_post(request, self.admin)
        # then
        self.assertEqual(['begin', 'create', 'tag', 'end'], events)


class TaskNewPostWithRealLogicLayerTest(unittest.TestCase):
    """The new-task POST against a real logic and persistence layer, as in
    issue #157: a tag on the new task used to fail with an AttributeError."""

    def setUp(self):
        self.app = generate_test_app()
        self.pl = self.app.pl
        self.ll = self.app.ll
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)
        self.user = self.pl.create_user('name@example.org', None, False)
        self.pl.add(self.user)
        self.pl.commit()

    def post(self, **form):
        request = generate_mock_request(method='POST', form=form)
        return self.vl.task_new_post(request, self.user)

    def tags_of(self, task_id):
        return sorted(tag.value for tag in self.pl.get_tags(task_id=task_id))

    def get_task_by_summary(self, summary):
        tasks = [t for t in self.pl.get_tasks() if t.summary == summary]
        self.assertEqual(1, len(tasks))
        return tasks[0]

    def test_new_task_with_a_tag_gets_the_tag(self):
        # when
        self.post(summary='t1', tags='metaindu')
        # then
        task = self.get_task_by_summary('t1')
        self.assertEqual(['metaindu'], self.tags_of(task.id))

    def test_cloning_a_task_with_a_tag_and_children(self):
        # given
        original = self.ll.create_new_task(summary='original',
                                           current_user=self.user)
        self.ll.do_add_tag_to_task_by_id(original.id, 'metaindu', self.user)
        child = self.ll.create_new_task(summary='child', parent_id=original.id,
                                        current_user=self.user)
        self.ll.do_add_tag_to_task_by_id(child.id, 'metaindu', self.user)
        # when
        self.post(summary='clone', tags='metaindu', clone_id=str(original.id),
                  clone_children='true')
        # then
        clone = self.get_task_by_summary('clone')
        self.assertEqual(['metaindu'], self.tags_of(clone.id))
        children = list(self.pl.get_tasks(parent_id=clone.id))
        self.assertEqual(1, len(children))
        self.assertEqual('child', children[0].summary)
        self.assertEqual(['metaindu'], self.tags_of(children[0].id))
