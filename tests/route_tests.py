#!/usr/bin/env python

import unittest
from mock import Mock

from tudor import generate_app
from view_layer import ViewLayer


class RouteTest(unittest.TestCase):
    def setUp(self):
        vl = Mock(spec=ViewLayer)
        mock_method = Mock(return_value=('', 606))

        vl.index = mock_method
        vl.task_id_add_prioritize_after = mock_method
        vl.hierarchy = mock_method
        vl.task_id_add_dependant = mock_method
        vl.task_purge = mock_method
        vl.task_up = mock_method
        vl.task_down = mock_method
        vl.long_order_change = mock_method
        vl.deadlines = mock_method
        vl.task_hierarchy = mock_method
        vl.task_id_add_dependee = mock_method
        vl.task_bottom = mock_method
        vl.task_add_tag = mock_method
        vl.reset_order_nums = mock_method
        vl.purge_all = mock_method
        vl.task_id_add_prioritize_before = mock_method
        vl.task_mark_undone = mock_method
        vl.task_id_convert_to_tag = mock_method
        vl.task_id_remove_dependee = mock_method
        vl.task_pick_user = mock_method
        vl.show_hide_done = mock_method
        vl.export = mock_method
        vl.task_id_remove_prioritize_after = mock_method
        vl.task_edit = mock_method
        vl.task_new_post = mock_method
        vl.index = mock_method
        vl.option_delete = mock_method
        vl.task_crud = mock_method
        vl.import_ = mock_method
        vl.task_undelete = mock_method
        vl.note_new_post = mock_method
        vl.task_mark_done = mock_method
        vl.task_delete_tag = mock_method
        vl.attachment = mock_method
        vl.task_id_remove_dependant = mock_method
        vl.task_id_remove_prioritize_before = mock_method
        vl.task_authorize_user_user = mock_method
        vl.tags_id_get = mock_method
        vl.users = mock_method
        vl.tags = mock_method
        vl.task_authorize_user = mock_method
        vl.users_user_get = mock_method
        vl.attachment_new = mock_method
        vl.show_hide_deleted = mock_method
        vl.logout = mock_method
        vl.task_delete = mock_method
        vl.task_new_get = mock_method
        vl.search = mock_method
        vl.task = mock_method
        vl.task_top = mock_method
        vl.tags_id_edit = mock_method
        vl.login = mock_method
        vl.options = mock_method
        vl.task_deauthorize_user = mock_method

        ll = Mock()
        self.app = generate_app(vl=vl, ll=ll, configs={'LOGIN_DISABLED': True},
                                secret_key='12345', disable_admin_check=True)
        self.client = self.app.test_client()
        self.vl = vl
        self.mock_method = mock_method

    def test_index_get(self):
        resp = self.client.get('/')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_index_post(self):
        resp = self.client.post('/')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_hierarchy_get(self):
        resp = self.client.get('/hierarchy')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_hierarchy_post(self):
        resp = self.client.post('/hierarchy')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_deadlines_get(self):
        resp = self.client.get('/deadlines')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_deadlines_post(self):
        resp = self.client.post('/deadlines')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_new_get(self):
        resp = self.client.get('/task/new')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_new_post(self):
        resp = self.client.post('/task/new')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_mark_done_get(self):
        resp = self.client.get('/task/1/mark_done')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_mark_done_post(self):
        resp = self.client.post('/task/1/mark_done')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_mark_undone_get(self):
        resp = self.client.get('/task/1/mark_undone')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_mark_undone_post(self):
        resp = self.client.post('/task/1/mark_undone')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_delete_get(self):
        resp = self.client.get('/task/1/delete')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_delete_post(self):
        resp = self.client.post('/task/1/delete')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_undelete_get(self):
        resp = self.client.get('/task/1/undelete')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_undelete_post(self):
        resp = self.client.post('/task/1/undelete')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_purge_get(self):
        resp = self.client.get('/task/1/purge')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_purge_post(self):
        resp = self.client.post('/task/1/purge')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_purge_all_get(self):
        resp = self.client.get('/purge_all')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_purge_all_post(self):
        resp = self.client.post('/purge_all')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_get(self):
        resp = self.client.get('/task/1')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_post(self):
        resp = self.client.post('/task/1')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_hierarchy_get(self):
        resp = self.client.get('/task/1/hierarchy')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_hierarchy_post(self):
        resp = self.client.post('/task/1/hierarchy')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_note_new_post_get(self):
        resp = self.client.get('/note/new')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_note_new_post_post(self):
        resp = self.client.post('/note/new')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_edit_get(self):
        resp = self.client.get('/task/1/edit')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_edit_post(self):
        resp = self.client.post('/task/1/edit')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_attachment_new_get(self):
        resp = self.client.get('/attachment/new')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_attachment_new_post(self):
        resp = self.client.post('/attachment/new')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_attachment_get(self):
        resp = self.client.get('/attachment/1')
        self.assertEqual(301, resp.status_code)
        self.mock_method.assert_not_called()

    def test_attachment_slash_get(self):
        resp = self.client.get('/attachment/1/')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_attachment_slash_name_get(self):
        resp = self.client.get('/attachment/1/x')
        self.assertEqual(301, resp.status_code)
        self.mock_method.assert_not_called()

    def test_attachment_post(self):
        resp = self.client.post('/attachment/1')
        self.assertEqual(301, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_up_get(self):
        resp = self.client.get('/task/1/up')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_up_post(self):
        resp = self.client.post('/task/1/up')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_top_get(self):
        resp = self.client.get('/task/1/top')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_top_post(self):
        resp = self.client.post('/task/1/top')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_down_get(self):
        resp = self.client.get('/task/1/down')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_down_post(self):
        resp = self.client.post('/task/1/down')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_bottom_get(self):
        resp = self.client.get('/task/1/bottom')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_bottom_post(self):
        resp = self.client.post('/task/1/bottom')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_long_order_change_get(self):
        resp = self.client.get('/long_order_change')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_long_order_change_post(self):
        resp = self.client.post('/long_order_change')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_add_tag_get(self):
        resp = self.client.get('/task/1/add_tag')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_add_tag_post(self):
        resp = self.client.post('/task/1/add_tag')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_delete_tag_get(self):
        resp = self.client.get('/task/1/delete_tag')
        self.assertEqual(301, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_delete_tag_slash_get(self):
        resp = self.client.get('/task/1/delete_tag/')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_delete_tag_slash_id_get(self):
        resp = self.client.get('/task/1/delete_tag/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_delete_tag_post(self):
        resp = self.client.post('/task/1/delete_tag')
        self.assertEqual(301, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_authorize_user_get(self):
        resp = self.client.get('/task/1/authorize_user')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_authorize_user_post(self):
        resp = self.client.post('/task/1/authorize_user')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_pick_user_get(self):
        resp = self.client.get('/task/1/pick_user')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_pick_user_post(self):
        resp = self.client.post('/task/1/pick_user')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_authorize_user_user_get(self):
        resp = self.client.get('/task/1/authorize_user/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_authorize_user_user_post(self):
        resp = self.client.post('/task/1/authorize_user/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_deauthorize_user_get(self):
        resp = self.client.get('/task/1/deauthorize_user')
        self.assertEqual(301, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_deauthorize_user_slash_get(self):
        resp = self.client.get('/task/1/deauthorize_user/')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_deauthorize_user_slash_id_get(self):
        resp = self.client.get('/task/1/deauthorize_user/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_deauthorize_user_post(self):
        resp = self.client.post('/task/1/deauthorize_user')
        self.assertEqual(301, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_deauthorize_user_slash_post(self):
        resp = self.client.post('/task/1/deauthorize_user/')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_deauthorize_user_slash_id_post(self):
        resp = self.client.post('/task/1/deauthorize_user/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_login_get(self):
        resp = self.client.get('/login')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_login_post(self):
        resp = self.client.post('/login')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_logout_get(self):
        resp = self.client.get('/logout')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_logout_post(self):
        resp = self.client.post('/logout')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_users_get(self):
        resp = self.client.get('/users')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_users_post(self):
        resp = self.client.post('/users')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_users_user_get_get(self):
        resp = self.client.get('/users/1')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_users_user_get_post(self):
        resp = self.client.post('/users/1')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_show_hide_deleted_get(self):
        resp = self.client.get('/show_hide_deleted')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_show_hide_deleted_post(self):
        resp = self.client.post('/show_hide_deleted')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_show_hide_done_get(self):
        resp = self.client.get('/show_hide_done')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_show_hide_done_post(self):
        resp = self.client.post('/show_hide_done')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_options_get(self):
        resp = self.client.get('/options')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_options_post(self):
        resp = self.client.post('/options')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_option_delete_get(self):
        resp = self.client.get('/option/1/delete')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_option_delete_post(self):
        resp = self.client.post('/option/1/delete')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_reset_order_nums_get(self):
        resp = self.client.get('/reset_order_nums')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_reset_order_nums_post(self):
        resp = self.client.post('/reset_order_nums')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_export_get(self):
        resp = self.client.get('/export')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_export_post(self):
        resp = self.client.post('/export')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_import__get(self):
        resp = self.client.get('/import')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_import__post(self):
        resp = self.client.post('/import')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_crud_get(self):
        resp = self.client.get('/task_crud')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_crud_post(self):
        resp = self.client.post('/task_crud')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_tags_get(self):
        resp = self.client.get('/tags')
        self.assertEqual(301, resp.status_code)
        self.mock_method.assert_not_called()

    def test_tags_post(self):
        resp = self.client.post('/tags')
        self.assertEqual(301, resp.status_code)
        self.mock_method.assert_not_called()

    def test_tags_id_get_get(self):
        resp = self.client.get('/tags/1')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_tags_id_get_post(self):
        resp = self.client.post('/tags/1')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_tags_id_edit_get(self):
        resp = self.client.get('/tags/1/edit')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_tags_id_edit_post(self):
        resp = self.client.post('/tags/1/edit')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_convert_to_tag_get(self):
        resp = self.client.get('/task/1/convert_to_tag')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_convert_to_tag_post(self):
        resp = self.client.post('/task/1/convert_to_tag')
        self.assertEqual(405, resp.status_code)
        self.mock_method.assert_not_called()

    def test_search_get(self):
        resp = self.client.get('/search')
        self.assertEqual(301, resp.status_code)
        self.mock_method.assert_not_called()

    def test_search_slash_get(self):
        resp = self.client.get('/search/')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_search_slash_value_get(self):
        resp = self.client.get('/search/x')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_search_post(self):
        resp = self.client.post('/search')
        self.assertEqual(301, resp.status_code)
        self.mock_method.assert_not_called()

    def test_search_slash_post(self):
        resp = self.client.post('/search')
        self.assertEqual(301, resp.status_code)
        self.mock_method.assert_not_called()

    def test_search_slash_value_post(self):
        resp = self.client.post('/search')
        self.assertEqual(301, resp.status_code)
        self.mock_method.assert_not_called()

    def test_task_id_add_dependee_get(self):
        resp = self.client.get('/task/1/add_dependee/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_add_dependee_post(self):
        resp = self.client.post('/task/1/add_dependee/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_remove_dependee_get(self):
        resp = self.client.get('/task/1/remove_dependee/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_remove_dependee_post(self):
        resp = self.client.post('/task/1/remove_dependee/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_add_dependant_get(self):
        resp = self.client.get('/task/1/add_dependant/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_add_dependant_post(self):
        resp = self.client.post('/task/1/add_dependant/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_remove_dependant_get(self):
        resp = self.client.get('/task/1/remove_dependant/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_remove_dependant_post(self):
        resp = self.client.post('/task/1/remove_dependant/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_add_prioritize_before_get(self):
        resp = self.client.get('/task/1/add_prioritize_before/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_add_prioritize_before_post(self):
        resp = self.client.post('/task/1/add_prioritize_before/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_remove_prioritize_before_get(self):
        resp = self.client.get('/task/1/remove_prioritize_before/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_remove_prioritize_before_post(self):
        resp = self.client.post('/task/1/remove_prioritize_before/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_add_prioritize_after_get(self):
        resp = self.client.get('/task/1/add_prioritize_after/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_add_prioritize_after_post(self):
        resp = self.client.post('/task/1/add_prioritize_after/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_remove_prioritize_after_get(self):
        resp = self.client.get('/task/1/remove_prioritize_after/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()

    def test_task_id_remove_prioritize_after_post(self):
        resp = self.client.post('/task/1/remove_prioritize_after/2')
        self.assertEqual(606, resp.status_code)
        self.mock_method.assert_called()
