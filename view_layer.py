
import itertools

from flask import make_response, render_template, url_for, redirect


class ViewLayer(object):
    def __init__(self, ll, db):
        self.ll = ll
        self.db = db

    def get_form_or_arg(self, request, name):
        if name in request.form:
            return request.form[name]
        return request.args.get(name)

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

    def hierarchy(self, request, current_user):
        show_deleted = request.cookies.get('show_deleted')
        show_done = request.cookies.get('show_done')

        data = self.ll.get_index_hierarchy_data(show_deleted, show_done,
                                                current_user)

        resp = make_response(
            render_template('hierarchy.t.html',
                            show_deleted=data['show_deleted'],
                            show_done=data['show_done'],
                            cycle=itertools.cycle,
                            user=current_user,
                            tasks_h=data['tasks_h'],
                            tags=data['all_tags']))
        return resp

    def deadlines(self, request, current_user):
        data = self.ll.get_deadlines_data(current_user)
        return make_response(
            render_template(
                'deadlines.t.html',
                cycle=itertools.cycle,
                deadline_tasks=data['deadline_tasks']))

    def task_new_get(self, request, current_user):
        summary = self.get_form_or_arg(request, 'summary')
        description = self.get_form_or_arg(request, 'description')
        deadline = self.get_form_or_arg(request, 'deadline')
        is_done = self.get_form_or_arg(request, 'is_done')
        is_deleted = self.get_form_or_arg(request, 'is_deleted')
        order_num = self.get_form_or_arg(request, 'order_num')
        expected_duration_minutes = self.get_form_or_arg(
            request, 'expected_duration_minutes')
        expected_cost = self.get_form_or_arg(request, 'expected_cost')
        parent_id = self.get_form_or_arg(request, 'parent_id')
        tags = self.get_form_or_arg(request, 'tags')

        prev_url = self.get_form_or_arg(request, 'prev_url')

        return render_template(
            'new_task.t.html', prev_url=prev_url, summary=summary,
            description=description, deadline=deadline, is_done=is_done,
            is_deleted=is_deleted, order_num=order_num,
            expected_duration_minutes=expected_duration_minutes,
            expected_cost=expected_cost, parent_id=parent_id, tags=tags)

    def task_new_post(self, request, current_user):
        summary = self.get_form_or_arg(request, 'summary')
        description = self.get_form_or_arg(request, 'description')
        deadline = self.get_form_or_arg(request, 'deadline') or None
        is_done = self.get_form_or_arg(request, 'is_done') or None
        is_deleted = self.get_form_or_arg(request, 'is_deleted') or None
        order_type = self.get_form_or_arg(request, 'order_type') or 'bottom'
        expected_duration_minutes = self.get_form_or_arg(
            request, 'expected_duration_minutes') or None
        expected_cost = self.get_form_or_arg(request, 'expected_cost') or None
        parent_id = self.get_form_or_arg(request, 'parent_id') or None

        tags = self.get_form_or_arg(request, 'tags')
        if tags:
            tags = [s.strip() for s in tags.split(',')]

        if order_type == 'top':
            order_num = self.ll.get_highest_order_num()
            if order_num is not None:
                order_num += 2
            else:
                order_num = 0
        elif order_type == 'order_num':
            order_num = self.get_form_or_arg(request, 'order_num') or None
        else:  # bottom
            order_num = self.ll.get_lowest_order_num()
            if order_num is not None:
                order_num -= 2
            else:
                order_num = 0

        task = self.ll.create_new_task(
            summary=summary, description=description, is_done=is_done,
            is_deleted=is_deleted, deadline=deadline, order_num=order_num,
            expected_duration_minutes=expected_duration_minutes,
            expected_cost=expected_cost, parent_id=parent_id,
            current_user=current_user)

        for tag_name in tags:
            tag = self.ll.get_or_create_tag(tag_name)
            task.tags.append(tag)
            self.db.session.add(tag)

        self.db.session.add(task)
        self.db.session.commit()

        next_url = self.get_form_or_arg(request, 'next_url')
        if not next_url:
            next_url = url_for('view_task', id=task.id)

        return redirect(next_url)
