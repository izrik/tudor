
import itertools
import re

from flask import jsonify, json
from werkzeug.exceptions import NotFound, BadRequest

from conversions import int_from_str, money_from_str, bool_from_str

from models.task_user_ops import TaskUserOps


class DefaultRenderer(object):
    def render_template(self, template_name, **kwargs):
        from flask import render_template
        return render_template(template_name, **kwargs)

    def make_response(self, *args):
        from flask import make_response
        return make_response(*args)

    def redirect(self, *args, **kwargs):
        from flask import redirect
        return redirect(*args, **kwargs)

    def url_for(self, *args, **kwargs):
        from flask import url_for
        return url_for(*args, **kwargs)

    def send_from_directory(self, *args, **kwargs):
        from flask import send_from_directory
        return send_from_directory(*args, **kwargs)

    def flash(self, *args, **kwargs):
        from flask import flash
        return flash(*args, **kwargs)


class DefaultLoginSource(object):
    def __init__(self, bcrypt):
        self.bcrypt = bcrypt

    def login_user(self, *args, **kwargs):
        from flask_login import login_user
        return login_user(*args, **kwargs)

    def logout_user(self, *args, **kwargs):
        from flask_login import logout_user
        return logout_user(*args, **kwargs)

    def check_password_hash(self, *args, **kwargs):
        return self.bcrypt.check_password_hash(*args, **kwargs)


