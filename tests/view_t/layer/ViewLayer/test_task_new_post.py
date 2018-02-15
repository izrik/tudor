import unittest

from mock import Mock

from logic.layer import LogicLayer
from models.user import User
from persistence.in_memory_persistence_layer import InMemoryPersistenceLayer
from tests.view_t.layer.ViewLayer.util import generate_mock_request
from view.layer import ViewLayer, DefaultRenderer


class TaskNewPostTest(unittest.TestCase):
    def setUp(self):
        self.pl = Mock(spec=InMemoryPersistenceLayer)
        self.ll = Mock(spec=LogicLayer)
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)
        self.admin = Mock(spec=User)

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
