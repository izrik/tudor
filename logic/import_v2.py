import werkzeug.exceptions

from conversions import money_from_str
import logging_util
from .data_import_error import DataImportError

_logger = logging_util.get_logger_by_name(__name__, 'LogicLayer')


def import_data(pl, src, keep_id_numbers=True):
    # TODO: check for id conflicts for tags
    # TODO: check for id conflicts for comments
    # TODO: check for id conflicts for attachments
    # TODO: check for id conflicts for users
    # TODO: check for key conflicts for options
    # TODO: merge tags?
    # TODO: merge users?
    # TODO: merge options?
    # TODO: merge tasks???
    # TODO: merge comments???
    # TODO: merge attachments???
    #
    # TODO: more run-time checks, instead of relying on the db and pl

    db_objects = []

    if 'format_version' not in src:
        raise werkzeug.exceptions.BadRequest('Missing format_version')
    if src['format_version'] != 2:
        raise werkzeug.exceptions.BadRequest('Bad format_version')

    if 'tasks' not in src:
        src['tasks'] = []
    if 'tags' not in src:
        src['tags'] = []
    if 'comments' not in src:
        src['comments'] = []
    if 'attachments' not in src:
        src['attachments'] = []
    if 'users' not in src:
        src['users'] = []
    if 'options' not in src:
        src['options'] = []

    # TODO: tests

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
            t = pl.create_task(
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
    if pl.count_tasks(task_id_in=task_ids) > 0:
        raise werkzeug.exceptions.Conflict(
            "Some specified task id's already exist in the "
            "database")

    for tag in src['tags']:
        try:
            value = tag['value']
            description = tag.get('description', '')
            t = pl.create_tag(value=value,
                              description=description)
            if keep_id_numbers:
                t.id = tag['id']
            tag['__object__'] = t
        except Exception as e:
            raise DataImportError('Error loading tag', tag, exc=e)
        db_objects.append(t)

    for comment in src['comments']:
        try:
            content = comment['content']
            timestamp = comment['timestamp']
            n = pl.create_comment(content=content,
                                  timestamp=timestamp)
            if keep_id_numbers:
                n.id = comment['id']
            comment['__object__'] = n
        except Exception as e:
            raise DataImportError('Error loading comment', comment, exc=e)
        db_objects.append(n)

    for attachment in src['attachments']:
        try:
            timestamp = attachment['timestamp']
            path = attachment['path']
            filename = attachment['filename']
            description = attachment['description']
            a = pl.create_attachment(path=path,
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
            u = pl.create_user(email=email,
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
            o = pl.create_option(key, value)
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

    for comment in src['comments']:
        try:
            task_map = tasks_by_id[comment['task_id']]
            comment['__object__'].task = task_map['__object__']
        except Exception as e:
            raise DataImportError('Error connecting comment', comment, exc=e)

    for attachment in src['attachments']:
        try:
            task_map = tasks_by_id[attachment['task_id']]
            attachment['__object__'].task = task_map['__object__']
        except Exception as e:
            raise DataImportError('Error connecting attachment',
                                  attachment, exc=e)

    for dbo in db_objects:
        pl.add(dbo)
    pl.commit()
