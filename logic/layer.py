#!/usr/bin/env python

import os
from datetime import datetime
from numbers import Number

from dateutil.parser import parse as dparse
import werkzeug.exceptions
from werkzeug.exceptions import Forbidden
from werkzeug.utils import secure_filename

import logging_util
from conversions import int_from_str, money_from_str
from exception import UserCannotViewTaskException
from models.object_types import ObjectTypes
from models.task_user_ops import TaskUserOps


class LogicLayer(object):
    _logger = logging_util.get_logger_by_name(__name__, 'LogicLayer')

    def __init__(self, upload_folder, allowed_extensions, pl):
        self.pl = pl
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions
        self.pl = pl

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
                        order_num=None, parent_id=None, is_public=None):
        self._logger.debug('begin')
        self._logger.debug('creating the new task')
        date_created = datetime.utcnow()
        date_last_updated = date_created
        task = self.pl.create_task(
            summary=summary, description=description, is_done=is_done,
            is_deleted=is_deleted, deadline=deadline,
            expected_duration_minutes=expected_duration_minutes,
            expected_cost=expected_cost, is_public=is_public,
            date_created=date_created,
            date_last_updated=date_last_updated,
        )

        if order_num is None:
            self._logger.debug('order_num not set, calculating')
            order_num = self.get_lowest_order_num()
            if order_num is not None:
                order_num -= 2
            else:
                order_num = 0

        task.order_num = order_num

        if parent_id is not None:
            self._logger.debug('parent_id specified. looking it up (%d)',
                               parent_id)
            parent = self.pl.get_task(parent_id)
            if (parent is not None and
                    not TaskUserOps.is_user_authorized_or_admin(parent,
                                                                current_user)):
                self._logger.debug('User (%d) not authorized for parent (%d)',
                                   current_user.id, parent_id)
                raise werkzeug.exceptions.Forbidden()
            task.parent = parent

        self._logger.debug('authorizing the current user for this task')
        task.users.append(current_user)

        self._logger.debug('adding the task to the session')
        self.pl.add(task)
        self._logger.debug('committing')
        self.pl.commit()

        self._logger.debug('end')
        return task

    def get_lowest_order_num(self):
        self._logger.debug('getting lowest order task')
        tasks = self.pl.get_tasks(
            order_by=[[self.pl.ORDER_NUM, self.pl.ASCENDING]], limit=1)
        self._logger.debug('rendering list')
        lowest_order_num_tasks = list(tasks)
        self._logger.debug('checking list size')
        if len(lowest_order_num_tasks) > 0:
            self._logger.debug('list size > 0, lowest order_num == %d',
                               lowest_order_num_tasks[0].order_num)
            return lowest_order_num_tasks[0].order_num
        self._logger.debug('list size == 0')
        return None

    def get_highest_order_num(self):
        self._logger.debug('getting highest order task')
        tasks = self.pl.get_tasks(
            order_by=[[self.pl.ORDER_NUM, self.pl.DESCENDING]], limit=1)
        self._logger.debug('rendering list')
        highest_order_num_tasks = list(tasks)
        self._logger.debug('checking list size')
        if len(highest_order_num_tasks) > 0:
            self._logger.debug('list size > 0, highest order_num == %d',
                               highest_order_num_tasks[0].order_num)
            return highest_order_num_tasks[0].order_num
        self._logger.debug('list size == 0')
        return None

    def task_set_done(self, id, current_user):
        task = self.pl.get_task(id)
        if not task:
            raise werkzeug.exceptions.NotFound()
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()
        task.is_done = True
        task.date_last_updated = datetime.utcnow()
        self.pl.commit()
        return task

    def task_unset_done(self, id, current_user):
        task = self.pl.get_task(id)
        if not task:
            raise werkzeug.exceptions.NotFound()
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()
        task.is_done = False
        task.date_last_updated = datetime.utcnow()
        self.pl.commit()
        return task

    def task_set_deleted(self, id, current_user):
        task = self.pl.get_task(id)
        if not task:
            raise werkzeug.exceptions.NotFound()
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()
        task.is_deleted = True
        task.date_last_updated = datetime.utcnow()
        self.pl.commit()
        return task

    def task_unset_deleted(self, id, current_user):
        task = self.pl.get_task(id)
        if not task:
            raise werkzeug.exceptions.NotFound()
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()
        task.is_deleted = False
        task.date_last_updated = datetime.utcnow()
        self.pl.commit()
        return task

    def get_task_data(self, id, current_user, include_deleted=True,
                      include_done=True, page_num=1, tasks_per_page=20):

        if page_num is not None and not isinstance(page_num, Number):
            raise TypeError('page_num must be a number')
        if page_num is not None and page_num < 1:
            raise ValueError('page_num must be greater than zero')
        if tasks_per_page is not None and not isinstance(tasks_per_page,
                                                         Number):
            raise TypeError('tasks_per_page must be a number')
        if tasks_per_page is not None and tasks_per_page < 1:
            raise ValueError('tasks_per_page must be greater than zero')

        task = self.pl.get_task(id)
        # TODO: normalize access restrictions and exceptions in LogicLayer
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if TaskUserOps.is_user_authorized_or_admin(task, current_user):
            pass
        elif task.is_public:
            pass
        elif current_user and current_user.is_authenticated:
            raise werkzeug.exceptions.Forbidden()
        else:
            raise werkzeug.exceptions.Unauthorized()

        _pager = []
        descendants = self.load_no_hierarchy(current_user=current_user,
                                             include_done=include_done,
                                             include_deleted=include_deleted,
                                             order_by_order_num=True,
                                             parent_id=task.id, paginate=True,
                                             pager=_pager, page_num=page_num,
                                             tasks_per_page=tasks_per_page)
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
        # TODO: normalize access restrictions and exceptions in LogicLayer
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if TaskUserOps.is_user_authorized_or_admin(task, current_user):
            pass
        elif task.is_public:
            pass
        elif current_user and current_user.is_authenticated:
            raise werkzeug.exceptions.Forbidden()
        else:
            raise werkzeug.exceptions.Unauthorized()

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
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()
        timestamp = datetime.utcnow()
        note = self.pl.create_note(content, timestamp)
        note.task = task
        self.pl.add(note)
        self.pl.commit()
        return note

    def set_task(self, task_id, current_user, summary, description,
                 deadline=None, is_done=False, is_deleted=False,
                 order_num=None, duration=None, expected_cost=None,
                 parent_id=None, is_public=False):

        task = self.pl.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
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
            parent = None
        elif parent_id == '':
            parent = None
        else:
            parent = self.pl.get_task(parent_id)
            if parent:
                pass
            else:
                parent_id = None
                parent = None

        task.summary = summary
        task.description = description

        task.deadline = deadline

        task.is_done = is_done
        task.is_deleted = is_deleted

        task.order_num = order_num

        task.expected_duration_minutes = duration

        task.expected_cost = expected_cost

        task.parent = parent

        task.is_public = is_public

        task.date_last_updated = datetime.utcnow()

        self.pl.commit()

        return task

    def get_edit_task_data(self, id, current_user):
        task = self.pl.get_task(id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
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

    def create_new_attachment(self, task_id, f, description, current_user,
                              timestamp=None):

        task = self.pl.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                'No task found for the task_id "{}"'.format(task_id))
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        path = secure_filename(f.filename)
        f.save(os.path.join(self.upload_folder, path))

        filename = os.path.split(path)[1]
        att = self.pl.create_attachment(path, description, timestamp=timestamp,
                                        filename=filename)
        att.task = task

        self.pl.add(att)
        self.pl.commit()

        return att

    def reorder_tasks(self, tasks):
        tasks = list(tasks)
        N = len(tasks)
        for i in range(N):
            tasks[i].order_num = 2 * (N - i)
            self.pl.add(tasks[i])

    def do_move_task_up(self, id, show_deleted, current_user):
        update_timestamp = datetime.utcnow()
        task = self.pl.get_task(id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
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
                tasks_to_reorder = self.pl.get_tasks(
                    parent_id=task.parent_id,
                    order_by=[[
                        self.pl.ORDER_NUM,
                        self.pl.DESCENDING]])
                self.reorder_tasks(tasks_to_reorder)
                for ttr in tasks_to_reorder:
                    ttr.date_last_updated = update_timestamp
            if next_task.order_num > task.order_num:
                new_order_num = next_task.order_num
                task.order_num, next_task.order_num = \
                    new_order_num, task.order_num

            # TODO: remove all redundant add()'s everywhere
            task.date_last_updated = update_timestamp
            next_task.date_last_updated = update_timestamp
            self.pl.add(task)
            self.pl.add(next_task)

        self.pl.commit()

        return task

    def do_move_task_to_top(self, id, current_user):
        task = self.pl.get_task(id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()
        kwargs = {
            'parent_id': task.parent_id,
            'order_by': [[self.pl.ORDER_NUM, self.pl.DESCENDING]],
            'limit': 1
        }

        top_task = list(self.pl.get_tasks(**kwargs))
        if top_task and top_task[0] is not task:
            task.order_num = top_task[0].order_num + 1
            task.date_last_updated = datetime.utcnow()
            self.pl.add(task)

        self.pl.commit()

        return task

    def do_move_task_down(self, id, show_deleted, current_user):
        update_timestamp = datetime.utcnow()
        task = self.pl.get_task(id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
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
                tasks_to_reorder = self.pl.get_tasks(
                    parent_id=task.parent_id,
                    order_by=[[
                        self.pl.ORDER_NUM,
                        self.pl.DESCENDING]])
                self.reorder_tasks(tasks_to_reorder)
                for ttr in tasks_to_reorder:
                    ttr.date_last_updated = update_timestamp
            if next_task.order_num < task.order_num:
                new_order_num = next_task.order_num
                task.order_num, next_task.order_num = \
                    new_order_num, task.order_num

            task.date_last_updated = update_timestamp
            next_task.date_last_updated = update_timestamp
            self.pl.add(task)
            self.pl.add(next_task)

        self.pl.commit()

        return task

    def do_move_task_to_bottom(self, id, current_user):
        task = self.pl.get_task(id)
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        kwargs = {
            'parent_id': task.parent_id,
            'order_by': [[self.pl.ORDER_NUM, self.pl.ASCENDING]],
            'limit': 1,
        }

        bottom_task = list(self.pl.get_tasks(**kwargs))
        if bottom_task and bottom_task[0] is not task:
            task.order_num = bottom_task[0].order_num - 2
            task.date_last_updated = datetime.utcnow()
            self.pl.add(task)

        self.pl.commit()

        return task

    def do_long_order_change(self, task_to_move_id, target_id, current_user):
        update_timestamp = datetime.utcnow()
        task_to_move = self.pl.get_task(task_to_move_id)
        if task_to_move is None:
            raise werkzeug.exceptions.NotFound(
                "No task object found for id '{}'".format(task_to_move_id))
        target = self.pl.get_task(target_id)
        if target is None:
            raise werkzeug.exceptions.NotFound(
                "No task object found for id '{}'".format(target_id))

        if not TaskUserOps.is_user_authorized_or_admin(task_to_move,
                                                       current_user):
            raise werkzeug.exceptions.Forbidden()
        if not TaskUserOps.is_user_authorized_or_admin(target, current_user):
            raise werkzeug.exceptions.Forbidden()

        if target.parent_id != task_to_move.parent_id:
            raise werkzeug.exceptions.Conflict(
                "Tasks '{}' and '{}' have different parents ('{}' and '{}'"
                ", respectively). Long order changes are not allowed to "
                "change the parenting hierarchy.".format(
                    task_to_move_id, target_id, task_to_move.parent_id,
                    target.parent_id))

        siblings = list(self.pl.get_tasks(parent_id=target.parent_id))
        siblings2 = sorted(siblings, key=lambda t: t.order_num,
                           reverse=True)

        k = len(siblings) * 2
        for s in siblings2:
            s.order_num = k
            s.date_last_updated = update_timestamp
            k -= 2

        task_to_move.order_num = target.order_num + 1
        task_to_move.date_last_updated = update_timestamp
        siblings2 = sorted(siblings, key=lambda t: t.order_num,
                           reverse=True)

        k = len(siblings) * 2
        for s in siblings2:
            s.order_num = k
            s.date_last_updated = update_timestamp
            k -= 2
            self.pl.add(s)

        self.pl.commit()

        return task_to_move, target

    def do_add_tag_to_task_by_id(self, id, value, current_user):
        task = self.pl.get_task(id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(id))
        return self.do_add_tag_to_task(task, value, current_user)

    def do_add_tag_to_task(self, task, value, current_user):
        if task is None:
            raise ValueError('No task specified')
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        tag = self.get_or_create_tag(value)

        if tag not in task.tags:
            task.tags.append(tag)
            self.pl.add(task)

        self.pl.commit()

        return tag

    def get_or_create_tag(self, value):
        tag = self.pl.get_tag_by_value(value)
        if tag is None:
            tag = self.pl.create_tag(value)
            self.pl.add(tag)
            self.pl.commit()
        return tag

    def do_delete_tag_from_task(self, task_id, tag_id, current_user):
        if tag_id is None:
            raise ValueError("No tag_id was specified.")

        task = self.pl.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(task_id))
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        tag = self.pl.get_tag(tag_id)
        if tag is not None:
            if tag in task.tags:
                task.tags.remove(tag)
                self.pl.add(task)
                self.pl.add(tag)

        self.pl.commit()

        return tag

    def do_authorize_user_for_task(self, task, user_to_authorize,
                                   current_user):
        if task is None:
            raise ValueError("No task was specified.")
        if user_to_authorize is None:
            raise ValueError("No user was specified.")
        if current_user is None:
            raise ValueError("No current_user was specified.")
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        if user_to_authorize not in task.users:
            task.users.append(user_to_authorize)

        self.pl.commit()

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
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
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
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
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
        if current_user is None:
            raise ValueError("No current_user was specified.")

        task = self.pl.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(task_id))

        user_to_deauthorize = self.pl.get_user(user_id)
        if user_to_deauthorize is None:
            raise werkzeug.exceptions.NotFound(
                "No user found for the id '{}'".format(user_id))
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        if user_to_deauthorize not in task.users:
            return task

        if len(task.users) < 2:
            # TODO: maybe re-think this. the task is never inaccessible to
            # admins, after all.
            raise werkzeug.exceptions.Conflict(
                "The user cannot be de-authorized. It is the last authorized "
                "user for the task. De-authorizing the user would make the "
                "task inaccessible.")

        task.users.remove(user_to_deauthorize)
        self.pl.add(task)
        self.pl.add(user_to_deauthorize)

        self.pl.commit()

        return task

    def do_add_new_user(self, email, is_admin=False):
        user = self.pl.get_user_by_email(email)
        if user is not None:
            raise werkzeug.exceptions.Conflict(
                "A user already exists with the email address '{}'".format(
                    email))
        user = self.pl.create_user(email=email, is_admin=is_admin)
        self.pl.add(user)
        self.pl.commit()
        return user

    def do_get_user_data(self, user_id, current_user):
        user = self.pl.get_user(user_id)
        if user is None:
            raise werkzeug.exceptions.NotFound(
                f"No user found for the id '{user_id}'")
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
            option = self.pl.create_option(key, value)
        self.pl.add(option)
        self.pl.commit()
        return option

    def do_delete_option(self, key):
        option = self.pl.get_option(key)
        if option is None:
            return None
        self.pl.delete(option)
        self.pl.commit()
        return option

    def do_reset_order_nums(self, current_user):
        update_timestamp = datetime.utcnow()
        tasks_h = self.load(current_user, root_task_id=None, max_depth=None,
                            include_done=True, include_deleted=True)
        tasks_h = self.sort_by_hierarchy(tasks_h)

        k = len(tasks_h) + 1
        for task in tasks_h:
            if task is None:
                continue
            task.order_num = 2 * k
            task.date_last_updated = update_timestamp
            self.pl.add(task)
            k -= 1

        self.pl.commit()

        return tasks_h

    def do_export_data(self, types_to_export):
        results = {'format_version': 1}
        if 'tasks' in types_to_export:
            results['tasks'] = [t.to_flat_dict() for t in self.pl.get_tasks()]
        if 'tags' in types_to_export:
            results['tags'] = [t.to_flat_dict() for t in self.pl.get_tags()]
        if 'notes' in types_to_export:
            results['notes'] = [t.to_flat_dict() for t in self.pl.get_notes()]
        if 'attachments' in types_to_export:
            results['attachments'] = [t.to_flat_dict() for t in
                                      self.pl.get_attachments()]
        if 'users' in types_to_export:
            results['users'] = [t.to_flat_dict() for t in self.pl.get_users()]
        if 'options' in types_to_export:
            results['options'] = [t.to_flat_dict() for t in
                                  self.pl.get_options()]
        return results

    def do_import_data(self, src, keep_id_numbers=True):

        # TODO: check for id conflicts for tags
        # TODO: check for id conflicts for notes
        # TODO: check for id conflicts for attachments
        # TODO: check for id conflicts for users
        # TODO: check for key conflicts for options
        # TODO: merge tags?
        # TODO: merge users?
        # TODO: merge options?
        # TODO: merge tasks???
        # TODO: merge notes???
        # TODO: merge attachments???
        #
        # TODO: more run-time checks, insteead of relying on the db and pl

        db_objects = []

        if 'format_version' not in src:
            raise werkzeug.exceptions.BadRequest('Missing format_version')
        if src['format_version'] != 1:
            raise werkzeug.exceptions.BadRequest('Bad format_version')

        if 'tasks' not in src:
            src['tasks'] = []
        if 'tags' not in src:
            src['tags'] = []
        if 'notes' not in src:
            src['notes'] = []
        if 'attachments' not in src:
            src['attachments'] = []
        if 'users' not in src:
            src['users'] = []
        if 'options' not in src:
            src['options'] = []

        class DataImportError(Exception):
            def __init__(self, message, obj=None, exc=None):
                if obj:
                    message = f'{message}: {obj}'
                if exc:
                    message = f'{message}: {exc}'
                super().__init__(message)
                self.obj = obj
                self.exc = exc

        # TODO: tests

        try:
            try:
                tasks_by_id = {task['id']: task for task in src['tasks']}
            except Exception as e:
                raise DataImportError('Error collecting tasks', exc=e)
            try:
                tags_by_id = {tag['id']: tag for tag in src['tags']}
            except Exception as e:
                raise DataImportError('Error collecting tags', exc=e)
            try:
                users_by_id = {user['id']: user for user in src['users']}
            except Exception as e:
                raise DataImportError('Error collecting users', exc=e)

            for task in src['tasks']:
                try:
                    summary = task['summary']
                    description = task.get('description', '')
                    is_done = task.get('is_done', False)
                    is_deleted = task.get('is_deleted', False)
                    deadline = task.get('deadline', None)
                    exp_dur_min = task.get('expected_duration_minutes')
                    expected_cost = task.get('expected_cost')
                    expected_cost = money_from_str(expected_cost)
                    order_num = task.get('order_num', None)
                    t = self.pl.create_task(
                        summary=summary, description=description,
                        is_done=is_done, is_deleted=is_deleted,
                        deadline=deadline,
                        expected_duration_minutes=exp_dur_min,
                        expected_cost=expected_cost)
                    if keep_id_numbers:
                        t.id = task['id']
                    t.order_num = order_num
                    task['__object__'] = t
                except Exception as e:
                    raise DataImportError('Error loading task', task, exc=e)
                db_objects.append(t)

            try:
                task_ids = set(task['__object__'].id for task in src['tasks'])
            except Exception as e:
                raise DataImportError('Error collecting task id\'s', exc=e)
            if self.pl.count_tasks(task_id_in=task_ids) > 0:
                raise werkzeug.exceptions.Conflict(
                    "Some specified task id's already exist in the "
                    "database")

            for tag in src['tags']:
                try:
                    value = tag['value']
                    description = tag.get('description', '')
                    t = self.pl.create_tag(value=value,
                                           description=description)
                    if keep_id_numbers:
                        t.id = tag['id']
                    tag['__object__'] = t
                except Exception as e:
                    raise DataImportError('Error loading tag', tag, exc=e)
                db_objects.append(t)

            for note in src['notes']:
                try:
                    content = note['content']
                    timestamp = note['timestamp']
                    n = self.pl.create_note(content=content,
                                            timestamp=timestamp)
                    if keep_id_numbers:
                        n.id = note['id']
                    note['__object__'] = n
                except Exception as e:
                    raise DataImportError('Error loading note', note, exc=e)
                db_objects.append(n)

            for attachment in src['attachments']:
                try:
                    timestamp = attachment['timestamp']
                    path = attachment['path']
                    filename = attachment['filename']
                    description = attachment['description']
                    a = self.pl.create_attachment(path=path,
                                                  description=description,
                                                  timestamp=timestamp,
                                                  filename=filename)
                    if keep_id_numbers:
                        a.id = attachment['id']
                    attachment['__object__'] = a
                except Exception as e:
                    raise DataImportError('Error loading attachment',
                                          attachment, exc=e)
                db_objects.append(a)

            for user in src['users']:
                try:
                    email = user['email']
                    hashed_password = user['hashed_password']
                    is_admin = user['is_admin']
                    u = self.pl.create_user(email=email,
                                            hashed_password=hashed_password,
                                            is_admin=is_admin)
                    if keep_id_numbers:
                        u.id = user['id']
                    user['__object__'] = u
                except Exception as e:
                    raise DataImportError('Error loading user', user, exc=e)
                db_objects.append(u)

            for option in src['options']:
                try:
                    key = option['key']
                    value = option['value']
                    o = self.pl.create_option(key, value)
                    option['__object__'] = o
                except Exception as e:
                    raise DataImportError('Error loading option', option, e)
                db_objects.append(o)

            #########

            for task in src['tasks']:
                try:
                    t = task['__object__']
                    if 'tag_ids' in task:
                        for tag_id in task['tag_ids']:
                            tag = tags_by_id[tag_id]['__object__']
                            t.tags.append(tag)
                    if 'user_ids' in task:
                        for user_id in task['user_ids']:
                            user = users_by_id[user_id]['__object__']
                            t.users.append(user)
                    if 'parent_id' in task and task['parent_id'] is not None:
                        t.parent = \
                            tasks_by_id[task['parent_id']]['__object__']
                except Exception as e:
                    raise DataImportError('Error connecting task', task, exc=e)

            for note in src['notes']:
                try:
                    task_map = tasks_by_id[note['task_id']]
                    note['__object__'].task = task_map['__object__']
                except Exception as e:
                    raise DataImportError('Error connecting note', note, exc=e)

            for attachment in src['attachments']:
                try:
                    task_map = tasks_by_id[attachment['task_id']]
                    attachment['__object__'].task = task_map['__object__']
                except Exception as e:
                    raise DataImportError('Error connecting attachment',
                                          attachment, exc=e)

            for dbo in db_objects:
                self.pl.add(dbo)
            self.pl.commit()

        except werkzeug.exceptions.HTTPException as e:
            self._logger.error(f'Exception while importing data: {e}')
            raise
        except DataImportError as e:
            self._logger.error(f'Exception while importing data: {e}')
            raise werkzeug.exceptions.BadRequest('The data was incorrect')
        except Exception as e:
            self._logger.error(f'Exception while importing data: {e}')
            raise werkzeug.exceptions.InternalServerError

    def get_task_crud_data(self, current_user):
        return self.load_no_hierarchy(current_user, include_done=True,
                                      include_deleted=True)

    def do_submit_task_crud(self, crud_data, current_user):
        if current_user is None:
            # guest users not allowed
            raise ValueError('current_user cannot be None.')
        if current_user.is_anonymous:
            # guest users not allowed
            # TODO: use a better exception type for unauthorized operations
            raise TypeError('Invalid user type.')

        current_timestamp = datetime.utcnow()

        # TODO: only load tasks that are specified in crud_data
        tasks = self.load_no_hierarchy(current_user, include_done=True,
                                       include_deleted=True)

        for task in tasks:
            # TODO: re-arrange so that alll statements related to a given
            # attribute are together
            summary = crud_data.get('task_{}_summary'.format(task.id))
            deadline = crud_data.get('task_{}_deadline'.format(task.id))
            is_done = crud_data.get('task_{}_is_done'.format(task.id))
            is_deleted = crud_data.get(
                'task_{}_is_deleted'.format(task.id))
            order_num = crud_data.get('task_{}_order_num'.format(task.id))
            duration = crud_data.get('task_{}_duration'.format(task.id))
            cost = crud_data.get('task_{}_cost'.format(task.id))
            parent_id = crud_data.get('task_{}_parent_id'.format(task.id))

            # TODO: Normalize the values the same way the class would, e.g. use
            # Task._clean_deadline to normalize the deadline.
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

            changed = False
            # TODO: clarify when None means "None" and when it means "Don't set
            # this value".
            if summary is not None and task.summary != summary:
                task.summary = summary
                changed = True
            if task.deadline != deadline:
                task.deadline = deadline
                changed = True
            if task.is_done != is_done:
                task.is_done = is_done
                changed = True
            if task.is_deleted != is_deleted:
                task.is_deleted = is_deleted
                changed = True
            if order_num is not None and task.order_num != order_num:
                task.order_num = order_num
                changed = True
            if task.expected_duration_minutes != duration:
                task.expected_duration_minutes = duration
                changed = True
            if task.expected_cost != cost:
                task.expected_cost = cost
                changed = True
            new_parent = self.pl.get_task(parent_id)
            if task.parent != new_parent:
                task.parent = new_parent
                changed = True

            if changed:
                task.date_last_updated = current_timestamp

            self.pl.add(task)

        self.pl.commit()

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
        tag = self.pl.get_tag(tag_id)
        if not tag:
            raise werkzeug.exceptions.NotFound(
                "No tag found for the id '{}'".format(tag_id))
        tag.value = value
        tag.description = description
        self.pl.add(tag)
        self.pl.commit()
        return tag

    def get_task(self, task_id, current_user):
        task = self.pl.get_task(task_id)
        # TODO: normalize access restrictions and exceptions in LogicLayer
        if task is None:
            raise werkzeug.exceptions.NotFound()
        if TaskUserOps.is_user_authorized_or_admin(task, current_user):
            pass
        elif task.is_public:
            pass
        else:
            return None
        return task

    def convert_task_to_tag(self, task_id, current_user):
        task = self.get_task(task_id, current_user)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(id))
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        if self.pl.count_tags(value=task.summary) > 0:
            raise werkzeug.exceptions.Conflict(
                'A tag already exists with the name "{}"'.format(
                    task.summary))

        tag = self.pl.create_tag(task.summary, task.description)
        self.pl.add(tag)

        current_timestamp = datetime.utcnow()
        for child in list(task.children):
            child.tags.append(tag)
            child.parent = task.parent
            for tag2 in task.tags:
                child.tags.append(tag2)
            child.date_last_updated = current_timestamp
            self.pl.add(child)

        task.parent = None

        self.pl.delete(task)

        self.pl.commit()

        return tag

    def load(self, current_user, root_task_id=None, max_depth=0,
             include_done=False, include_deleted=False,
             exclude_undeadlined=False):

        if root_task_id is not None:
            root_task = self.get_task(root_task_id, current_user)
            if root_task is None:
                return []
            # TODO: normalize access restrictions and exceptions in LogicLayer
            if TaskUserOps.user_can_view_task(root_task, current_user):
                pass
            else:
                raise UserCannotViewTaskException(current_user, root_task)

        kwargs = {}

        if current_user is None or current_user.is_anonymous:
            kwargs['is_public'] = True
        elif not current_user.is_admin:
            kwargs['is_public_or_users_contains'] = current_user

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
            next_ids = [t.id for t in tasks]
            already_ids = set()
            already_ids.update(next_ids)

            while ((max_depth is None or depth < max_depth) and
                   len(next_ids) > 0):

                depth += 1

                kwargs = {}
                if current_user is None or current_user.is_anonymous:
                    kwargs['is_public'] = True
                elif not current_user.is_admin:
                    kwargs['is_public_or_users_contains'] = current_user
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
                          exclude_non_public=False,
                          tag=None, paginate=False, pager=None, page_num=None,
                          tasks_per_page=None, parent_id_is_none=False,
                          parent_id=None, order_by_order_num=False,
                          order_by_deadline=False):

        kwargs = {}

        if current_user is None or current_user.is_anonymous:
            kwargs['is_public'] = True
        elif not current_user.is_admin:
            kwargs['is_public_or_users_contains'] = current_user

        if not include_done:
            kwargs['is_done'] = False

        if not include_deleted:
            kwargs['is_deleted'] = False

        if exclude_undeadlined:
            kwargs['deadline_is_not_none'] = True

        if exclude_non_public:
            kwargs['is_public'] = True

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
            elif hasattr(tag, 'object_type') and \
                    tag.object_type == ObjectTypes.Tag:
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
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        dependee = self.pl.get_task(dependee_id)
        if dependee is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(dependee_id))
        if not TaskUserOps.is_user_authorized_or_admin(dependee, current_user):
            raise werkzeug.exceptions.Forbidden()

        if dependee not in task.dependees:
            task.dependees.append(dependee)

        self.pl.commit()

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
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        dependee = self.pl.get_task(dependee_id)
        if dependee is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(dependee_id))
        if not TaskUserOps.is_user_authorized_or_admin(dependee, current_user):
            raise werkzeug.exceptions.Forbidden()

        if dependee in task.dependees:
            task.dependees.remove(dependee)
            self.pl.add(task)
            self.pl.add(dependee)

        self.pl.commit()

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
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        prioritize_before = self.pl.get_task(prioritize_before_id)
        if prioritize_before is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(prioritize_before_id))
        if not TaskUserOps.is_user_authorized_or_admin(prioritize_before,
                                                       current_user):
            raise werkzeug.exceptions.Forbidden()

        if prioritize_before not in task.prioritize_before:
            task.prioritize_before.append(prioritize_before)

        self.pl.commit()

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
        if not TaskUserOps.is_user_authorized_or_admin(task, current_user):
            raise werkzeug.exceptions.Forbidden()

        prioritize_before = self.pl.get_task(prioritize_before_id)
        if prioritize_before is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(prioritize_before_id))
        if not TaskUserOps.is_user_authorized_or_admin(prioritize_before,
                                                       current_user):
            raise werkzeug.exceptions.Forbidden()

        if prioritize_before in task.prioritize_before:
            task.prioritize_before.remove(prioritize_before)
            self.pl.add(task)
            self.pl.add(prioritize_before)

        self.pl.commit()

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

    def purge_task(self, task, current_user):
        if not current_user.is_admin:
            raise Forbidden('Current user is not authorized to purge tasks.')
        if task is None:
            raise ValueError('task cannot be None.')
        if not task.is_deleted:
            raise Exception(
                "Task (id {}) has not been deleted.".format(task.id))

        self.pl.delete(task)
        self.pl.commit()

    def purge_all_deleted_tasks(self, current_user):
        if not current_user.is_admin:
            raise Forbidden('Current user is not authorized to purge tasks.')
        n = 0
        deleted_tasks = list(self.pl.get_tasks(is_deleted=True))
        for task in deleted_tasks:
            self.purge_task(task, current_user)
            n += 1
        self.pl.commit()
        return n

    def pl_get_task(self, task_id):
        return self.pl.get_task(task_id)

    def pl_get_attachment(self, attachment_id):
        return self.pl.get_attachment(attachment_id)

    def pl_get_user_by_email(self, email):
        return self.pl.get_user_by_email(email)
