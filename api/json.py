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

    def get_task(self, current_user, task_id):
        data = self.ll.get_task_data(task_id, current_user,
                                     include_deleted=True, include_done=True,
                                     show_hierarchy=True)
        return self.jr.render_task(data)

    def get_deadlines(self, current_user):
        data = self.ll.get_deadlines_data(current_user)
        return self.jr.render_deadlines(data)
