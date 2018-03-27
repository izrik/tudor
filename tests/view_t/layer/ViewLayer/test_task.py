
import unittest

from mock import Mock

from logic.layer import LogicLayer
from tests.view_t.layer.ViewLayer.util import generate_mock_request
from view.layer import ViewLayer, DefaultRenderer


class TaskTest(unittest.TestCase):
    def setUp(self):
        self.ll = Mock(spec=LogicLayer)
        self.return_value = {
            'task': None,
            'descendants': [],
            'pager': None,
        }
        self.ll.get_task_data = Mock(return_value=self.return_value)
        self.r = Mock(spec=DefaultRenderer)
        self.vl = ViewLayer(self.ll, None, renderer=self.r)

    def test_gets_task_data_from_logic_layer(self):
        # given
        request = generate_mock_request(args={}, cookies={})
        user = Mock()
        TASK_ID = 1
        # when
        result = self.vl.task(request, user, TASK_ID)
        # then
        self.assertIsNotNone(result)
        self.ll.get_task_data.assert_called_with(TASK_ID, user,
                                                 include_deleted=None,
                                                 include_done=None,
                                                 page_num=1, tasks_per_page=20)
        self.r.render_template.assert_called()

    def test_page_num_not_int_defaults_to_one(self):
        # given
        request = generate_mock_request(args={'page': 'asdf'}, cookies={})
        user = Mock()
        TASK_ID = 1
        # when
        result = self.vl.task(request, user, TASK_ID)
        # then
        self.assertIsNotNone(result)
        self.ll.get_task_data.assert_called_with(TASK_ID, user,
                                                 include_deleted=None,
                                                 include_done=None,
                                                 page_num=1, tasks_per_page=20)
        self.r.render_template.assert_called()

    def test_task_per_page_not_int_default_to_twenty(self):
        # given
        request = generate_mock_request(args={'per_page': 'asdf'}, cookies={})
        user = Mock()
        TASK_ID = 1
        # when
        result = self.vl.task(request, user, TASK_ID)
        # then
        self.assertIsNotNone(result)
        self.ll.get_task_data.assert_called_with(TASK_ID, user,
                                                 include_deleted=None,
                                                 include_done=None,
                                                 page_num=1, tasks_per_page=20)
        self.r.render_template.assert_called()
