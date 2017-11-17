#!/usr/bin/env python

import unittest
from mock import Mock

from tudor import generate_app
from view_layer import ViewLayer


class RouteTest(unittest.TestCase):
    def setUp(self):
        vl = Mock(spec=ViewLayer)

        vl.index = Mock(return_value=('', 606))
        vl.task_id_add_prioritize_after = Mock(return_value=('', 606))
        vl.hierarchy = Mock(return_value=('', 606))
        vl.task_id_add_dependant = Mock(return_value=('', 606))
        vl.task_purge = Mock(return_value=('', 606))
        vl.task_up = Mock(return_value=('', 606))
        vl.task_down = Mock(return_value=('', 606))
        vl.long_order_change = Mock(return_value=('', 606))
        vl.deadlines = Mock(return_value=('', 606))
        vl.task_hierarchy = Mock(return_value=('', 606))
        vl.task_id_add_dependee = Mock(return_value=('', 606))
        vl.task_bottom = Mock(return_value=('', 606))
        vl.task_add_tag = Mock(return_value=('', 606))
        vl.reset_order_nums = Mock(return_value=('', 606))
        vl.purge_all = Mock(return_value=('', 606))
        vl.task_id_add_prioritize_before = Mock(return_value=('', 606))
        vl.task_mark_undone = Mock(return_value=('', 606))
        vl.task_id_convert_to_tag = Mock(return_value=('', 606))
        vl.task_id_remove_dependee = Mock(return_value=('', 606))
        vl.task_pick_user = Mock(return_value=('', 606))
        vl.show_hide_done = Mock(return_value=('', 606))
        vl.export = Mock(return_value=('', 606))
        vl.task_id_remove_prioritize_after = Mock(return_value=('', 606))
        vl.task_edit = Mock(return_value=('', 606))
        vl.task_new_post = Mock(return_value=('', 606))
        vl.index = Mock(return_value=('', 606))
        vl.option_delete = Mock(return_value=('', 606))
        vl.task_crud = Mock(return_value=('', 606))
        vl.import_ = Mock(return_value=('', 606))
        vl.task_undelete = Mock(return_value=('', 606))
        vl.note_new_post = Mock(return_value=('', 606))
        vl.task_mark_done = Mock(return_value=('', 606))
        vl.task_delete_tag = Mock(return_value=('', 606))
        vl.attachment = Mock(return_value=('', 606))
        vl.task_id_remove_dependant = Mock(return_value=('', 606))
        vl.task_id_remove_prioritize_before = Mock(return_value=('', 606))
        vl.task_authorize_user_user = Mock(return_value=('', 606))
        vl.tags_id_get = Mock(return_value=('', 606))
        vl.users = Mock(return_value=('', 606))
        vl.tags = Mock(return_value=('', 606))
        vl.task_authorize_user = Mock(return_value=('', 606))
        vl.users_user_get = Mock(return_value=('', 606))
        vl.attachment_new = Mock(return_value=('', 606))
        vl.show_hide_deleted = Mock(return_value=('', 606))
        vl.logout = Mock(return_value=('', 606))
        vl.task_delete = Mock(return_value=('', 606))
        vl.task_new_get = Mock(return_value=('', 606))
        vl.search = Mock(return_value=('', 606))
        vl.task = Mock(return_value=('', 606))
        vl.task_top = Mock(return_value=('', 606))
        vl.tags_id_edit = Mock(return_value=('', 606))
        vl.login = Mock(return_value=('', 606))
        vl.options = Mock(return_value=('', 606))
        vl.task_deauthorize_user = Mock(return_value=('', 606))

        ll = Mock()
        self.app = generate_app(vl=vl, ll=ll, flask_configs={'LOGIN_DISABLED': True},
                                secret_key='12345', disable_admin_check=True)
        self.client = self.app.test_client()
        self.vl = vl

    def test_index_get(self):
        resp = self.client.get('/')
        self.assertEqual(606, resp.status_code)
        self.vl.index.assert_called()

    def test_index_post(self):
        resp = self.client.post('/')
        self.assertEqual(405, resp.status_code)
        self.vl.index.assert_not_called()

    def test_hierarchy_get(self):
        resp = self.client.get('/hierarchy')
        self.assertEqual(606, resp.status_code)
        self.vl.hierarchy.assert_called()

    def test_hierarchy_post(self):
        resp = self.client.post('/hierarchy')
        self.assertEqual(405, resp.status_code)
        self.vl.hierarchy.assert_not_called()

    def test_deadlines_get(self):
        resp = self.client.get('/deadlines')
        self.assertEqual(606, resp.status_code)
        self.vl.deadlines.assert_called()

    def test_deadlines_post(self):
        resp = self.client.post('/deadlines')
        self.assertEqual(405, resp.status_code)
        self.vl.deadlines.assert_not_called()

    def test_task_new_get(self):
        resp = self.client.get('/task/new')
        self.assertEqual(606, resp.status_code)
        self.vl.task_new_get.assert_called()

    def test_task_new_post(self):
        resp = self.client.post('/task/new')
        self.assertEqual(606, resp.status_code)
        self.vl.task_new_post.assert_called()

    def test_task_mark_done_get(self):
        resp = self.client.get('/task/1/mark_done')
        self.assertEqual(606, resp.status_code)
        self.vl.task_mark_done.assert_called()

    def test_task_mark_done_post(self):
        resp = self.client.post('/task/1/mark_done')
        self.assertEqual(405, resp.status_code)
        self.vl.task_mark_done.assert_not_called()

    def test_task_mark_undone_get(self):
        resp = self.client.get('/task/1/mark_undone')
        self.assertEqual(606, resp.status_code)
        self.vl.task_mark_undone.assert_called()

    def test_task_mark_undone_post(self):
        resp = self.client.post('/task/1/mark_undone')
        self.assertEqual(405, resp.status_code)
        self.vl.task_mark_undone.assert_not_called()

    def test_task_delete_get(self):
        resp = self.client.get('/task/1/delete')
        self.assertEqual(606, resp.status_code)
        self.vl.task_delete.assert_called()

    def test_task_delete_post(self):
        resp = self.client.post('/task/1/delete')
        self.assertEqual(405, resp.status_code)
        self.vl.task_delete.assert_not_called()

    def test_task_undelete_get(self):
        resp = self.client.get('/task/1/undelete')
        self.assertEqual(606, resp.status_code)
        self.vl.task_undelete.assert_called()

    def test_task_undelete_post(self):
        resp = self.client.post('/task/1/undelete')
        self.assertEqual(405, resp.status_code)
        self.vl.task_undelete.assert_not_called()

    def test_task_purge_get(self):
        resp = self.client.get('/task/1/purge')
        self.assertEqual(606, resp.status_code)
        self.vl.task_purge.assert_called()

    def test_task_purge_post(self):
        resp = self.client.post('/task/1/purge')
        self.assertEqual(405, resp.status_code)
        self.vl.task_purge.assert_not_called()

    def test_purge_all_get(self):
        resp = self.client.get('/purge_all')
        self.assertEqual(606, resp.status_code)
        self.vl.purge_all.assert_called()

    def test_purge_all_post(self):
        resp = self.client.post('/purge_all')
        self.assertEqual(405, resp.status_code)
        self.vl.purge_all.assert_not_called()

    def test_task_get(self):
        resp = self.client.get('/task/1')
        self.assertEqual(606, resp.status_code)
        self.vl.task.assert_called()

    def test_task_post(self):
        resp = self.client.post('/task/1')
        self.assertEqual(405, resp.status_code)
        self.vl.task.assert_not_called()

    def test_task_hierarchy_get(self):
        resp = self.client.get('/task/1/hierarchy')
        self.assertEqual(606, resp.status_code)
        self.vl.task_hierarchy.assert_called()

    def test_task_hierarchy_post(self):
        resp = self.client.post('/task/1/hierarchy')
        self.assertEqual(405, resp.status_code)
        self.vl.task_hierarchy.assert_not_called()

    def test_note_new_post_get(self):
        resp = self.client.get('/note/new')
        self.assertEqual(405, resp.status_code)
        self.vl.note_new_post.assert_not_called()

    def test_note_new_post_post(self):
        resp = self.client.post('/note/new')
        self.assertEqual(606, resp.status_code)
        self.vl.note_new_post.assert_called()

    def test_task_edit_get(self):
        resp = self.client.get('/task/1/edit')
        self.assertEqual(606, resp.status_code)
        self.vl.task_edit.assert_called()

    def test_task_edit_post(self):
        resp = self.client.post('/task/1/edit')
        self.assertEqual(606, resp.status_code)
        self.vl.task_edit.assert_called()

    def test_attachment_new_get(self):
        resp = self.client.get('/attachment/new')
        self.assertEqual(405, resp.status_code)
        self.vl.attachment_new.assert_not_called()

    def test_attachment_new_post(self):
        resp = self.client.post('/attachment/new')
        self.assertEqual(606, resp.status_code)
        self.vl.attachment_new.assert_called()

    def test_attachment_get(self):
        resp = self.client.get('/attachment/1')
        self.assertEqual(301, resp.status_code)
        self.vl.attachment.assert_not_called()

    def test_attachment_slash_get(self):
        resp = self.client.get('/attachment/1/')
        self.assertEqual(606, resp.status_code)
        self.vl.attachment.assert_called()

    def test_attachment_slash_name_get(self):
        resp = self.client.get('/attachment/1/x')
        self.assertEqual(301, resp.status_code)
        self.vl.attachment.assert_not_called()

    def test_attachment_post(self):
        resp = self.client.post('/attachment/1')
        self.assertEqual(405, resp.status_code)
        self.vl.attachment.assert_not_called()

    def test_task_up_get(self):
        resp = self.client.get('/task/1/up')
        self.assertEqual(606, resp.status_code)
        self.vl.task_up.assert_called()

    def test_task_up_post(self):
        resp = self.client.post('/task/1/up')
        self.assertEqual(405, resp.status_code)
        self.vl.task_up.assert_not_called()

    def test_task_top_get(self):
        resp = self.client.get('/task/1/top')
        self.assertEqual(606, resp.status_code)
        self.vl.task_top.assert_called()

    def test_task_top_post(self):
        resp = self.client.post('/task/1/top')
        self.assertEqual(405, resp.status_code)
        self.vl.task_top.assert_not_called()

    def test_task_down_get(self):
        resp = self.client.get('/task/1/down')
        self.assertEqual(606, resp.status_code)
        self.vl.task_down.assert_called()

    def test_task_down_post(self):
        resp = self.client.post('/task/1/down')
        self.assertEqual(405, resp.status_code)
        self.vl.task_down.assert_not_called()

    def test_task_bottom_get(self):
        resp = self.client.get('/task/1/bottom')
        self.assertEqual(606, resp.status_code)
        self.vl.task_bottom.assert_called()

    def test_task_bottom_post(self):
        resp = self.client.post('/task/1/bottom')
        self.assertEqual(405, resp.status_code)
        self.vl.task_bottom.assert_not_called()

    def test_long_order_change_get(self):
        resp = self.client.get('/long_order_change')
        self.assertEqual(405, resp.status_code)
        self.vl.long_order_change.assert_not_called()

    def test_long_order_change_post(self):
        resp = self.client.post('/long_order_change')
        self.assertEqual(606, resp.status_code)
        self.vl.long_order_change.assert_called()

    def test_task_add_tag_get(self):
        resp = self.client.get('/task/1/add_tag')
        self.assertEqual(606, resp.status_code)
        self.vl.task_add_tag.assert_called()

    def test_task_add_tag_post(self):
        resp = self.client.post('/task/1/add_tag')
        self.assertEqual(606, resp.status_code)
        self.vl.task_add_tag.assert_called()

    def test_task_delete_tag_get(self):
        resp = self.client.get('/task/1/delete_tag')
        self.assertEqual(301, resp.status_code)
        self.vl.task_delete_tag.assert_not_called()

    def test_task_delete_tag_slash_get(self):
        resp = self.client.get('/task/1/delete_tag/')
        self.assertEqual(606, resp.status_code)
        self.vl.task_delete_tag.assert_called()

    def test_task_delete_tag_slash_id_get(self):
        resp = self.client.get('/task/1/delete_tag/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_delete_tag.assert_called()

    def test_task_delete_tag_post(self):
        resp = self.client.post('/task/1/delete_tag')
        self.assertEqual(301, resp.status_code)
        self.vl.task_delete_tag.assert_not_called()

    def test_task_authorize_user_get(self):
        resp = self.client.get('/task/1/authorize_user')
        self.assertEqual(606, resp.status_code)
        self.vl.task_authorize_user.assert_called()

    def test_task_authorize_user_post(self):
        resp = self.client.post('/task/1/authorize_user')
        self.assertEqual(606, resp.status_code)
        self.vl.task_authorize_user.assert_called()

    def test_task_pick_user_get(self):
        resp = self.client.get('/task/1/pick_user')
        self.assertEqual(606, resp.status_code)
        self.vl.task_pick_user.assert_called()

    def test_task_pick_user_post(self):
        resp = self.client.post('/task/1/pick_user')
        self.assertEqual(405, resp.status_code)
        self.vl.task_pick_user.assert_not_called()

    def test_task_authorize_user_user_get(self):
        resp = self.client.get('/task/1/authorize_user/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_authorize_user_user.assert_called()

    def test_task_authorize_user_user_post(self):
        resp = self.client.post('/task/1/authorize_user/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_authorize_user_user.assert_called()

    def test_task_deauthorize_user_get(self):
        resp = self.client.get('/task/1/deauthorize_user')
        self.assertEqual(301, resp.status_code)
        self.vl.task_deauthorize_user.assert_not_called()

    def test_task_deauthorize_user_slash_get(self):
        resp = self.client.get('/task/1/deauthorize_user/')
        self.assertEqual(606, resp.status_code)
        self.vl.task_deauthorize_user.assert_called()

    def test_task_deauthorize_user_slash_id_get(self):
        resp = self.client.get('/task/1/deauthorize_user/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_deauthorize_user.assert_called()

    def test_task_deauthorize_user_post(self):
        resp = self.client.post('/task/1/deauthorize_user')
        self.assertEqual(301, resp.status_code)
        self.vl.task_deauthorize_user.assert_not_called()

    def test_task_deauthorize_user_slash_post(self):
        resp = self.client.post('/task/1/deauthorize_user/')
        self.assertEqual(606, resp.status_code)
        self.vl.task_deauthorize_user.assert_called()

    def test_task_deauthorize_user_slash_id_post(self):
        resp = self.client.post('/task/1/deauthorize_user/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_deauthorize_user.assert_called()

    def test_login_get(self):
        resp = self.client.get('/login')
        self.assertEqual(606, resp.status_code)
        self.vl.login.assert_called()

    def test_login_post(self):
        resp = self.client.post('/login')
        self.assertEqual(606, resp.status_code)
        self.vl.login.assert_called()

    def test_logout_get(self):
        resp = self.client.get('/logout')
        self.assertEqual(606, resp.status_code)
        self.vl.logout.assert_called()

    def test_logout_post(self):
        resp = self.client.post('/logout')
        self.assertEqual(405, resp.status_code)
        self.vl.logout.assert_not_called()

    def test_users_get(self):
        resp = self.client.get('/users')
        self.assertEqual(606, resp.status_code)
        self.vl.users.assert_called()

    def test_users_post(self):
        resp = self.client.post('/users')
        self.assertEqual(606, resp.status_code)
        self.vl.users.assert_called()

    def test_users_user_get_get(self):
        resp = self.client.get('/users/1')
        self.assertEqual(606, resp.status_code)
        self.vl.users_user_get.assert_called()

    def test_users_user_get_post(self):
        resp = self.client.post('/users/1')
        self.assertEqual(405, resp.status_code)
        self.vl.users_user_get.assert_not_called()

    def test_show_hide_deleted_get(self):
        resp = self.client.get('/show_hide_deleted')
        self.assertEqual(606, resp.status_code)
        self.vl.show_hide_deleted.assert_called()

    def test_show_hide_deleted_post(self):
        resp = self.client.post('/show_hide_deleted')
        self.assertEqual(405, resp.status_code)
        self.vl.show_hide_deleted.assert_not_called()

    def test_show_hide_done_get(self):
        resp = self.client.get('/show_hide_done')
        self.assertEqual(606, resp.status_code)
        self.vl.show_hide_done.assert_called()

    def test_show_hide_done_post(self):
        resp = self.client.post('/show_hide_done')
        self.assertEqual(405, resp.status_code)
        self.vl.show_hide_done.assert_not_called()

    def test_options_get(self):
        resp = self.client.get('/options')
        self.assertEqual(606, resp.status_code)
        self.vl.options.assert_called()

    def test_options_post(self):
        resp = self.client.post('/options')
        self.assertEqual(606, resp.status_code)
        self.vl.options.assert_called()

    def test_option_delete_get(self):
        resp = self.client.get('/option/1/delete')
        self.assertEqual(606, resp.status_code)
        self.vl.option_delete.assert_called()

    def test_option_delete_post(self):
        resp = self.client.post('/option/1/delete')
        self.assertEqual(405, resp.status_code)
        self.vl.option_delete.assert_not_called()

    def test_reset_order_nums_get(self):
        resp = self.client.get('/reset_order_nums')
        self.assertEqual(606, resp.status_code)
        self.vl.reset_order_nums.assert_called()

    def test_reset_order_nums_post(self):
        resp = self.client.post('/reset_order_nums')
        self.assertEqual(405, resp.status_code)
        self.vl.reset_order_nums.assert_not_called()

    def test_export_get(self):
        resp = self.client.get('/export')
        self.assertEqual(606, resp.status_code)
        self.vl.export.assert_called()

    def test_export_post(self):
        resp = self.client.post('/export')
        self.assertEqual(606, resp.status_code)
        self.vl.export.assert_called()

    def test_import__get(self):
        resp = self.client.get('/import')
        self.assertEqual(606, resp.status_code)
        self.vl.import_.assert_called()

    def test_import__post(self):
        resp = self.client.post('/import')
        self.assertEqual(606, resp.status_code)
        self.vl.import_.assert_called()

    def test_task_crud_get(self):
        resp = self.client.get('/task_crud')
        self.assertEqual(606, resp.status_code)
        self.vl.task_crud.assert_called()

    def test_task_crud_post(self):
        resp = self.client.post('/task_crud')
        self.assertEqual(606, resp.status_code)
        self.vl.task_crud.assert_called()

    def test_tags_get(self):
        resp = self.client.get('/tags')
        self.assertEqual(301, resp.status_code)
        self.vl.tags.assert_not_called()

    def test_tags_slash_get(self):
        resp = self.client.get('/tags/')
        self.assertEqual(606, resp.status_code)
        self.vl.tags.assert_called()

    def test_tags_post(self):
        resp = self.client.post('/tags')
        self.assertEqual(405, resp.status_code)
        self.vl.tags.assert_not_called()

    def test_tags_slash_post(self):
        resp = self.client.post('/tags/')
        self.assertEqual(405, resp.status_code)
        self.vl.tags.assert_not_called()

    def test_tags_id_get_get(self):
        resp = self.client.get('/tags/1')
        self.assertEqual(606, resp.status_code)
        self.vl.tags_id_get.assert_called()

    def test_tags_id_get_post(self):
        resp = self.client.post('/tags/1')
        self.assertEqual(405, resp.status_code)
        self.vl.tags_id_get.assert_not_called()

    def test_tags_id_edit_get(self):
        resp = self.client.get('/tags/1/edit')
        self.assertEqual(606, resp.status_code)
        self.vl.tags_id_edit.assert_called()

    def test_tags_id_edit_post(self):
        resp = self.client.post('/tags/1/edit')
        self.assertEqual(606, resp.status_code)
        self.vl.tags_id_edit.assert_called()

    def test_task_id_convert_to_tag_get(self):
        resp = self.client.get('/task/1/convert_to_tag')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_convert_to_tag.assert_called()

    def test_task_id_convert_to_tag_post(self):
        resp = self.client.post('/task/1/convert_to_tag')
        self.assertEqual(405, resp.status_code)
        self.vl.task_id_convert_to_tag.assert_not_called()

    def test_search_get(self):
        resp = self.client.get('/search')
        self.assertEqual(301, resp.status_code)
        self.vl.search.assert_not_called()

    def test_search_slash_get(self):
        resp = self.client.get('/search/')
        self.assertEqual(606, resp.status_code)
        self.vl.search.assert_called()

    def test_search_slash_value_get(self):
        resp = self.client.get('/search/x')
        self.assertEqual(606, resp.status_code)
        self.vl.search.assert_called()

    def test_search_post(self):
        resp = self.client.post('/search')
        self.assertEqual(301, resp.status_code)
        self.vl.search.assert_not_called()

    def test_search_slash_post(self):
        resp = self.client.post('/search')
        self.assertEqual(301, resp.status_code)
        self.vl.search.assert_not_called()

    def test_search_slash_value_post(self):
        resp = self.client.post('/search')
        self.assertEqual(301, resp.status_code)
        self.vl.search.assert_not_called()

    def test_task_id_add_dependee_get(self):
        resp = self.client.get('/task/1/add_dependee/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_add_dependee.assert_called()

    def test_task_id_add_dependee_post(self):
        resp = self.client.post('/task/1/add_dependee/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_add_dependee.assert_called()

    def test_task_id_remove_dependee_get(self):
        resp = self.client.get('/task/1/remove_dependee/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_remove_dependee.assert_called()

    def test_task_id_remove_dependee_post(self):
        resp = self.client.post('/task/1/remove_dependee/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_remove_dependee.assert_called()

    def test_task_id_add_dependant_get(self):
        resp = self.client.get('/task/1/add_dependant/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_add_dependant.assert_called()

    def test_task_id_add_dependant_post(self):
        resp = self.client.post('/task/1/add_dependant/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_add_dependant.assert_called()

    def test_task_id_remove_dependant_get(self):
        resp = self.client.get('/task/1/remove_dependant/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_remove_dependant.assert_called()

    def test_task_id_remove_dependant_post(self):
        resp = self.client.post('/task/1/remove_dependant/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_remove_dependant.assert_called()

    def test_task_id_add_prioritize_before_get(self):
        resp = self.client.get('/task/1/add_prioritize_before/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_add_prioritize_before.assert_called()

    def test_task_id_add_prioritize_before_post(self):
        resp = self.client.post('/task/1/add_prioritize_before/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_add_prioritize_before.assert_called()

    def test_task_id_remove_prioritize_before_get(self):
        resp = self.client.get('/task/1/remove_prioritize_before/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_remove_prioritize_before.assert_called()

    def test_task_id_remove_prioritize_before_post(self):
        resp = self.client.post('/task/1/remove_prioritize_before/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_remove_prioritize_before.assert_called()

    def test_task_id_add_prioritize_after_get(self):
        resp = self.client.get('/task/1/add_prioritize_after/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_add_prioritize_after.assert_called()

    def test_task_id_add_prioritize_after_post(self):
        resp = self.client.post('/task/1/add_prioritize_after/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_add_prioritize_after.assert_called()

    def test_task_id_remove_prioritize_after_get(self):
        resp = self.client.get('/task/1/remove_prioritize_after/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_remove_prioritize_after.assert_called()

    def test_task_id_remove_prioritize_after_post(self):
        resp = self.client.post('/task/1/remove_prioritize_after/2')
        self.assertEqual(606, resp.status_code)
        self.vl.task_id_remove_prioritize_after.assert_called()

    def test_index_put(self):
        resp = self.client.put('/')
        self.assertEqual(405, resp.status_code)
        self.vl.index.assert_not_called()

    def test_hierarchy_put(self):
        resp = self.client.put('/hierarchy')
        self.assertEqual(405, resp.status_code)
        self.vl.hierarchy.assert_not_called()

    def test_deadlines_put(self):
        resp = self.client.put('/deadlines')
        self.assertEqual(405, resp.status_code)
        self.vl.deadlines.assert_not_called()

    def test_task_new_get_put(self):
        resp = self.client.put('/task/new')
        self.assertEqual(405, resp.status_code)
        self.vl.task_new_get.assert_not_called()

    def test_task_new_post_put(self):
        resp = self.client.put('/task/new')
        self.assertEqual(405, resp.status_code)
        self.vl.task_new_post.assert_not_called()

    def test_task_mark_done_put(self):
        resp = self.client.put('/task/1/mark_done')
        self.assertEqual(405, resp.status_code)
        self.vl.task_mark_done.assert_not_called()

    def test_task_mark_undone_put(self):
        resp = self.client.put('/task/1/mark_undone')
        self.assertEqual(405, resp.status_code)
        self.vl.task_mark_undone.assert_not_called()

    def test_task_delete_put(self):
        resp = self.client.put('/task/1/delete')
        self.assertEqual(405, resp.status_code)
        self.vl.task_delete.assert_not_called()

    def test_task_undelete_put(self):
        resp = self.client.put('/task/1/undelete')
        self.assertEqual(405, resp.status_code)
        self.vl.task_undelete.assert_not_called()

    def test_task_purge_put(self):
        resp = self.client.put('/task/1/purge')
        self.assertEqual(405, resp.status_code)
        self.vl.task_purge.assert_not_called()

    def test_purge_all_put(self):
        resp = self.client.put('/purge_all')
        self.assertEqual(405, resp.status_code)
        self.vl.purge_all.assert_not_called()

    def test_task_put(self):
        resp = self.client.put('/task/1')
        self.assertEqual(405, resp.status_code)
        self.vl.task.assert_not_called()

    def test_task_hierarchy_put(self):
        resp = self.client.put('/task/1/hierarchy')
        self.assertEqual(405, resp.status_code)
        self.vl.task_hierarchy.assert_not_called()

    def test_note_new_post_put(self):
        resp = self.client.put('/note/new')
        self.assertEqual(405, resp.status_code)
        self.vl.note_new_post.assert_not_called()

    def test_task_edit_put(self):
        resp = self.client.put('/task/1/edit')
        self.assertEqual(405, resp.status_code)
        self.vl.task_edit.assert_not_called()

    def test_attachment_new_put(self):
        resp = self.client.put('/attachment/new')
        self.assertEqual(405, resp.status_code)
        self.vl.attachment_new.assert_not_called()

    def test_attachment_put(self):
        resp = self.client.put('/attachment/1')
        self.assertEqual(405, resp.status_code)
        self.vl.attachment.assert_not_called()

    def test_task_up_put(self):
        resp = self.client.put('/task/1/up')
        self.assertEqual(405, resp.status_code)
        self.vl.task_up.assert_not_called()

    def test_task_top_put(self):
        resp = self.client.put('/task/1/top')
        self.assertEqual(405, resp.status_code)
        self.vl.task_top.assert_not_called()

    def test_task_down_put(self):
        resp = self.client.put('/task/1/down')
        self.assertEqual(405, resp.status_code)
        self.vl.task_down.assert_not_called()

    def test_task_bottom_put(self):
        resp = self.client.put('/task/1/bottom')
        self.assertEqual(405, resp.status_code)
        self.vl.task_bottom.assert_not_called()

    def test_long_order_change_put(self):
        resp = self.client.put('/long_order_change')
        self.assertEqual(405, resp.status_code)
        self.vl.long_order_change.assert_not_called()

    def test_task_add_tag_put(self):
        resp = self.client.put('/task/1/add_tag')
        self.assertEqual(405, resp.status_code)
        self.vl.task_add_tag.assert_not_called()

    def test_task_delete_tag_put(self):
        resp = self.client.put('/task/1/delete_tag')
        self.assertEqual(405, resp.status_code)
        self.vl.task_delete_tag.assert_not_called()

    def test_task_authorize_user_put(self):
        resp = self.client.put('/task/1/authorize_user')
        self.assertEqual(405, resp.status_code)
        self.vl.task_authorize_user.assert_not_called()

    def test_task_pick_user_put(self):
        resp = self.client.put('/task/1/pick_user')
        self.assertEqual(405, resp.status_code)
        self.vl.task_pick_user.assert_not_called()

    def test_task_authorize_user_user_put(self):
        resp = self.client.put('/task/1/authorize_user/2')
        self.assertEqual(405, resp.status_code)
        self.vl.task_authorize_user_user.assert_not_called()

    def test_task_deauthorize_user_put(self):
        resp = self.client.put('/task/1/deauthorize_user/2')
        self.assertEqual(405, resp.status_code)
        self.vl.task_deauthorize_user.assert_not_called()

    def test_login_put(self):
        resp = self.client.put('/login')
        self.assertEqual(405, resp.status_code)
        self.vl.login.assert_not_called()

    def test_logout_put(self):
        resp = self.client.put('/logout')
        self.assertEqual(405, resp.status_code)
        self.vl.logout.assert_not_called()

    def test_users_put(self):
        resp = self.client.put('/users')
        self.assertEqual(405, resp.status_code)
        self.vl.users.assert_not_called()

    def test_users_user_get_put(self):
        resp = self.client.put('/users/1')
        self.assertEqual(405, resp.status_code)
        self.vl.users_user_get.assert_not_called()

    def test_show_hide_deleted_put(self):
        resp = self.client.put('/show_hide_deleted')
        self.assertEqual(405, resp.status_code)
        self.vl.show_hide_deleted.assert_not_called()

    def test_show_hide_done_put(self):
        resp = self.client.put('/show_hide_done')
        self.assertEqual(405, resp.status_code)
        self.vl.show_hide_done.assert_not_called()

    def test_options_put(self):
        resp = self.client.put('/options')
        self.assertEqual(405, resp.status_code)
        self.vl.options.assert_not_called()

    def test_option_delete_put(self):
        resp = self.client.put('/option/1/delete')
        self.assertEqual(405, resp.status_code)
        self.vl.option_delete.assert_not_called()

    def test_reset_order_nums_put(self):
        resp = self.client.put('/reset_order_nums')
        self.assertEqual(405, resp.status_code)
        self.vl.reset_order_nums.assert_not_called()

    def test_export_put(self):
        resp = self.client.put('/export')
        self.assertEqual(405, resp.status_code)
        self.vl.export.assert_not_called()

    def test_import__put(self):
        resp = self.client.put('/import')
        self.assertEqual(405, resp.status_code)
        self.vl.import_.assert_not_called()

    def test_task_crud_put(self):
        resp = self.client.put('/task_crud')
        self.assertEqual(405, resp.status_code)
        self.vl.task_crud.assert_not_called()

    def test_tags_put(self):
        resp = self.client.put('/tags')
        self.assertEqual(405, resp.status_code)
        self.vl.tags.assert_not_called()

    def test_tags_slash_put(self):
        resp = self.client.put('/tags/')
        self.assertEqual(405, resp.status_code)
        self.vl.tags.assert_not_called()

    def test_tags_id_get_put(self):
        resp = self.client.put('/tags/1')
        self.assertEqual(405, resp.status_code)
        self.vl.tags_id_get.assert_not_called()

    def test_tags_id_edit_put(self):
        resp = self.client.put('/tags/1/edit')
        self.assertEqual(405, resp.status_code)
        self.vl.tags_id_edit.assert_not_called()

    def test_task_id_convert_to_tag_put(self):
        resp = self.client.put('/task/1/convert_to_tag')
        self.assertEqual(405, resp.status_code)
        self.vl.task_id_convert_to_tag.assert_not_called()

    def test_search_put(self):
        resp = self.client.put('/search')
        self.assertEqual(405, resp.status_code)
        self.vl.search.assert_not_called()

    def test_task_id_add_dependee_put(self):
        resp = self.client.put('/task/1/add_dependee/2')
        self.assertEqual(405, resp.status_code)
        self.vl.task_id_add_dependee.assert_not_called()

    def test_task_id_remove_dependee_put(self):
        resp = self.client.put('/task/1/remove_dependee/2')
        self.assertEqual(405, resp.status_code)
        self.vl.task_id_remove_dependee.assert_not_called()

    def test_task_id_add_dependant_put(self):
        resp = self.client.put('/task/1/add_dependant/2')
        self.assertEqual(405, resp.status_code)
        self.vl.task_id_add_dependant.assert_not_called()

    def test_task_id_remove_dependant_put(self):
        resp = self.client.put('/task/1/remove_dependant/2')
        self.assertEqual(405, resp.status_code)
        self.vl.task_id_remove_dependant.assert_not_called()

    def test_task_id_add_prioritize_before_put(self):
        resp = self.client.put('/task/1/add_prioritize_before/2')
        self.assertEqual(405, resp.status_code)
        self.vl.task_id_add_prioritize_before.assert_not_called()

    def test_task_id_remove_prioritize_before_put(self):
        resp = self.client.put('/task/1/remove_prioritize_before/2')
        self.assertEqual(405, resp.status_code)
        self.vl.task_id_remove_prioritize_before.assert_not_called()

    def test_task_id_add_prioritize_after_put(self):
        resp = self.client.put('/task/1/add_prioritize_after/2')
        self.assertEqual(405, resp.status_code)
        self.vl.task_id_add_prioritize_after.assert_not_called()

    def test_task_id_remove_prioritize_after_put(self):
        resp = self.client.put('/task/1/remove_prioritize_after/2')
        self.assertEqual(405, resp.status_code)
        self.vl.task_id_remove_prioritize_after.assert_not_called()