class ViewLayer(object):
    def __init__(self, ll, app, pl, renderer=None, login_src=None):
        self.ll = ll
        self.app = app
        self.pl = pl
        if renderer is None:
            renderer = DefaultRenderer()
        self.renderer = renderer
        if login_src is None:
            bcrypt = None
            if app:
                bcrypt = app.bcrypt
            login_src = DefaultLoginSource(bcrypt)
        self.login_src = login_src

    def render_template(self, template_name, **kwargs):
        return self.renderer.render_template(template_name, **kwargs)

    def make_response(self, *args):
        return self.renderer.make_response(*args)

    def redirect(self, *args, **kwargs):
        return self.renderer.redirect(*args, **kwargs)

    def url_for(self, *args, **kwargs):
        return self.renderer.url_for(*args, **kwargs)

    def send_from_directory(self, *args, **kwargs):
        return self.renderer.send_from_directory(*args, **kwargs)

    def flash(self, *args, **kwargs):
        return self.renderer.flash(*args, **kwargs)

    def login_user(self, *args, **kwargs):
        return self.login_src.login_user(*args, **kwargs)

    def logout_user(self, *args, **kwargs):
        return self.login_src.logout_user(*args, **kwargs)

    def check_password_hash(self, *args, **kwargs):
        return self.login_src.check_password_hash(*args, **kwargs)

    def get_form_or_arg(self, request, name):
        if name in request.form:
            return request.form[name]
        return request.args.get(name)

    def index(self, request, current_user):
        show_deleted = request.cookies.get('show_deleted')
        show_done = request.cookies.get('show_done')
        page_num = None
        try:
            page_num = int(self.get_form_or_arg(request, 'page'))
        except:
            pass
        tasks_per_page = None
        try:
            tasks_per_page = int(self.get_form_or_arg(request, 'per_page'))
        except:
            pass

        data = self.ll.get_index_data(show_deleted, show_done, current_user,
                                      page_num=page_num,
                                      tasks_per_page=tasks_per_page)

        resp = self.make_response(
            self.render_template('index.t.html',
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

        resp = self.make_response(
            self.render_template('hierarchy.t.html',
                                 show_deleted=data['show_deleted'],
                                 show_done=data['show_done'],
                                 cycle=itertools.cycle,
                                 user=current_user,
                                 tasks_h=data['tasks_h'],
                                 tags=data['all_tags']))
        return resp

    def deadlines(self, request, current_user):
        data = self.ll.get_deadlines_data(current_user)
        return self.make_response(
            self.render_template(
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

        return self.render_template(
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
        is_public = self.get_form_or_arg(request, 'is_public') or None

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
            is_public=is_public, current_user=current_user)

        if tags:
            for tag_name in tags:
                self.ll.do_add_tag_to_task(task, tag_name, current_user)

        next_url = self.get_form_or_arg(request, 'next_url')
        if not next_url:
            next_url = self.url_for('view_task', id=task.id)

        return self.redirect(next_url)

    def task_mark_done(self, request, current_user, task_id):
        self.ll.task_set_done(task_id, current_user)
        return self.redirect(request.args.get('next') or self.url_for('index'))

    def task_mark_undone(self, request, current_user, task_id):
        self.ll.task_unset_done(task_id, current_user)
        return self.redirect(request.args.get('next') or self.url_for('index'))

    def task_delete(self, request, current_user, task_id):
        self.ll.task_set_deleted(task_id, current_user)
        return self.redirect(request.args.get('next') or self.url_for('index'))

    def task_undelete(self, request, current_user, task_id):
        self.ll.task_unset_deleted(task_id, current_user)
        return self.redirect(request.args.get('next') or self.url_for('index'))

    def task_purge(self, request, current_user, task_id):
        task = self.pl.get_task(task_id)
        if not task:
            raise NotFound("No task found for the id '{}'".format(task_id))
        if not task.is_deleted:
            raise BadRequest(
                "Indicated task (id {}) has not been deleted.".format(task_id))
        self.ll.purge_task(task, current_user)
        return self.redirect(request.args.get('next') or self.url_for('index'))

    def purge_all(self, request, current_user):
        are_you_sure = request.args.get('are_you_sure')
        if are_you_sure:
            self.ll.purge_all_deleted_tasks(current_user)
            return self.redirect(request.args.get('next') or
                                 self.url_for('index'))
        return self.render_template('purge.t.html')

    def task(self, request, current_user, task_id):
        show_deleted = request.cookies.get('show_deleted')
        show_done = request.cookies.get('show_done')
        try:
            page_num = int(request.args.get('page', 1))
        except Exception:
            page_num = 1
        try:
            tasks_per_page = int(request.args.get('per_page', 20))
        except Exception:
            tasks_per_page = 20
        data = self.ll.get_task_data(task_id, current_user,
                                     include_deleted=show_deleted,
                                     include_done=show_done,
                                     page_num=page_num,
                                     tasks_per_page=tasks_per_page)

        return self.render_template('task.t.html',
                                    task=data['task'],
                                    descendants=data['descendants'],
                                    cycle=itertools.cycle,
                                    show_deleted=show_deleted,
                                    show_done=show_done,
                                    pager=data['pager'],
                                    pager_link_page='view_task',
                                    pager_link_args={'id': task_id},
                                    current_user=current_user,
                                    ops=TaskUserOps,
                                    show_hierarchy=False)

    def task_hierarchy(self, request, current_user, task_id):
        show_deleted = request.cookies.get('show_deleted')
        show_done = request.cookies.get('show_done')
        data = self.ll.get_task_hierarchy_data(task_id, current_user,
                                               include_deleted=show_deleted,
                                               include_done=show_done)

        return self.render_template('task.t.html',
                                    task=data['task'],
                                    descendants=data['descendants'],
                                    cycle=itertools.cycle,
                                    show_deleted=show_deleted,
                                    show_done=show_done,
                                    ops=TaskUserOps,
                                    show_hierarchy=True)

    def note_new_post(self, request, current_user):
        if 'task_id' not in request.form:
            return ('No task_id specified', 400)
        task_id = request.form['task_id']
        content = request.form['content']

        self.ll.create_new_note(task_id, content, current_user)

        return self.redirect(self.url_for('view_task', id=task_id))

    def task_edit(self, request, current_user, task_id):

        def render_get_response():
            data = self.ll.get_edit_task_data(task_id, current_user)
            return self.render_template("edit_task.t.html", task=data['task'],
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

        is_public = ('is_public' in request.form and
                     not not request.form['is_public'])

        duration = int_from_str(request.form['expected_duration_minutes'])

        expected_cost = money_from_str(request.form['expected_cost'])

        task = self.ll.set_task(task_id, current_user, summary, description,
                                deadline, is_done, is_deleted, order_num,
                                duration, expected_cost, parent_id, is_public)

        return self.redirect(self.url_for('view_task', id=task.id))

    def attachment_new(self, request, current_user):
        if 'task_id' not in request.form:
            raise BadRequest('No task_id specified')
        task_id = request.form['task_id']

        f = request.files['filename']
        if f is None or not f.filename or not self.ll.allowed_file(f.filename):
            raise BadRequest('Invalid file')

        if 'description' in request.form:
            description = request.form['description']
        else:
            description = ''

        self.ll.create_new_attachment(task_id, f, description, current_user)

        return self.redirect(self.url_for('view_task', id=task_id))

    def attachment(self, request, current_user, attachment_id, name):
        att = self.pl.get_attachment(attachment_id)
        if att is None:
            raise NotFound(
                "No attachment found for the id '{}'".format(attachment_id))

        return self.send_from_directory(self.ll.upload_folder, att.path)

    def task_up(self, request, current_user, task_id):
        show_deleted = request.cookies.get('show_deleted')
        self.ll.do_move_task_up(task_id, show_deleted, current_user)
        return self.redirect(request.args.get('next') or self.url_for('index'))

    def task_top(self, request, current_user, task_id):
        self.ll.do_move_task_to_top(task_id, current_user)
        return self.redirect(request.args.get('next') or self.url_for('index'))

    def task_down(self, request, current_user, task_id):
        show_deleted = request.cookies.get('show_deleted')
        self.ll.do_move_task_down(task_id, show_deleted, current_user)
        return self.redirect(request.args.get('next') or self.url_for('index'))

    def task_bottom(self, request, current_user, task_id):
        self.ll.do_move_task_to_bottom(task_id, current_user)

        return self.redirect(request.args.get('next') or self.url_for('index'))

    def long_order_change(self, request, current_user):
        task_to_move_id = self.get_form_or_arg(request,
                                               'long_order_task_to_move')
        if task_to_move_id is None:
            return self.redirect(request.args.get('next') or
                                 self.url_for('index'))

        target_id = self.get_form_or_arg(request, 'long_order_target')
        if target_id is None:
            return self.redirect(request.args.get('next') or
                                 self.url_for('index'))

        self.ll.do_long_order_change(task_to_move_id, target_id, current_user)

        return self.redirect(request.args.get('next') or self.url_for('index'))

    def task_add_tag(self, request, current_user, task_id):

        value = self.get_form_or_arg(request, 'value')
        if value is None or value == '':
            return (self.redirect(request.args.get('next') or
                                  self.url_for('view_task', id=task_id)))

        self.ll.do_add_tag_to_task_by_id(task_id, value, current_user)

        return (self.redirect(request.args.get('next') or
                              self.url_for('view_task', id=task_id)))

    def task_delete_tag(self, request, current_user, task_id, tag_id):

        if tag_id is None:
            tag_id = self.get_form_or_arg(request, 'tag_id')

        self.ll.do_delete_tag_from_task(task_id, tag_id, current_user)

        return (self.redirect(request.args.get('next') or
                              self.url_for('view_task', id=task_id)))

    def task_authorize_user(self, request, current_user, task_id):

        email = self.get_form_or_arg(request, 'email')
        if email is None or email == '':
            return (self.redirect(request.args.get('next') or
                                  self.url_for('view_task', id=task_id)))

        self.ll.do_authorize_user_for_task_by_email(task_id, email,
                                                    current_user)

        return (self.redirect(request.args.get('next') or
                              self.url_for('view_task', id=task_id)))

    def task_pick_user(self, request, current_user, task_id):
        task = self.ll.get_task(task_id, current_user)
        users = self.ll.get_users()
        return self.render_template('pick_user.t.html', task=task, users=users,
                                    cycle=itertools.cycle)

    def task_authorize_user_user(self, request, current_user, task_id,
                                 user_id):
        if user_id is None or user_id == '':
            return (self.redirect(request.args.get('next') or
                                  self.url_for('view_task', id=task_id)))

        self.ll.do_authorize_user_for_task_by_id(task_id, user_id,
                                                 current_user)

        return (self.redirect(request.args.get('next') or
                              self.url_for('view_task', id=task_id)))

    def task_deauthorize_user(self, request, current_user, task_id, user_id):
        if user_id is None:
            user_id = self.get_form_or_arg(request, 'user_id')

        self.ll.do_deauthorize_user_for_task(task_id, user_id, current_user)

        return (self.redirect(request.args.get('next') or
                              self.url_for('view_task', id=task_id)))

    def login(self, request, current_user):
        if request.method == 'GET':
            return self.render_template('login.t.html')
        email = request.form['email']
        password = request.form['password']
        user = self.pl.get_user_by_email(email)

        if user is None:
            self.flash('Username or Password is invalid', 'error')
            return self.redirect(self.url_for('login'))
        if user.hashed_password is None or user.hashed_password == '':
            self.flash('Username or Password is invalid', 'error')
            return self.redirect(self.url_for('login'))
        if not self.check_password_hash(user.hashed_password, password):
            self.flash('Username or Password is invalid', 'error')
            return self.redirect(self.url_for('login'))

        self.login_user(user)
        self.flash('Logged in successfully')
        return self.redirect(request.args.get('next') or self.url_for('index'))

    def logout(self, request, current_user):
        self.logout_user()
        return self.redirect(self.url_for('index'))

    def users(self, request, current_user):
        if request.method == 'GET':
            users = self.ll.get_users()
            return self.render_template('list_users.t.html', users=users,
                                        cycle=itertools.cycle)

        email = request.form['email']
        is_admin = False
        if 'is_admin' in request.form:
            is_admin = bool_from_str(request.form['is_admin'])

        self.ll.do_add_new_user(email, is_admin)

        return self.redirect(self.url_for('list_users'))

    def users_user_get(self, request, current_user, user_id):
        user = self.ll.do_get_user_data(user_id, current_user)
        return self.render_template('view_user.t.html', user=user)

    def show_hide_deleted(self, request, current_user):
        show_deleted = request.args.get('show_deleted')
        resp = self.make_response(
            self.redirect(request.args.get('next') or self.url_for('index')))
        if show_deleted and show_deleted != '0':
            resp.set_cookie('show_deleted', '1')
        else:
            resp.set_cookie('show_deleted', '')
        return resp

    def show_hide_done(self, request, current_user):
        show_done = request.args.get('show_done')
        resp = self.make_response(
            self.redirect(request.args.get('next') or self.url_for('index')))
        if show_done and show_done != '0':
            resp.set_cookie('show_done', '1')
        else:
            resp.set_cookie('show_done', '')
        return resp

    def options(self, request, current_user):
        if request.method == 'GET' or 'key' not in request.form:
            data = self.ll.get_view_options_data()
            return self.render_template('options.t.html', options=data)

        key = request.form['key']
        value = ''
        if 'value' in request.form:
            value = request.form['value']

        self.ll.do_set_option(key, value)

        return self.redirect(request.args.get('next') or
                             self.url_for('view_options'))

    def option_delete(self, request, current_user, key):
        self.ll.do_delete_option(key)
        return self.redirect(request.args.get('next') or
                             self.url_for('view_options'))

    def reset_order_nums(self, request, current_user):
        self.ll.do_reset_order_nums(current_user)
        return self.redirect(request.args.get('next') or self.url_for('index'))

    def export(self, request, current_user):
        if request.method == 'GET':
            return self.render_template('export.t.html', results=None)
        types_to_export = set(k for k in request.form.keys() if
                              k in request.form and request.form[k] == 'all')
        results = self.ll.do_export_data(types_to_export)
        return jsonify(results)

    def import_(self, request, current_user):
        if request.method == 'GET':
            return self.render_template('import.t.html')

        f = request.files.get('file')
        if f is None or not f:
            r = request.form['raw']
            src = json.loads(r)
        else:
            src = json.load(f)

        self.ll.do_import_data(src)

        return self.redirect(self.url_for('index'))

    def task_crud(self, request, current_user):
        if request.method == 'GET':
            tasks = self.ll.get_task_crud_data(current_user)
            return self.render_template('task_crud.t.html', tasks=tasks,
                                        cycle=itertools.cycle)

        crud_data = {}
        for key in request.form.keys():
            if re.match(r'task_\d+_(summary|deadline|is_done|is_deleted|'
                        r'order_num|duration|cost|parent_id)', key):
                crud_data[key] = request.form[key]

        self.ll.do_submit_task_crud(crud_data, current_user)

        return self.redirect(self.url_for('task_crud'))

    def tags(self, request, current_user):
        tags = self.ll.get_tags()
        return self.render_template('list_tags.t.html', tags=tags,
                                    cycle=itertools.cycle)

    def tags_id_get(self, request, current_user, tag_id):
        data = self.ll.get_tag_data(tag_id, current_user)
        return self.render_template('tag.t.html', tag=data['tag'],
                                    tasks=data['tasks'], cycle=itertools.cycle)

    def tags_id_edit(self, request, current_user, tag_id):

        def render_get_response():
            tag = self.ll.get_tag(tag_id)
            return self.render_template("edit_tag.t.html", tag=tag)

        if request.method == 'GET':
            return render_get_response()

        if 'value' not in request.form or 'description' not in request.form:
            return render_get_response()
        value = request.form['value']
        description = request.form['description']
        self.ll.do_edit_tag(tag_id, value, description)

        return self.redirect(self.url_for('view_tag', id=tag_id))

    def task_id_convert_to_tag(self, request, current_user, task_id):
        are_you_sure = request.args.get('are_you_sure')
        if are_you_sure:

            tag = self.ll.convert_task_to_tag(task_id, current_user)

            return self.redirect(
                request.args.get('next') or self.url_for('view_tag',
                                                         id=tag.id))

        task = self.ll.get_task(task_id, current_user)
        return self.render_template('convert_task_to_tag.t.html',
                                    task_id=task.id,
                                    tag_value=task.summary,
                                    tag_description=task.description,
                                    cycle=itertools.cycle,
                                    tasks=task.children)

    def search(self, request, current_user, search_query):
        if search_query is None and request.method == 'POST':
            search_query = request.form['query']

        results = self.ll.search(search_query, current_user)

        return self.render_template('search.t.html', query=search_query,
                                    results=results)

    def task_id_add_dependee(self, request, current_user, task_id,
                             dependee_id):
        if dependee_id is None or dependee_id == '':
            dependee_id = self.get_form_or_arg(request, 'dependee_id')
        if dependee_id is None or dependee_id == '':
            return (self.redirect(request.args.get('next') or
                                  request.args.get('next_url') or
                                  self.url_for('view_task', id=task_id)))

        self.ll.do_add_dependee_to_task(task_id, dependee_id, current_user)

        return (self.redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            self.url_for('view_task', id=task_id)))

    def task_id_remove_dependee(self, request, current_user, task_id,
                                dependee_id):
        if dependee_id is None:
            dependee_id = self.get_form_or_arg(request, 'dependee_id')

        self.ll.do_remove_dependee_from_task(task_id, dependee_id,
                                             current_user)

        return (self.redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            self.url_for('view_task', id=task_id)))

    def task_id_add_dependant(self, request, current_user, task_id,
                              dependant_id):
        if dependant_id is None or dependant_id == '':
            dependant_id = self.get_form_or_arg(request, 'dependant_id')
        if dependant_id is None or dependant_id == '':
            return (self.redirect(request.args.get('next') or
                                  request.args.get('next_url') or
                                  self.url_for('view_task', id=task_id)))

        self.ll.do_add_dependant_to_task(task_id, dependant_id, current_user)

        return (self.redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            self.url_for('view_task', id=task_id)))

    def task_id_remove_dependant(self, request, current_user, task_id,
                                 dependant_id):
        if dependant_id is None:
            dependant_id = self.get_form_or_arg(request, 'dependant_id')

        self.ll.do_remove_dependant_from_task(task_id, dependant_id,
                                              current_user)

        return (self.redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            self.url_for('view_task', id=task_id)))

    def task_id_add_prioritize_before(self, request, current_user, task_id,
                                      prioritize_before_id):
        if prioritize_before_id is None or prioritize_before_id == '':
            prioritize_before_id = self.get_form_or_arg(request,
                                                        'prioritize_before_id')
        if prioritize_before_id is None or prioritize_before_id == '':
            return (self.redirect(request.args.get('next') or
                                  request.args.get('next_url') or
                                  self.url_for('view_task', id=task_id)))

        self.ll.do_add_prioritize_before_to_task(task_id, prioritize_before_id,
                                                 current_user)

        return (self.redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            self.url_for('view_task', id=task_id)))

    def task_id_remove_prioritize_before(self, request, current_user, task_id,
                                         prioritize_before_id):
        if prioritize_before_id is None:
            prioritize_before_id = self.get_form_or_arg(request,
                                                        'prioritize_before_id')

        self.ll.do_remove_prioritize_before_from_task(task_id,
                                                      prioritize_before_id,
                                                      current_user)

        return (self.redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            self.url_for('view_task', id=task_id)))

    def task_id_add_prioritize_after(self, request, current_user, task_id,
                                     prioritize_after_id):
        if prioritize_after_id is None or prioritize_after_id == '':
            prioritize_after_id = self.get_form_or_arg(request,
                                                       'prioritize_after_id')
        if prioritize_after_id is None or prioritize_after_id == '':
            return (self.redirect(request.args.get('next') or
                                  request.args.get('next_url') or
                                  self.url_for('view_task', id=task_id)))

        self.ll.do_add_prioritize_after_to_task(task_id, prioritize_after_id,
                                                current_user)

        return (self.redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            self.url_for('view_task', id=task_id)))

    def task_id_remove_prioritize_after(self, request, current_user, task_id,
                                        prioritize_after_id):
        if prioritize_after_id is None:
            prioritize_after_id = self.get_form_or_arg(request,
                                                       'prioritize_after_id')

        self.ll.do_remove_prioritize_after_from_task(task_id,
                                                     prioritize_after_id,
                                                     current_user)

        return (self.redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            self.url_for('view_task', id=task_id)))
