
from flask import json, url_for, make_response


class JsonApi(object):
    def __init__(self, jr, ll, db):
        self.jr = jr
        self.ll = ll
        self.db = db

    def index(self):
        return {
                   'tasks': url_for('api_list_tasks'),
                   'tags': url_for('api_list_tags'),
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

        task, tul = self.ll.create_new_task(
            current_user, summary, description=description, is_done=is_done,
            is_deleted=is_deleted, deadline=deadline,
            expected_duration_minutes=expected_duration_minutes,
            expected_cost=expected_cost)
        if order_num is not None:
            task.order_num = order_num

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

    def update_task(self, current_user, task_id, task_data):
        task = self.ll.get_task_data(id=task_id, current_user=current_user,
                                     show_hierarchy=False)

        summary = task_data.get('summary', self.ll.DO_NOT_CHANGE)
        description = task_data.get('description', self.ll.DO_NOT_CHANGE)
        is_done = task_data.get('is_done', self.ll.DO_NOT_CHANGE)
        is_deleted = task_data.get('is_deleted', self.ll.DO_NOT_CHANGE)
        order_num = task_data.get('order_num', self.ll.DO_NOT_CHANGE)
        deadline = task_data.get('deadline', self.ll.DO_NOT_CHANGE)
        expected_duration_minutes = task_data.get('expected_duration_minutes',
                                                  self.ll.DO_NOT_CHANGE)
        expected_cost = task_data.get('expected_cost', self.ll.DO_NOT_CHANGE)

        task = self.ll.set_task(task_id, current_user, summary=summary,
                                description=description, deadline=deadline,
                                is_done=is_done, is_deleted=is_deleted,
                                order_num=order_num,
                                duration=expected_duration_minutes,
                                expected_cost=expected_cost)

        self.db.session.add(task)
        # TODO: extra commit in view
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
        resp = make_response(content, 200)
        resp.headers['Location'] = location
        return resp

    def purge_task(self, current_user, task_id):
        return self.ll.purge_task(current_user, task_id)

    def list_tags(self, current_user):
        tags = self.ll.get_tags()
        return self.jr.render_list_tags(tags)

    def get_tag(self, current_user, tag_id):
        data = self.ll.get_tag_data(tag_id, current_user)
        return self.jr.render_tag(data)
