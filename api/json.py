from flask import json, url_for


class JsonApi(object):
    def __init__(self, jr, ll):
        self.jr = jr
        self.ll = ll

    def index(self):
        return {
                   'tasks': url_for('api_list_tasks')
               }, 200

    def list_tasks(self, current_user):
        tasks = self.ll.get_tasks(current_user, include_done=False,
                                  include_deleted=False, root=None)
        return self.jr.render_list_tasks(tasks)
