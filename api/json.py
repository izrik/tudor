from flask import json, url_for, make_response


class JsonApi(object):
    def __init__(self, jr, ll, db):
        self.jr = jr
        self.ll = ll
        self.db = db

    def index(self):
        return {
                   'tasks': url_for('api_list_tasks')
               }, 200

    def list_tasks(self, current_user):
        tasks = self.ll.get_tasks(current_user, include_done=False,
                                  include_deleted=False, root=None)
        return self.jr.render_list_tasks(tasks)

    def create_task(self, current_user, task_data):
        summary = task_data.get('summary')
        description = task_data.get('description')
        is_done = task_data.get('is_done')
        is_deleted = task_data.get('is_deleted')
        order_num = task_data.get('order_num')
        deadline = task_data.get('deadline')
        expected_duration_minutes = task_data.get('expected_duration_minutes')
        expected_cost = task_data.get('expected_cost')

        task, tul = self.ll.create_new_task(summary, None, current_user)
        task.description = description
        task.is_done = is_done
        task.is_deleted = is_deleted
        task.order_num = order_num
        task.deadline = deadline
        task.expected_duration_minutes = expected_duration_minutes
        task.expected_cost = expected_cost

        self.db.session.add(task)
        # TODO: extra commit in view
        self.db.session.commit()
        # TODO: modifying return value from logic layer in view
        tul.task_id = task.id
        self.db.session.add(tul)
        self.db.session.commit()

        # parent ?
        # tags ?

        # users ?
        # children ?

        location = url_for('api_get_task', task_id=task.id)

        data = {
            'task': task,
            'descendants': task.children,
        }
        content, code = self.jr.render_task(data)
        resp = make_response(content, 201)
        resp.headers['Location'] = location
        return resp


    def get_task(self, current_user, task_id):
        data = self.ll.get_task_data(task_id, current_user,
                                     include_deleted=True, include_done=True,
                                     show_hierarchy=True)
        return self.jr.render_task(data)

    def get_deadlines(self, current_user):
        data = self.ll.get_deadlines_data(current_user)
        return self.jr.render_deadlines(data)
