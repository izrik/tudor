
import itertools

from flask import make_response, render_template


class ViewLayer(object):
    def __init__(self, ll):
        self.ll = ll

    def index(self, request, current_user):
        show_deleted = request.cookies.get('show_deleted')
        show_done = request.cookies.get('show_done')

        data = self.ll.get_index_data(show_deleted, show_done, current_user)

        resp = make_response(
            render_template('index.t.html',
                            show_deleted=data['show_deleted'],
                            show_done=data['show_done'],
                            cycle=itertools.cycle,
                            user=current_user,
                            tasks=data['tasks'],
                            tags=data['all_tags'],
                            pager=data['pager'],
                            pager_link_page='index',
                            pager_link_args={}))
        return resp
