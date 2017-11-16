
import unittest
from mock import Mock

from tudor import generate_app
from view_layer import ViewLayer, DefaultRenderer
from logic_layer import LogicLayer


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
        self.vl = ViewLayer(self.ll, None, '', None, renderer=self.r)
        self.app = generate_app(vl=self.vl, ll=self.ll, pl=None,
                                configs={'LOGIN_DISABLED': True},
                                secret_key='12345', disable_admin_check=True)
        self.vl.app = self.app

    def test_gets_task_data_from_logic_layer(self):
        # given
        request = Mock()
        request.args = {}
        request.cookies = {}
        user = Mock()
        TASK_ID = 1
        # when
        with self.app.app_context():
            result = self.vl.task(request, user, TASK_ID)
        # then
        self.ll.get_task_data.assert_called_with(TASK_ID, user,
                                                 include_deleted=None,
                                                 include_done=None,
                                                 page_num=1, tasks_per_page=20)
        self.r.render_template.assert_called()

    def test_page_num_not_int_defaults_to_one(self):
        # given
        request = Mock()
        request.args = {'page': 'asdf'}
        request.cookies = {}
        user = Mock()
        TASK_ID = 1
        # when
        with self.app.app_context():
            result = self.vl.task(request, user, TASK_ID)
        # then
        self.ll.get_task_data.assert_called_with(TASK_ID, user,
                                                 include_deleted=None,
                                                 include_done=None,
                                                 page_num=1, tasks_per_page=20)
        self.r.render_template.assert_called()

    def test_task_per_page_not_int_default_to_twenty(self):
        # given
        request = Mock()
        request.args = {'per_page': 'asdf'}
        request.cookies = {}
        user = Mock()
        TASK_ID = 1
        # when
        with self.app.app_context():
            result = self.vl.task(request, user, TASK_ID)
        # then
        self.ll.get_task_data.assert_called_with(TASK_ID, user,
                                                 include_deleted=None,
                                                 include_done=None,
                                                 page_num=1, tasks_per_page=20)
        self.r.render_template.assert_called()

