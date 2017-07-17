#!/usr/bin/env python

import re
import itertools
import os
from datetime import datetime

from dateutil.parser import parse as dparse
import werkzeug.exceptions
from werkzeug import secure_filename

from conversions import int_from_str, money_from_str
from models.task import Task
from models.tag import Tag
from models.note import NoteBase
from models.attachment import Attachment
from models.option import Option
from models.user import User


class LogicLayer(object):

    def __init__(self, upload_folder, allowed_extensions, pl):
        self.pl = pl
        self.db = self.pl.db
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions
        self.pl = pl

    def is_user_authorized_or_admin(self, task, user):
        if user.is_admin:
            return True
        if task.is_user_authorized(user):
            return True
        return False

    def sort_by_hierarchy(self, tasks, root=None):
        tasks_by_parent = {}

        for d in tasks:
            if d.parent not in tasks_by_parent:
                tasks_by_parent[d.parent] = []
            tasks_by_parent[d.parent].append(d)

        for parent in tasks_by_parent:
            tasks_by_parent[parent] = sorted(tasks_by_parent[parent],
                                             key=lambda t: t.order_num,
                                             reverse=True)

        def get_sorted_order(p):
            yield p
            if p in tasks_by_parent:
                for c in tasks_by_parent[p]:
                    for x in get_sorted_order(c):
                        yield x

        return list(get_sorted_order(root))

    def get_index_data(self, show_deleted, show_done,
                       current_user, page_num=None, tasks_per_page=None):
        _pager = []
        tasks = self.load_no_hierarchy(
            current_user=current_user, include_done=show_done,
            include_deleted=show_deleted, order_by_order_num=True,
            parent_id_is_none=True, paginate=True, pager=_pager,
            page_num=page_num, tasks_per_page=tasks_per_page)
        pager = _pager[0]

        all_tags = list(self.pl.get_tags())
        return {
            'show_deleted': show_deleted,
            'show_done': show_done,
            'tasks': tasks,
            'all_tags': all_tags,
            'pager': pager,
        }

    def get_index_hierarchy_data(self, show_deleted, show_done, current_user):
        max_depth = None
        tasks_h = self.load(current_user, root_task_id=None,
                            max_depth=max_depth, include_done=show_done,
                            include_deleted=show_deleted)
        tasks_h = self.sort_by_hierarchy(tasks_h)

        all_tags = list(self.pl.get_tags())
        return {
            'show_deleted': show_deleted,
            'show_done': show_done,
            'tasks_h': tasks_h,
            'all_tags': all_tags,
        }

    def get_deadlines_data(self, current_user):
        deadline_tasks = self.load_no_hierarchy(
            current_user,
            exclude_undeadlined=True,
            order_by_deadline=True)
        return {
            'deadline_tasks': deadline_tasks,
        }

    def create_new_task(self, summary, current_user, description=None,
                        is_done=None, is_deleted=None, deadline=None,
                        expected_duration_minutes=None, expected_cost=None,
                        order_num=None, parent_id=None):
        task = Task(
            summary=summary, description=description, is_done=is_done,
            is_deleted=is_deleted, deadline=deadline,
            expected_duration_minutes=expected_duration_minutes,
            expected_cost=expected_cost)

        if order_num is None:
            order_num = self.get_lowest_order_num()
            if order_num is not None:
                order_num -= 2
            else:
                order_num = 0

        task.order_num = order_num

        if parent_id is not None:
            parent = self.pl.get_task(parent_id)
            if parent is not None and not self.is_user_authorized_or_admin(
                    parent, current_user):
                raise werkzeug.exceptions.Forbidden()
            task.parent = parent

        task.users.append(current_user)

        return task

    def get_lowest_order_num(self):
        tasks = self.pl.get_tasks(
            order_by=[[self.pl.ORDER_NUM, self.pl.ASCENDING]], limit=1)
        lowest_order_num_tasks = list(tasks)
        if len(lowest_order_num_tasks) > 0:
            return lowest_order_num_tasks[0].order_num
        return None

    def get_highest_order_num(self):
        tasks = self.pl.get_tasks(
            order_by=[[self.pl.ORDER_NUM, self.pl.DESCENDING]], limit=1)
        highest_order_num_tasks = list(tasks)
        if len(highest_order_num_tasks) > 0:
            return highest_order_num_tasks[0].order_num
        return None

    def task_set_done(self, id, current_user):
        task = self.pl.get_task(id)
        if not task:
            raise werkzeug.exceptions.NotFound()
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()
        task.is_done = True
        return task

    def task_unset_done(self, id, current_user):
        task = self.pl.get_task(id)
        if not task:
            raise werkzeug.exceptions.NotFound()
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()
        task.is_done = False
        return task

    def task_set_deleted(self, id, current_user):
        task = self.pl.get_task(id)
        if not task:
            raise werkzeug.exceptions.NotFound()
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()
        task.is_deleted = True
        return task

    def task_unset_deleted(self, id, current_user):
        task = self.pl.get_task(id)
        if not task:
            raise werkzeug.exceptions.NotFound()
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()
        task.is_deleted = False
        return task

    def get_task_data(self, id, current_user, include_deleted=True,
                      include_done=True):
        task = self.pl.get_task(id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        _pager = []
        descendants = self.load_no_hierarchy(current_user=current_user,
                                             include_done=include_done,
                                             include_deleted=include_deleted,
                                             order_by_order_num=True,
                                             parent_id=task.id, paginate=True,
                                             pager=_pager)
        pager = _pager[0]

        hierarchy_sort = True
        if hierarchy_sort:
            descendants = self.sort_by_hierarchy(descendants, root=task)

        return {
            'task': task,
            'descendants': descendants,
            'pager': pager,
        }

    def get_task_hierarchy_data(self, id, current_user, include_deleted=True,
                                include_done=True):
        task = self.pl.get_task(id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        descendants = self.load(current_user, root_task_id=task.id,
                                max_depth=None, include_done=include_done,
                                include_deleted=include_deleted)

        descendants = self.sort_by_hierarchy(descendants, root=task)

        return {
            'task': task,
            'descendants': descendants,
        }

    def create_new_note(self, task_id, content, current_user):
        task = self.pl.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()
        note = Note(content)
        note.task = task
        return note

    def set_task(self, task_id, current_user, summary, description,
                 deadline=None, is_done=False, is_deleted=False,
                 order_num=None, duration=None, expected_cost=None,
                 parent_id=None):

        task = self.pl.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        if deadline is None:
            pass
        elif deadline == '':
            deadline = None
        elif not deadline:
            deadline = None
        elif isinstance(deadline, datetime):
            pass
        else:
            deadline = dparse(deadline)

        if order_num is None:
            order_num = 0

        if parent_id is None:
            pass
        elif parent_id == '':
            parent_id = None
        elif self.pl.get_task(parent_id):
            pass
        else:
            # TODO: does this silently ignore the case when parent_id holds a
            # value that no task has as its id?
            parent_id = None

        task.summary = summary
        task.description = description

        task.deadline = deadline

        task.is_done = is_done
        task.is_deleted = is_deleted

        task.order_num = order_num

        task.expected_duration_minutes = duration

        task.expected_cost = expected_cost

        task.parent_id = parent_id

        return task

    def get_edit_task_data(self, id, current_user):
        task = self.pl.get_task(id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()
        tag_list = ','.join(task.get_tag_values())
        return {
            'task': task,
            'tag_list': tag_list,
        }

    def allowed_file(self, filename):
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1]
        return (ext in self.allowed_extensions)

    def create_new_attachment(self, task_id, f, description, current_user):

        task = self.pl.get_task(task_id)
        if task is None:
            return (('No task found for the task_id "%s"' % task_id), 404)
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        path = secure_filename(f.filename)
        f.save(os.path.join(self.upload_folder, path))

        att = Attachment(path, description)
        att.task = task

        return att

    def reorder_tasks(self, tasks):
        tasks = list(tasks)
        N = len(tasks)
        for i in xrange(N):
            tasks[i].order_num = 2 * (N - i)
            self.pl.add(tasks[i])

    def do_move_task_up(self, id, show_deleted, current_user):
        task = self.pl.get_task(id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        kwargs = {
            'parent_id': task.parent_id,
            'order_num_greq_than': task.order_num,
            'task_id_not_in': [task.id],
            'order_by': self.pl.ORDER_NUM,
            'limit': 1
        }

        if not show_deleted:
            kwargs['is_deleted'] = False

        higher_siblings = list(self.pl.get_tasks(**kwargs))
        if higher_siblings:
            next_task = higher_siblings[0]
            if task.order_num == next_task.order_num:
                self.reorder_tasks(
                    self.pl.get_tasks(parent_id=task.parent_id,
                                      order_by=self.pl.ORDER_NUM))
            new_order_num = next_task.order_num
            task.order_num, next_task.order_num =\
                new_order_num, task.order_num

            self.pl.add(task)
            self.pl.add(next_task)

        return task

    def do_move_task_to_top(self, id, current_user):
        task = self.pl.get_task(id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()
        kwargs = {
            'parent_id': task.parent_id,
            'order_by': [[self.pl.ORDER_NUM, self.pl.DESCENDING]],
            'limit': 1
        }

        top_task = list(self.pl.get_tasks(**kwargs))
        if top_task:
            task.order_num = top_task[0].order_num + 1

            self.pl.add(task)

        return task

    def do_move_task_down(self, id, show_deleted, current_user):
        task = self.pl.get_task(id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        kwargs = {
            'parent_id': task.parent_id,
            'order_num_lesseq_than': task.order_num,
            'task_id_not_in': [task.id],
            'order_by': [[self.pl.ORDER_NUM, self.pl.DESCENDING]],
            'limit': 1,
        }

        if not show_deleted:
            kwargs['is_deleted'] = False

        lower_siblings = list(self.pl.get_tasks(**kwargs))
        if lower_siblings:
            next_task = lower_siblings[0]
            if task.order_num == next_task.order_num:
                self.reorder_tasks(
                    self.pl.get_tasks(parent_id=task.parent_id,
                                      order_by=self.pl.ORDER_NUM))
            new_order_num = next_task.order_num
            task.order_num, next_task.order_num =\
                new_order_num, task.order_num

            self.pl.add(task)
            self.pl.add(next_task)

        return task

    def do_move_task_to_bottom(self, id, current_user):
        task = self.pl.get_task(id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        kwargs = {
            'parent_id': task.parent_id,
            'order_by': [[self.pl.ORDER_NUM, self.pl.ASCENDING]],
            'limit': 1,
        }

        bottom_task = list(self.pl.get_tasks(**kwargs))
        if bottom_task:
            task.order_num = bottom_task[0].order_num - 2

            self.pl.add(task)

        return task

    def do_long_order_change(self, task_to_move_id, target_id, current_user):
        task_to_move = self.pl.get_task(task_to_move_id)
        if task_to_move is None:
            raise werkzeug.exceptions.NotFound(
                "No task object found for id '{}'".format(task_to_move_id))
        if not self.is_user_authorized_or_admin(task_to_move, current_user):
            raise werkzeug.exceptions.Forbidden()

        target = self.pl.get_task(target_id)
        if target is None:
            raise werkzeug.exceptions.NotFound(
                "No task object found for id '{}'".format(target_id))
        if not self.is_user_authorized_or_admin(target, current_user):
            raise werkzeug.exceptions.Forbidden()

        if target.parent_id != task_to_move.parent_id:
            raise werkzeug.exceptions.Conflict(
                "Tasks '{}' and '{}' have different parents ('{}' and '{}'"
                ", respectively). Long order changes are not allowed to "
                "change the parenting hierarchy.".format(
                    task_to_move_id, target_id, task_to_move.parent_id,
                    target.parent_id))

        kwargs = {
            'parent_id': target.parent_id,
        }
        siblings = list(self.pl.get_tasks(parent_id=target.parent_id))
        siblings2 = sorted(siblings, key=lambda t: t.order_num,
                           reverse=True)

        k = len(siblings) * 2
        for s in siblings2:
            s.order_num = k
            k -= 2

        task_to_move.order_num = target.order_num + 1
        siblings2 = sorted(siblings, key=lambda t: t.order_num,
                           reverse=True)

        k = len(siblings) * 2
        for s in siblings2:
            s.order_num = k
            k -= 2
            self.pl.add(s)

        return task_to_move, target

    def do_add_tag_to_task(self, id, value, current_user):
        task = self.pl.get_task(id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(id))
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        tag = self.get_or_create_tag(value)

        if tag not in task.tags:
            task.tags.append(tag)
            self.pl.add(task)

        return tag

    def get_or_create_tag(self, value):
        tag = self.pl.get_tag_by_value(value)
        if tag is None:
            tag = Tag(value)
            self.pl.add(tag)
        return tag

    def do_delete_tag_from_task(self, task_id, tag_id, current_user):
        if tag_id is None:
            raise ValueError("No tag_id was specified.")

        task = self.pl.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(task_id))
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        tag = self.pl.get_tag(tag_id)
        if tag is not None:
            if tag in task.tags:
                task.tags.remove(tag)
                self.pl.add(task)
                self.pl.add(tag)

        return tag

    def do_authorize_user_for_task(self, task, user_to_authorize,
                                   current_user):
        if task is None:
            raise ValueError("No task was specified.")
        if user_to_authorize is None:
            raise ValueError("No user was specified.")
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        if user_to_authorize not in task.users:
            task.users.append(user_to_authorize)

        return task

    def do_authorize_user_for_task_by_email(self, task_id, user_email,
                                            current_user):
        if task_id is None:
            raise ValueError("No task_id was specified.")
        if user_email is None or user_email == '':
            raise ValueError("No user_email was specified.")

        task = self.pl.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(task_id))
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        user_to_authorize = self.pl.get_user_by_email(user_email)
        if user_to_authorize is None:
            raise werkzeug.exceptions.NotFound(
                "No user found for the email '{}'".format(user_email))

        return self.do_authorize_user_for_task(task, user_to_authorize,
                                               current_user)

    def do_authorize_user_for_task_by_id(self, task_id, user_id, current_user):
        if task_id is None:
            raise ValueError("No task_id was specified.")
        if user_id is None:
            raise ValueError("No user_id was specified.")

        task = self.pl.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(task_id))
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        user_to_authorize = self.pl.get_user(user_id)
        if user_to_authorize is None:
            raise werkzeug.exceptions.NotFound(
                "No user found for the id '{}'".format(user_id))

        return self.do_authorize_user_for_task(task, user_to_authorize,
                                               current_user)

    def do_deauthorize_user_for_task(self, task_id, user_id, current_user):
        if task_id is None:
            raise ValueError("No task_id was specified.")
        if user_id is None:
            raise ValueError("No user_id was specified.")

        task = self.pl.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(task_id))

        user_to_deauthorize = self.pl.get_user(user_id)
        if user_to_deauthorize is None:
            raise werkzeug.exceptions.NotFound(
                "No user found for the id '{}'".format(user_id))
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        if len(task.users) < 2:
            raise werkzeug.exceptions.Conflict(
                "The user cannot be de-authorized. It is the last authorized "
                "user for the task. De-authorizing the user would make the "
                "task inaccessible.")

        if user_to_deauthorize in task.users:
            task.users.remove(user_to_deauthorize)
            self.pl.add(task)
            self.pl.add(user_to_deauthorize)

        return task

    def do_add_new_user(self, email, is_admin):
        user = self.pl.get_user_by_email(email)
        if user is not None:
            return werkzeug.exceptions.Conflict(
                "A user already exists with the email address '{}'".format(
                    email))
        user = User(email=email, is_admin=is_admin)
        self.pl.add(user)
        return user

    def do_get_user_data(self, user_id, current_user):
        user = self.pl.get_user(user_id)
        if user is None:
            raise werkzeug.exceptions.NotFound(
                "No user found for the id '%s'".format(user_id))
        if user != current_user and not current_user.is_admin:
            raise werkzeug.exceptions.Forbidden()

        return user

    def get_users(self):
        return self.pl.get_users()

    def get_view_options_data(self):
        return self.pl.get_options()

    def do_set_option(self, key, value):
        option = self.pl.get_option(key)
        if option is not None:
            option.value = value
        else:
            option = Option(key, value)
        self.pl.add(option)
        return option

    def do_delete_option(self, key):
        option = self.pl.get_option(key)
        if option is not None:
            self.pl.delete(option)
        return option

    def do_reset_order_nums(self, current_user):
        tasks_h = self.load(current_user, root_task_id=None, max_depth=None,
                            include_done=True, include_deleted=True)
        tasks_h = self.sort_by_hierarchy(tasks_h)

        k = len(tasks_h) + 1
        for task in tasks_h:
            if task is None:
                continue
            task.order_num = 2 * k
            self.pl.add(task)
            k -= 1
        return tasks_h

    def do_export_data(self, types_to_export):
        results = {}
        if 'tasks' in types_to_export:
            results['tasks'] = [t.to_dict() for t in self.pl.get_tasks()]
        if 'tags' in types_to_export:
            results['tags'] = [t.to_dict() for t in self.pl.get_tags()]
        if 'notes' in types_to_export:
            results['notes'] = [t.to_dict() for t in self.pl.get_notes()]
        if 'attachments' in types_to_export:
            results['attachments'] = [t.to_dict() for t in
                                      self.pl.get_attachments()]
        if 'users' in types_to_export:
            results['users'] = [t.to_dict() for t in self.pl.get_users()]
        if 'options' in types_to_export:
            results['options'] = [t.to_dict() for t in
                                  self.pl.get_options()]
        return results

    def do_import_data(self, src):

        db_objects = []

        try:

            if 'tags' in src:
                for tag in src['tags']:
                    task_id = tag['id']
                    value = tag['value']
                    description = tag.get('description', '')
                    t = Tag(value=value, description=description)
                    t.id = task_id
                    db_objects.append(t)

            if 'tasks' in src:
                ids = set()
                for task in src['tasks']:
                    ids.add(task['id'])
                if ids:
                    existing_tasks = self.pl.count_tasks(task_id_in=ids)
                    if existing_tasks > 0:
                        raise werkzeug.exceptions.Conflict(
                            'Some specified task id\'s already exist in the '
                            'database')
                for task in src['tasks']:
                    id = task['id']
                    summary = task['summary']
                    description = task.get('description', '')
                    is_done = task.get('is_done', False)
                    is_deleted = task.get('is_deleted', False)
                    deadline = task.get('deadline', None)
                    exp_dur_min = task.get('expected_duration_minutes')
                    expected_cost = task.get('expected_cost')
                    parent_id = task.get('parent_id', None)
                    order_num = task.get('order_num', None)
                    tag_ids = task.get('tag_ids', [])
                    user_ids = task.get('user_ids', [])
                    t = Task(summary=summary, description=description,
                             is_done=is_done, is_deleted=is_deleted,
                             deadline=deadline,
                             expected_duration_minutes=exp_dur_min,
                             expected_cost=expected_cost)
                    t.id = id
                    t.parent_id = parent_id
                    t.order_num = order_num
                    for tag_id in tag_ids:
                        tag = self.pl.get_tag(tag_id)
                        if tag is None:
                            tag = next((obj for obj in db_objects
                                        if isinstance(obj, Tag) and
                                        obj.id == tag_id),
                                       None)
                        if tag is None:
                            raise Exception('Tag not found')
                        t.tags.append(tag)
                    for user_id in user_ids:
                        user = self.pl.get_user(user_id)
                        if user is None:
                            user = next((obj for obj in db_objects
                                        if isinstance(obj, User) and
                                         obj.id == user_id),
                                        None)
                        if user is None:
                            raise Exception('User not found')
                        t.users.append(user)
                    db_objects.append(t)

            if 'notes' in src:
                ids = set()
                for note in src['notes']:
                    ids.add(note['id'])
                if ids:
                    if self.pl.count_notes(note_id_in=ids) > 0:
                        raise werkzeug.exceptions.Conflict(
                            'Some specified note id\'s already exist in the '
                            'database')
                for note in src['notes']:
                    id = note['id']
                    content = note['content']
                    timestamp = note['timestamp']
                    task_id = note['task_id']
                    n = Note(content=content, timestamp=timestamp)
                    n.id = id
                    n.task_id = task_id
                    db_objects.append(n)

            if 'attachments' in src:
                attachments = src['attachments']
                ids = set()
                for attachment in attachments:
                    ids.add(attachment['id'])
                if ids:
                    if self.pl.count_attachments(attachment_id_in=ids) > 0:
                        raise werkzeug.exceptions.Conflict(
                            'Some specified attachment id\'s already exist in '
                            'the database')
                for attachment in attachments:
                    id = attachment['id']
                    timestamp = attachment['timestamp']
                    path = attachment['path']
                    filename = attachment['filename']
                    description = attachment['description']
                    task_id = attachment['task_id']
                    a = Attachment(path=path, description=description,
                                   timestamp=timestamp, filename=filename)
                    a.id = id
                    a.task_id = task_id
                    db_objects.append(a)

            if 'users' in src:
                users = src['users']
                emails = set()
                for user in users:
                    emails.add(user['email'])
                if emails:
                    if self.pl.count_users(email_in=emails) > 0:
                        raise werkzeug.exceptions.Conflict(
                            'Some specified user email addresses already exist'
                            ' in the database')
                for user in users:
                    email = user['email']
                    hashed_password = user['hashed_password']
                    is_admin = user['is_admin']
                    u = User(email=email, hashed_password=hashed_password,
                             is_admin=is_admin)
                    db_objects.append(u)

            if 'options' in src:
                keys = set()
                for option in src['options']:
                    keys.add(option['key'])
                if keys:
                    if self.pl.count_options(key_in=keys) > 0:
                        raise werkzeug.exceptions.Conflict(
                            'Some specified option keys already exist in the '
                            'database')
                for option in src['options']:
                    key = option['key']
                    value = option['value']
                    t = Option(key, value)
                    db_objects.append(t)
        except werkzeug.exceptions.HTTPException:
            raise
        except:
            raise werkzeug.exceptions.BadRequest('The data was incorrect')

        for dbo in db_objects:
            self.pl.add(dbo)

    def get_task_crud_data(self, current_user):
        return self.load_no_hierarchy(current_user, include_done=True,
                                      include_deleted=True)

    def do_submit_task_crud(self, crud_data, current_user):

        tasks = self.load_no_hierarchy(current_user, include_done=True,
                                       include_deleted=True)

        for task in tasks:
            summary = crud_data.get('task_{}_summary'.format(task.id))
            deadline = crud_data.get('task_{}_deadline'.format(task.id))
            is_done = crud_data.get('task_{}_is_done'.format(task.id))
            is_deleted = crud_data.get(
                'task_{}_is_deleted'.format(task.id))
            order_num = crud_data.get('task_{}_order_num'.format(task.id))
            duration = crud_data.get('task_{}_duration'.format(task.id))
            cost = crud_data.get('task_{}_cost'.format(task.id))
            parent_id = crud_data.get('task_{}_parent_id'.format(task.id))

            if deadline:
                deadline = dparse(deadline)
            else:
                deadline = None
            is_done = (True if is_done else False)
            is_deleted = (True if is_deleted else False)
            order_num = int_from_str(order_num)
            duration = int_from_str(duration)
            cost = money_from_str(cost)
            parent_id = int_from_str(parent_id)

            if summary is not None:
                task.summary = summary
            task.deadline = deadline
            task.is_done = is_done
            task.is_deleted = is_deleted
            task.order_num = order_num
            task.expected_duration_minutes = duration
            task.expected_cost = cost
            task.parent_id = parent_id

            self.pl.add(task)

    def get_tags(self):
        return list(self.pl.get_tags())

    def get_tag_data(self, tag_id, current_user):
        tag = self.pl.get_tag(tag_id)
        if not tag:
            raise werkzeug.exceptions.NotFound(
                "No tag found for the id '{}'".format(tag_id))
        tasks = self.load_no_hierarchy(current_user, include_done=True,
                                       include_deleted=True, tag=tag)
        return {
            'tag': tag,
            'tasks': tasks,
        }

    def get_tag(self, tag_id):
        tag = self.pl.get_tag(tag_id)
        if not tag:
            raise werkzeug.exceptions.NotFound(
                "No tag found for the id '{}'".format(tag_id))
        return tag

    def do_edit_tag(self, tag_id, value, description):
        tag = self.get_tag(tag_id)
        if not tag:
            raise werkzeug.exceptions.NotFound(
                "No tag found for the id '{}'".format(tag_id))
        tag.value = value
        tag.description = description
        self.pl.add(tag)
        return tag

    def get_task(self, task_id, current_user):
        task = self.pl.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()
        return task

    def _convert_task_to_tag(self, task_id, current_user):
        task = self.get_task(task_id, current_user)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '%s'".format(id))
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        if self.pl.count_tags(value=task.summary) > 0:
            raise werkzeug.exceptions.Conflict(
                'A tag already exists with the name "{}"'.format(
                    task.summary))

        tag = Tag(task.summary, task.description)
        self.pl.add(tag)

        for child in task.children:
            child.tags.append(tag)
            child.parent = task.parent
            for tag2 in task.tags:
                child.tags.append(tag2)
            self.pl.add(child)

        task.parent = None
        self.pl.add(task)

        self.pl.delete(task)

        # TODO: commit in a non-view function
        self.pl.commit()

        return tag

    def load(self, current_user, root_task_id=None, max_depth=0,
             include_done=False, include_deleted=False,
             exclude_undeadlined=False):

        if root_task_id is not None:
            root_task = self.get_task(root_task_id, current_user)
            if not self.is_user_authorized_or_admin(root_task, current_user):
                raise werkzeug.exceptions.Forbidden()

        kwargs = {}

        if not current_user.is_admin:
            kwargs['users_contains'] = current_user

        if not include_done:
            kwargs['is_done'] = False

        if not include_deleted:
            kwargs['is_deleted'] = False

        if exclude_undeadlined:
            kwargs['deadline_is_not_none'] = True

        if root_task_id is None:
            kwargs['parent_id'] = None
        else:
            kwargs['task_id_in'] = [root_task_id]

        kwargs['order_by'] = [
            [self.pl.TASK_ID, self.pl.ASCENDING],
            [self.pl.ORDER_NUM, self.pl.DESCENDING],
        ]

        tasks = list(self.pl.get_tasks(**kwargs))

        depth = 0
        for task in tasks:
            task.depth = depth

        if max_depth is None or max_depth > 0:

            buckets = [tasks]
            next_ids = map(lambda t: t.id, tasks)
            already_ids = set()
            already_ids.update(next_ids)

            while ((max_depth is None or depth < max_depth) and
                   len(next_ids) > 0):

                depth += 1

                kwargs = {}
                if not current_user.is_admin:
                    kwargs['users_contains'] = current_user
                kwargs['parent_id_in'] = next_ids
                kwargs['task_id_not_in'] = already_ids
                if not include_done:
                    kwargs['is_done'] = False
                if not include_deleted:
                    kwargs['is_deleted'] = False
                if exclude_undeadlined:
                    kwargs['deadline_is_not_none'] = True

                children = list(self.pl.get_tasks(**kwargs))

                for child in children:
                    child.depth = depth

                child_ids = set(map(lambda t: t.id, children))
                next_ids = child_ids - already_ids
                already_ids.update(child_ids)
                buckets.append(children)
            tasks = list(
                set([task for bucket in buckets for task in bucket]))

        return tasks

    def load_no_hierarchy(self, current_user, include_done=False,
                          include_deleted=False, exclude_undeadlined=False,
                          tag=None, paginate=False, pager=None, page_num=None,
                          tasks_per_page=None, parent_id_is_none=False,
                          parent_id=None, order_by_order_num=False,
                          order_by_deadline=False):

        kwargs = {}

        if not current_user.is_admin:
            kwargs['users_contains'] = current_user

        if not include_done:
            kwargs['is_done'] = False

        if not include_deleted:
            kwargs['is_deleted'] = False

        if exclude_undeadlined:
            kwargs['deadline_is_not_none'] = True

        if parent_id_is_none:
            kwargs['parent_id'] = None
        elif parent_id is not None:
            kwargs['parent_id'] = parent_id

        if tag is not None:
            if tag == str(tag):
                value = tag
                tag = self.pl.get_tag_by_value(tag)
                if not tag:
                    raise werkzeug.exceptions.NotFound(
                        'No tag found by the name "{}"'.format(value))
            elif isinstance(tag, Tag):
                pass
            else:
                raise TypeError(
                    "Unknown type ('{}') of argument 'tag'".format(type(tag)))

            kwargs['tags_contains'] = tag

        order_by = []
        if order_by_order_num:
            order_by.append([self.pl.ORDER_NUM, self.pl.DESCENDING])

        if order_by_deadline:
            order_by.append([self.pl.DEADLINE, self.pl.ASCENDING])

        if order_by:
            kwargs['order_by'] = order_by

        if paginate:
            kwargs['page_num'] = page_num
            kwargs['tasks_per_page'] = tasks_per_page
            _pager = self.pl.get_paginated_tasks(**kwargs)
            tasks = list(_pager.items)
            for task in tasks:
                task.depth = 0
            if pager is not None:
                pager.append(_pager)
            return tasks

        tasks = self.pl.get_tasks(**kwargs)
        tasks = list(tasks)

        depth = 0
        for task in tasks:
            task.depth = depth

        return tasks

    def search(self, search_query, current_user):

        kwargs = {
            'summary_description_search_term': search_query
        }

        if not current_user.is_admin:
            kwargs['users_contains'] = current_user

        results = self.pl.get_tasks(**kwargs)

        return results

    def do_add_dependee_to_task(self, task_id, dependee_id, current_user):
        if task_id is None:
            raise ValueError("No task_id was specified.")
        if dependee_id is None:
            raise ValueError("No dependee_id was specified.")
        if current_user is None:
            raise ValueError("No current_user was specified.")

        task = self.pl.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(task_id))
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        dependee = self.pl.get_task(dependee_id)
        if dependee is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(dependee_id))
        if not self.is_user_authorized_or_admin(dependee, current_user):
            raise werkzeug.exceptions.Forbidden()

        if dependee not in task.dependees:
            task.dependees.append(dependee)

        return task, dependee

    def do_remove_dependee_from_task(self, task_id, dependee_id, current_user):
        if task_id is None:
            raise ValueError("No task_id was specified.")
        if dependee_id is None:
            raise ValueError("No dependee_id was specified.")
        if current_user is None:
            raise ValueError("No current_user was specified.")

        task = self.pl.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(task_id))
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        dependee = self.pl.get_task(dependee_id)
        if dependee is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(dependee_id))
        if not self.is_user_authorized_or_admin(dependee, current_user):
            raise werkzeug.exceptions.Forbidden()

        if dependee in task.dependees:
            task.dependees.remove(dependee)
            self.pl.add(task)
            self.pl.add(dependee)

        return task, dependee

    def do_add_dependant_to_task(self, task_id, dependant_id, current_user):
        if task_id is None:
            raise ValueError("No task_id was specified.")
        if dependant_id is None:
            raise ValueError("No dependant_id was specified.")
        if current_user is None:
            raise ValueError("No current_user was specified.")

        dependant, task = self.do_add_dependee_to_task(dependant_id, task_id,
                                                       current_user)
        return task, dependant

    def do_remove_dependant_from_task(self, task_id, dependant_id,
                                      current_user):
        if task_id is None:
            raise ValueError("No task_id was specified.")
        if dependant_id is None:
            raise ValueError("No dependant_id was specified.")
        if current_user is None:
            raise ValueError("No current_user was specified.")

        dependant, task = self.do_remove_dependee_from_task(dependant_id,
                                                            task_id,
                                                            current_user)
        return task, dependant

    def do_add_prioritize_before_to_task(self, task_id, prioritize_before_id,
                                         current_user):
        if task_id is None:
            raise ValueError("No task_id was specified.")
        if prioritize_before_id is None:
            raise ValueError("No prioritize_before_id was specified.")
        if current_user is None:
            raise ValueError("No current_user was specified.")

        task = self.pl.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(task_id))
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        prioritize_before = self.pl.get_task(prioritize_before_id)
        if prioritize_before is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(prioritize_before_id))
        if not self.is_user_authorized_or_admin(prioritize_before,
                                                current_user):
            raise werkzeug.exceptions.Forbidden()

        if prioritize_before not in task.prioritize_before:
            task.prioritize_before.append(prioritize_before)

        return task, prioritize_before

    def do_remove_prioritize_before_from_task(self, task_id,
                                              prioritize_before_id,
                                              current_user):
        if task_id is None:
            raise ValueError("No task_id was specified.")
        if prioritize_before_id is None:
            raise ValueError("No prioritize_before_id was specified.")
        if current_user is None:
            raise ValueError("No current_user was specified.")

        task = self.pl.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(task_id))
        if not self.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        prioritize_before = self.pl.get_task(prioritize_before_id)
        if prioritize_before is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(prioritize_before_id))
        if not self.is_user_authorized_or_admin(prioritize_before,
                                                current_user):
            raise werkzeug.exceptions.Forbidden()

        if prioritize_before in task.prioritize_before:
            task.prioritize_before.remove(prioritize_before)
            self.pl.add(task)
            self.pl.add(prioritize_before)

        return task, prioritize_before

    def do_add_prioritize_after_to_task(self, task_id, prioritize_after_id,
                                        current_user):
        if task_id is None:
            raise ValueError("No task_id was specified.")
        if prioritize_after_id is None:
            raise ValueError("No prioritize_after_id was specified.")
        if current_user is None:
            raise ValueError("No current_user was specified.")

        prioritize_after, task = self.do_add_prioritize_before_to_task(
            prioritize_after_id, task_id, current_user)
        return task, prioritize_after

    def do_remove_prioritize_after_from_task(self, task_id,
                                             prioritize_after_id,
                                             current_user):
        if task_id is None:
            raise ValueError("No task_id was specified.")
        if prioritize_after_id is None:
            raise ValueError("No prioritize_after_id was specified.")
        if current_user is None:
            raise ValueError("No current_user was specified.")

        prioritize_after, task = self.do_remove_prioritize_before_from_task(
            prioritize_after_id, task_id, current_user)
        return task, prioritize_after
