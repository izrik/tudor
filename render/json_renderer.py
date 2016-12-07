
from flask import json, url_for

from conversions import str_from_datetime


class JsonRenderer(object):
    def render_index(self, data):
        tasks = [
            {'summary': t.summary, 'href': url_for('view_task', id=t.id)}
            for t in data['tasks_h'] if t is not None]

        tags = [
            {'name': tag.value, 'href': url_for('view_tag', id=tag.id)}
            for tag in data['all_tags']]

        data = {
            'tasks': tasks,
            'tags': tags
        }

        return json.dumps(data), 200

    def render_deadlines(self, data):
        deadline_tasks = [{'deadline': task.deadline,
                           'summary': task.summary,
                           'href': url_for('api_get_task', task_id=task.id)} for
                          task in data['deadline_tasks']]
        return json.dumps(deadline_tasks), 200

    def render_list_tasks(self, tasks):
        data = [
            {'href': url_for('api_get_task', task_id=task.id),
             'summary': task.summary}
            for task in tasks if task]
        return json.dumps(data), 200

    def render_task(self, data):
        task = data['task']
        data = {
            'id': task.id,
            'summary': task.summary,
            'description': task.description,
            'is_done': task.is_done,
            'is_deleted': task.is_deleted,
            'order_num': task.order_num,
            'deadline': str_from_datetime(task.deadline),
            'parent': None,
            'expected_duration_minutes':
                task.expected_duration_minutes,
            'expected_cost': task.get_expected_cost_for_export(),
            'tags': [url_for('api_get_tag', tag_id=ttl.tag_id)
                     for ttl in task.tags],
            'users': [url_for('view_user', user_id=tul.user_id)
                      for tul in task.users],
            'children': [url_for('api_get_task', task_id=child.id) for child in
                         task.children]}
        if task.parent_id:
            data['parent'] = url_for('api_get_task', task_id=task.parent_id)
        return json.dumps(data), 200

    def render_list_users(self, users):
        data = [{'href': url_for('view_user', user_id=user.id),
                 'id': user.id,
                 'email': user.email}
                for user in users]
        return json.dumps(data), 200

    def render_user(self, user):
        data = {'id': user.id,
                'email': user.email,
                'is_admin': user.is_admin}
        return json.dumps(data), 200

    def render_options(self, data):
        data = [option.to_dict() for option in data]
        return json.dumps(data), 200

    def render_list_tags(self, tags):
        data = [{'href': url_for('view_tag', id=tag.id),
                 'value': tag.value}
                for tag in tags]
        return json.dumps(data), 200

    def render_tag(self, data):
        tag = data['tag'].to_dict()
        tasks = data['tasks']
        tag['tasks'] = [url_for('api_get_task', task_id=task.id) for task in tasks]
        return json.dumps(tag), 200
