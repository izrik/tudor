#!/usr/bin/env python

import re
import itertools
import os

from dateutil.parser import parse as dparse
import werkzeug.exceptions
from werkzeug import secure_filename

from conversions import int_from_str, money_from_str


class LogicLayer(object):

    def __init__(self, ds, upload_folder, allowed_extensions):
        self.ds = ds
        self.db = self.ds.db
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions

    def flatten(self, lst):
        gen = (x if isinstance(x, list) else [x] for x in lst)
        flattened = itertools.chain.from_iterable(gen)
        return list(flattened)

    def get_root_ids_from_str(self, roots):
        root_ids = roots.split(',')
        for i in xrange(len(root_ids)):
            m = re.match(r'(\d+)\*', root_ids[i])
            if m:
                id = m.group(1)
                task = self.ds.Task.query.get(id)
                root_ids[i] = map(lambda c: c.id, task.children)
        if root_ids:
            root_ids = self.flatten(root_ids)
            return root_ids
        return None

    def get_tasks_and_all_descendants_from_tasks(self, tasks):
        visited = set()
        result = []
        for task in tasks:
            task.get_all_descendants(visited=visited, result=result)
        return result

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

    def get_index_data(self, show_deleted, show_done, roots, tags):
        tasks = None
        if roots is not None:
            root_ids = self.get_root_ids_from_str(roots)
            if root_ids:
                tasks = self.ds.Task.query.filter(
                    self.ds.Task.id.in_(root_ids))

        if tasks is None:
            tasks = self.ds.Task.query.filter(self.ds.Task.parent_id == None)
        if not show_deleted:
            tasks = tasks.filter_by(is_deleted=False)
        if not show_done:
            tasks = tasks.filter_by(is_done=False)
        tasks = tasks.order_by(self.ds.Task.order_num.desc())
        tasks = tasks.all()

        all_tasks = self.get_tasks_and_all_descendants_from_tasks(tasks)
        deadline_tasks = self.ds.Task.load_no_hierarchy(
            exclude_undeadlined=True)

        if tags is not None and len(tags) > 0:
            tags = tags.split(',')
            tasks_h = self.ds.Task.load_no_hierarchy(
                include_done=show_done, include_deleted=show_deleted,
                tags=tags)
        else:
            tasks_h = self.ds.Task.load(roots=None, max_depth=None,
                                        include_done=show_done,
                                        include_deleted=show_deleted)
            tasks_h = self.sort_by_hierarchy(tasks_h)

        all_tags = self.ds.Tag.query.all()
        return {
            'tasks': tasks,
            'show_deleted': show_deleted,
            'show_done': show_done,
            'roots': roots,
            'views': self.ds.View.query,
            'tasks_h': tasks_h,
            'all_tags': all_tags,
        }

    def get_deadlines_data(self):
        deadline_tasks = self.ds.Task.load_no_hierarchy(
            exclude_undeadlined=True)
        return {
            'deadline_tasks': deadline_tasks,
        }

    def create_new_task(self, summary, parent_id):
        task = self.ds.Task(summary)

        # get lowest order number
        query = self.ds.Task.query.order_by(
            self.ds.Task.order_num.asc()).limit(1)
        lowest_order_num_tasks = query.all()
        task.order_num = 0
        if len(lowest_order_num_tasks) > 0:
            task.order_num = lowest_order_num_tasks[0].order_num - 2

        if parent_id is None or parent_id == '':
            task.parent_id = None
        elif self.ds.Task.query.filter_by(id=parent_id).count() > 0:
            task.parent_id = parent_id

        return task

    def task_set_done(self, id):
        task = self.ds.Task.query.filter_by(id=id).first()
        if not task:
            raise werkzeug.exceptions.NotFound()
        task.is_done = True
        return task

    def task_unset_done(self, id):
        task = self.ds.Task.query.filter_by(id=id).first()
        if not task:
            raise werkzeug.exceptions.NotFound()
        task.is_done = False
        return task

    def task_set_deleted(self, id):
        task = self.ds.Task.query.filter_by(id=id).first()
        if not task:
            raise werkzeug.exceptions.NotFound()
        task.is_deleted = True
        return task

    def task_unset_deleted(self, id):
        task = self.ds.Task.query.filter_by(id=id).first()
        if not task:
            raise werkzeug.exceptions.NotFound()
        task.is_deleted = False
        return task

    def get_task_data(self, id):
        task = self.ds.Task.query.filter_by(id=id).first()
        if task is None:
            raise werkzeug.exceptions.NotFound()

        descendants = self.ds.Task.load(roots=task.id, max_depth=None,
                                        include_done=True,
                                        include_deleted=True)

        hierarchy_sort = True
        if hierarchy_sort:
            descendants = self.sort_by_hierarchy(descendants, root=task)

        return {
            'task': task,
            'descendants': descendants,
        }

    def create_new_note(self, task_id, content):
        task = self.ds.Task.query.filter_by(id=task_id).first()
        if task is None:
            raise werkzeug.exceptions.NotFound()
        note = self.ds.Note(content)
        note.task = task
        return note

    def set_task(self, task_id, summary, description, deadline=None,
                 is_done=False, is_deleted=False, order_num=None,
                 duration=None, expected_cost=None, parent_id=None,
                 tags=None):

        if deadline:
            deadline = dparse(deadline)

        if order_num is None:
            order_num = 0

        if parent_id is None:
            pass
        elif parent_id == '':
            parent_id = None
        elif self.ds.Task.query.filter_by(id=parent_id).count() > 0:
            pass
        else:
            parent_id = None

        task = self.ds.Task.query.filter_by(id=task_id).first()
        task.summary = summary
        task.description = description

        task.deadline = deadline

        task.is_done = is_done
        task.is_deleted = is_deleted

        task.order_num = order_num

        task.expected_duration_minutes = duration

        task.expected_cost = expected_cost

        task.parent_id = parent_id

        if tags is not None:
            values = tags.split(',')
            for ttl in task.tags:
                self.db.session.delete(ttl)
            for value in values:
                if value is None or value == '':
                    continue

                tag = self.ds.Tag.query.filter_by(value=value).first()
                if tag is None:
                    tag = self.ds.Tag(value)
                    self.db.session.add(tag)

                ttl = self.ds.TaskTagLink.query.get((task.id, tag.id))
                if ttl is None:
                    ttl = self.ds.TaskTagLink(task.id, tag.id)
                    self.db.session.add(ttl)

        return task

    def get_edit_task_data(self, id):
        task = self.ds.Task.query.filter_by(id=id).first()
        if task is None:
            raise werkzeug.exceptions.NotFound()
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

    def create_new_attachment(self, task_id, f, description):

        task = self.ds.Task.query.filter_by(id=task_id).first()
        if task is None:
            return (('No task found for the task_id "%s"' % task_id), 404)

        path = secure_filename(f.filename)
        f.save(os.path.join(self.upload_folder, path))

        att = self.ds.Attachment(path, description)
        att.task = task

        return att

    def reorder_tasks(self, tasks):
        tasks = list(tasks)
        N = len(tasks)
        for i in xrange(N):
            tasks[i].order_num = 2 * (N - i)
            self.db.session.add(tasks[i])

    def do_move_task_up(self, id, show_deleted):
        task = self.ds.Task.query.get(id)
        siblings = task.get_siblings(show_deleted)
        higher_siblings = siblings.filter(
            self.ds.Task.order_num >= task.order_num)
        higher_siblings = higher_siblings.filter(self.ds.Task.id != task.id)
        next_task = higher_siblings.order_by(
            self.ds.Task.order_num.asc()).first()

        if next_task:
            if task.order_num == next_task.order_num:
                self.reorder_tasks(task.get_siblings(descending=True))
            new_order_num = next_task.order_num
            task.order_num, next_task.order_num =\
                new_order_num, task.order_num

            self.db.session.add(task)
            self.db.session.add(next_task)

        return task

    def do_move_task_to_top(self, id):
        task = self.ds.Task.query.get(id)
        siblings = task.get_siblings(True)
        top_task = siblings.order_by(self.ds.Task.order_num.desc()).first()

        if top_task:
            task.order_num = top_task.order_num + 1

            self.db.session.add(task)

        return task

    def do_move_task_down(self, id, show_deleted):
        task = self.ds.Task.query.get(id)
        siblings = task.get_siblings(show_deleted)
        lower_siblings = siblings.filter(
            self.ds.Task.order_num <= task.order_num)
        lower_siblings = lower_siblings.filter(self.ds.Task.id != task.id)
        next_task = lower_siblings.order_by(
            self.ds.Task.order_num.desc()).first()

        if next_task:
            if task.order_num == next_task.order_num:
                self.reorder_tasks(task.get_siblings(descending=True))
            new_order_num = next_task.order_num
            task.order_num, next_task.order_num =\
                new_order_num, task.order_num

            self.db.session.add(task)
            self.db.session.add(next_task)

        return task

    def do_move_task_to_bottom(self, id):
        task = self.ds.Task.query.get(id)
        siblings = task.get_siblings(True)
        bottom_task = siblings.order_by(self.ds.Task.order_num.asc()).first()

        if bottom_task:
            task.order_num = bottom_task.order_num - 2

            self.db.session.add(task)

        return task

    def do_long_order_change(self, task_to_move_id, target_id):
        task_to_move = self.ds.Task.query.get(task_to_move_id)
        if task_to_move is None:
            raise werkzeug.exceptions.NotFound(
                "No task object found for id '{}'".format(task_to_move_id))

        target = self.ds.Task.query.get(target_id)
        if target is None:
            raise werkzeug.exceptions.NotFound(
                "No task object found for id '{}'".format(target_id))

        if target.parent_id != task_to_move.parent_id:
            raise werkzeug.exceptions.Conflict(
                "Tasks '{}' and '{}' have different parents ('{}' and '{}'"
                ", respectively). Long order changes are not allowed to "
                "change the parenting hierarchy.".format(
                    task_to_move_id, target_id, task_to_move.parent_id,
                    target.parent_id))

        siblings = target.get_siblings(True).all()
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
            self.db.session.add(s)

        return task_to_move, target

    def do_add_tag_to_task(self, id, value):
        task = self.ds.Task.query.get(id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(id))

        tag = self.ds.Tag.query.filter_by(value=value).first()
        if tag is None:
            tag = self.ds.Tag(value)
            self.db.session.add(tag)

        ttl = self.ds.TaskTagLink.query.get((task.id, tag.id))
        if ttl is None:
            ttl = self.ds.TaskTagLink(task.id, tag.id)
            self.db.session.add(ttl)

        return ttl

    def do_delete_tag_from_task(self, task_id, tag_id):
        if tag_id is None:
            raise ValueError("No tag_id was specified.")

        task = self.ds.Task.query.get(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '{}'".format(task_id))

        ttl = self.ds.TaskTagLink.query.get((task_id, tag_id))
        if ttl is not None:
            self.db.session.delete(ttl)

        return ttl

    def do_add_new_user(self, email, is_admin):
        user = self.ds.User.query.get(email)
        if user is not None:
            return werkzeug.exceptions.Conflict(
                "A user already exists with the email address '{}'".format(
                    email))
        user = self.ds.User(email=email, is_admin=is_admin)
        self.db.session.add(user)
        return user

    def do_add_new_view(self, name, roots):
        view = self.ds.View(name, roots)
        self.db.session.add(view)
        return view

    def get_view_options_data(self):
        return self.ds.Option.query

    def do_set_option(self, key, value):
        option = self.ds.Option.query.get(key)
        if option is not None:
            option.value = value
        else:
            option = self.ds.Option(key, value)
        self.db.session.add(option)
        return option

    def do_delete_option(self, key):
        option = self.ds.Option.query.get(key)
        if option is not None:
            self.db.session.delete(option)
        return option

    def do_reset_order_nums(self):
        tasks_h = self.ds.Task.load(roots=None, max_depth=None,
                                    include_done=True, include_deleted=True)
        tasks_h = self.sort_by_hierarchy(tasks_h)

        k = len(tasks_h) + 1
        for task in tasks_h:
            if task is None:
                continue
            task.order_num = 2 * k
            self.db.session.add(task)
            k -= 1
        return tasks_h

    def do_export_data(self, types_to_export):
        results = {}
        if 'tasks' in types_to_export:
            results['tasks'] = [t.to_dict() for t in self.ds.Task.query.all()]
        if 'tags' in types_to_export:
            results['tags'] = [t.to_dict() for t in self.ds.Tag.query.all()]
        if 'notes' in types_to_export:
            results['notes'] = [t.to_dict() for t in self.ds.Note.query.all()]
        if 'attachments' in types_to_export:
            results['attachments'] = [t.to_dict() for t in
                                      self.ds.Attachment.query.all()]
        if 'users' in types_to_export:
            results['users'] = [t.to_dict() for t in self.ds.User.query.all()]
        if 'views' in types_to_export:
            results['views'] = [t.to_dict() for t in self.ds.View.query.all()]
        if 'options' in types_to_export:
            results['options'] = [t.to_dict() for t in
                                  self.ds.Option.query.all()]
        return results

    def do_import_data(self, src):

        db_objects = []

        try:

            if 'tags' in src:
                for tag in src['tags']:
                    task_id = tag['id']
                    value = tag['value']
                    description = tag.get('description', '')
                    t = self.ds.Tag(value=value, description=description)
                    t.id = task_id
                    db_objects.append(t)

            if 'tasks' in src:
                ids = set()
                for task in src['tasks']:
                    ids.add(task['id'])
                existing_tasks = self.ds.Task.query.filter(
                    self.ds.Task.id.in_(ids)).count()
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
                    t = self.ds.Task(summary=summary, description=description,
                                     is_done=is_done, is_deleted=is_deleted,
                                     deadline=deadline,
                                     expected_duration_minutes=exp_dur_min,
                                     expected_cost=expected_cost)
                    t.id = id
                    t.parent_id = parent_id
                    t.order_num = order_num
                    for tag_id in tag_ids:
                        ttl = self.ds.TaskTagLink(t.id, tag_id)
                        db_objects.append(ttl)
                    db_objects.append(t)

            if 'notes' in src:
                ids = set()
                for note in src['notes']:
                    ids.add(note['id'])
                existing_notes = self.ds.Note.query.filter(
                    self.ds.Note.id.in_(ids)).count()
                if existing_notes > 0:
                    raise werkzeug.exceptions.Conflict(
                        'Some specified note id\'s already exist in the '
                        'database')
                for note in src['notes']:
                    id = note['id']
                    content = note['content']
                    timestamp = note['timestamp']
                    task_id = note['task_id']
                    n = self.ds.Note(content=content, timestamp=timestamp)
                    n.id = id
                    n.task_id = task_id
                    db_objects.append(n)

            if 'attachments' in src:
                attachments = src['attachments']
                ids = set()
                for attachment in attachments:
                    ids.add(attachment['id'])
                existing_attachments = self.ds.Attachment.query.filter(
                    self.ds.Attachment.id.in_(ids)).count()
                if existing_attachments > 0:
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
                    a = self.ds.Attachment(path=path, description=description,
                                           timestamp=timestamp,
                                           filename=filename)
                    a.id = id
                    a.task_id = task_id
                    db_objects.append(a)

            if 'users' in src:
                users = src['users']
                emails = set()
                for user in users:
                    emails.add(user['email'])
                existing_users = self.ds.User.query.filter(
                    self.ds.User.email.in_(emails)).count()
                if existing_users > 0:
                    raise werkzeug.exceptions.Conflict(
                        'Some specified user email addresses already exist'
                        ' in the database')
                for user in users:
                    email = user['email']
                    hashed_password = user['hashed_password']
                    is_admin = user['is_admin']
                    u = self.ds.User(email=email,
                                     hashed_password=hashed_password,
                                     is_admin=is_admin)
                    db_objects.append(u)

            if 'views' in src:
                ids = set()
                for view in src['views']:
                    ids.add(view['id'])
                existing_views = self.ds.View.query.filter(
                    self.ds.View.id.in_(ids)).count()
                if existing_views > 0:
                    raise werkzeug.exceptions.Conflict(
                        'Some specified view id\'s already exist in the '
                        'database')
                for view in src['views']:
                    id = view['id']
                    name = view['name']
                    roots = view['roots']
                    v = self.ds.View(name=name, roots=roots)
                    v.id = id
                    db_objects.append(v)

            if 'options' in src:
                keys = set()
                for option in src['options']:
                    keys.add(option['key'])
                existing_options = self.ds.Option.query.filter(
                    self.ds.Option.key.in_(keys)).count()
                if existing_options > 0:
                    raise werkzeug.exceptions.Conflict(
                        'Some specified option keys already exist in the '
                        'database')
                for option in src['options']:
                    key = option['key']
                    value = option['value']
                    t = self.ds.Option(key, value)
                    db_objects.append(t)
        except werkzeug.exceptions.HTTPException:
            raise
        except:
            raise werkzeug.exceptions.BadRequest('The data was incorrect')

        for dbo in db_objects:
            self.db.session.add(dbo)

    def get_task_crud_data(self):
        return self.ds.Task.load_no_hierarchy(include_done=True,
                                              include_deleted=True)

    def do_submit_task_crud(self, crud_data):

        tasks = self.ds.Task.load_no_hierarchy(include_done=True,
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

            self.db.session.add(task)

    def get_tags(self):
        return self.ds.Tag.query.all()

    def get_tag_data(self, tag_id):
        tag = self.ds.Tag.query.get(tag_id)
        if not tag:
            raise werkzeug.exceptions.NotFound(
                "No tag found for the id '{}'".format(tag_id))
        tasks = self.ds.Task.load_no_hierarchy(include_done=True,
                                               include_deleted=True, tags=tag)
        return {
            'tag': tag,
            'tasks': tasks,
        }

    def get_tag(self, tag_id):
        tag = self.ds.Tag.query.get(tag_id)
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
        self.db.session.add(tag)
        return tag

    def get_task(self, task_id):
        return self.ds.Task.query.get(task_id)

    def _convert_task_to_tag(self, task_id):
        task = self.get_task(task_id)
        if task is None:
            raise werkzeug.exceptions.NotFound(
                "No task found for the id '%s'".format(id))

        if self.ds.Tag.query.filter_by(value=task.summary).first():
            raise werkzeug.exceptions.Conflict(
                'A tag already exists with the name "{}"'.format(
                    task.summary))

        tag = self.ds.Tag(task.summary, task.description)
        self.db.session.add(tag)

        for child in task.children:
            ttl = self.ds.TaskTagLink(child.id, tag.id)
            self.db.session.add(ttl)
            child.parent = task.parent
            self.db.session.add(child)
            for ttl2 in task.tags:
                ttl3 = self.ds.TaskTagLink(child.id, ttl2.tag_id)
                self.db.session.add(ttl3)

        for ttl2 in task.tags:
            self.db.session.delete(ttl2)

        task.parent = None
        self.db.session.add(task)

        self.db.session.delete(task)

        # TODO: commit in a non-view function
        self.db.session.commit()

        return tag
