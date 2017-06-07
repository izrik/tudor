
import itertools

import flask
from flask import make_response, render_template, url_for, redirect, flash
from flask_login import login_user, logout_user

from conversions import int_from_str, money_from_str, bool_from_str


class ViewLayer(object):
    def __init__(self, ll, db, app, upload_folder):
        self.ll = ll
        self.db = db
        self.app = app
        self.upload_folder = upload_folder

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

    def task_mark_done(self, request, current_user, task_id):
        task = self.ll.task_set_done(task_id, current_user)
        self.db.session.add(task)
        self.db.session.commit()
        return redirect(request.args.get('next') or url_for('index'))

    def task_mark_undone(self, request, current_user, task_id):
        task = self.ll.task_unset_done(task_id, current_user)
        self.db.session.add(task)
        self.db.session.commit()
        return redirect(request.args.get('next') or url_for('index'))

    def task_delete(self, request, current_user, task_id):
        task = self.ll.task_set_deleted(task_id, current_user)
        self.db.session.add(task)
        self.db.session.commit()
        return redirect(request.args.get('next') or url_for('index'))

    def task_undelete(self, request, current_user, task_id):
        task = self.ll.task_unset_deleted(task_id, current_user)
        self.db.session.add(task)
        self.db.session.commit()
        return redirect(request.args.get('next') or url_for('index'))

    def task_purge(self, request, current_user, task_id):
        task = self.app.Task.query.filter_by(id=task_id,
                                             is_deleted=True).first()
        if not task:
            return 404
        self.db.session.delete(task)
        self.db.session.commit()
        return redirect(request.args.get('next') or url_for('index'))

    def purge_all(self, request, current_user):
        are_you_sure = request.args.get('are_you_sure')
        if are_you_sure:
            deleted_tasks = self.app.Task.query.filter_by(is_deleted=True)
            for task in deleted_tasks:
                self.db.session.delete(task)
            self.db.session.commit()
            return redirect(request.args.get('next') or url_for('index'))
        return render_template('purge.t.html')

    def task(self, request, current_user, task_id):
        show_deleted = request.cookies.get('show_deleted')
        show_done = request.cookies.get('show_done')
        data = self.ll.get_task_data(task_id, current_user,
                                     include_deleted=show_deleted,
                                     include_done=show_done)

        return render_template('task.t.html', task=data['task'],
                               descendants=data['descendants'],
                               cycle=itertools.cycle,
                               show_deleted=show_deleted, show_done=show_done,
                               pager=data['pager'],
                               pager_link_page='view_task',
                               pager_link_args={'id': task_id})

    def task_hierarchy(self, request, current_user, task_id):
        show_deleted = request.cookies.get('show_deleted')
        show_done = request.cookies.get('show_done')
        data = self.ll.get_task_hierarchy_data(task_id, current_user,
                                               include_deleted=show_deleted,
                                               include_done=show_done)

        return render_template('task_hierarchy.t.html', task=data['task'],
                               descendants=data['descendants'],
                               cycle=itertools.cycle,
                               show_deleted=show_deleted, show_done=show_done)

    def note_new_post(self, request, current_user):
        if 'task_id' not in request.form:
            return ('No task_id specified', 400)
        task_id = request.form['task_id']
        content = request.form['content']

        note = self.ll.create_new_note(task_id, content, current_user)

        self.db.session.add(note)
        self.db.session.commit()

        return redirect(url_for('view_task', id=task_id))

    def task_edit(self, request, current_user, task_id):

        def render_get_response():
            data = self.ll.get_edit_task_data(task_id, current_user)
            return render_template("edit_task.t.html", task=data['task'],
                                   tag_list=data['tag_list'])

        if request.method == 'GET':
            return render_get_response()

        if 'summary' not in request.form or 'description' not in request.form:
            return render_get_response()

        summary = request.form['summary']
        description = request.form['description']
        deadline = request.form['deadline']

        is_done = ('is_done' in request.form and
                   not not request.form['is_done'])
        is_deleted = ('is_deleted' in request.form and
                      not not request.form['is_deleted'])

        order_num = None
        if 'order_num' in request.form:
            order_num = request.form['order_num']

        parent_id = None
        if 'parent_id' in request.form:
            parent_id = request.form['parent_id']

        duration = int_from_str(request.form['expected_duration_minutes'])

        expected_cost = money_from_str(request.form['expected_cost'])

        task = self.ll.set_task(task_id, current_user, summary, description,
                                deadline, is_done, is_deleted, order_num,
                                duration, expected_cost, parent_id)

        self.db.session.add(task)
        self.db.session.commit()

        return redirect(url_for('view_task', id=task.id))

    def attachment_new(self, request, current_user):
        if 'task_id' not in request.form:
            return ('No task_id specified', 400)
        task_id = request.form['task_id']

        f = request.files['filename']
        if f is None or not f or not self.ll.allowed_file(f.filename):
            return 'Invalid file', 400

        if 'description' in request.form:
            description = request.form['description']
        else:
            description = ''

        att = self.ll.create_new_attachment(task_id, f, description,
                                            current_user)

        self.db.session.add(att)
        self.db.session.commit()

        return redirect(url_for('view_task', id=task_id))

    def attachment(self, request, current_user, attachment_id, name):
        att = self.app.Attachment.query.filter_by(id=attachment_id).first()
        if att is None:
            return (('No attachment found for the id "%s"' % attachment_id),
                    404)

        return flask.send_from_directory(self.upload_folder, att.path)

    def task_up(self, request, current_user, task_id):
        show_deleted = request.cookies.get('show_deleted')
        self.ll.do_move_task_up(task_id, show_deleted, current_user)
        self.db.session.commit()

        return redirect(request.args.get('next') or url_for('index'))

    def task_top(self, request, current_user, task_id):
        self.ll.do_move_task_to_top(task_id, current_user)
        self.db.session.commit()

        return redirect(request.args.get('next') or url_for('index'))

    def task_down(self, request, current_user, task_id):
        show_deleted = request.cookies.get('show_deleted')
        self.ll.do_move_task_down(task_id, show_deleted, current_user)
        self.db.session.commit()

        return redirect(request.args.get('next') or url_for('index'))

    def task_bottom(self, request, current_user, task_id):
        self.ll.do_move_task_to_bottom(task_id, current_user)
        self.db.session.commit()

        return redirect(request.args.get('next') or url_for('index'))

    def long_order_change(self, request, current_user):
        task_to_move_id = self.get_form_or_arg(request,
                                               'long_order_task_to_move')
        if task_to_move_id is None:
            redirect(request.args.get('next') or url_for('index'))

        target_id = self.get_form_or_arg(request, 'long_order_target')
        if target_id is None:
            redirect(request.args.get('next') or url_for('index'))

        self.ll.do_long_order_change(task_to_move_id, target_id, current_user)

        self.db.session.commit()

        return redirect(request.args.get('next') or url_for('index'))

    def task_add_tag(self, request, current_user, task_id):

        value = self.get_form_or_arg(request, 'value')
        if value is None or value == '':
            return (redirect(request.args.get('next') or
                             url_for('view_task', id=task_id)))

        self.ll.do_add_tag_to_task(task_id, value, current_user)
        self.db.session.commit()

        return (redirect(request.args.get('next') or
                         url_for('view_task', id=task_id)))

    def task_delete_tag(self, request, current_user, task_id, tag_id):

        if tag_id is None:
            tag_id = self.get_form_or_arg(request, 'tag_id')

        self.ll.do_delete_tag_from_task(task_id, tag_id, current_user)
        self.db.session.commit()

        return (redirect(request.args.get('next') or
                         url_for('view_task', id=task_id)))

    def task_authorize_user(self, request, current_user, task_id):

        email = self.get_form_or_arg(request, 'email')
        if email is None or email == '':
            return (redirect(request.args.get('next') or
                             url_for('view_task', id=task_id)))

        self.ll.do_authorize_user_for_task_by_email(task_id, email,
                                                    current_user)
        self.db.session.commit()

        return (redirect(request.args.get('next') or
                         url_for('view_task', id=task_id)))

    def task_pick_user(self, request, current_user, task_id):
        task = self.ll.get_task(task_id, current_user)
        users = self.ll.get_users()
        return render_template('pick_user.t.html', task=task, users=users,
                               cycle=itertools.cycle)

    def task_authorize_user_user(self, request, current_user, task_id,
                                 user_id):
        if user_id is None or user_id == '':
            return (redirect(request.args.get('next') or
                             url_for('view_task', id=task_id)))

        self.ll.do_authorize_user_for_task_by_id(task_id, user_id,
                                                 current_user)
        self.db.session.commit()

        return (redirect(request.args.get('next') or
                         url_for('view_task', id=task_id)))

    def task_deauthorize_user(self, request, current_user, task_id, user_id):
        if user_id is None:
            user_id = self.get_form_or_arg(request, 'user_id')

        self.ll.do_deauthorize_user_for_task(task_id, user_id, current_user)
        self.db.session.commit()

        return (redirect(request.args.get('next') or
                         url_for('view_task', id=task_id)))

    def login(self, request, current_user):
        if request.method == 'GET':
            return render_template('login.t.html')
        email = request.form['email']
        password = request.form['password']
        user = self.app.User.query.filter_by(email=email).first()

        if (user is None or
                not self.app.bcrypt.check_password_hash(user.hashed_password,
                                                        password)):
            flash('Username or Password is invalid', 'error')
            return redirect(url_for('login'))

        login_user(user)
        flash('Logged in successfully')
        return redirect(request.args.get('next') or url_for('index'))

    def logout(self, request, current_user):
        logout_user()
        return redirect(url_for('index'))

    def users(self, request, current_user):
        if request.method == 'GET':
            users = self.ll.get_users()
            return render_template('list_users.t.html', users=users,
                                   cycle=itertools.cycle)

        email = request.form['email']
        is_admin = False
        if 'is_admin' in request.form:
            is_admin = bool_from_str(request.form['is_admin'])

        self.ll.do_add_new_user(email, is_admin)
        self.db.session.commit()

        return redirect(url_for('list_users'))

    def users_user_get(self, request, current_user, user_id):
        user = self.ll.do_get_user_data(user_id, current_user)
        return render_template('view_user.t.html', user=user)

    def show_hide_deleted(self, request, current_user):
        show_deleted = request.args.get('show_deleted')
        resp = make_response(
            redirect(request.args.get('next') or url_for('index')))
        if show_deleted and show_deleted != '0':
            resp.set_cookie('show_deleted', '1')
        else:
            resp.set_cookie('show_deleted', '')
        return resp

    def show_hide_done(self, request, current_user):
        show_done = request.args.get('show_done')
        resp = make_response(
            redirect(request.args.get('next') or url_for('index')))
        if show_done and show_done != '0':
            resp.set_cookie('show_done', '1')
        else:
            resp.set_cookie('show_done', '')
        return resp
