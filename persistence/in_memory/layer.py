
from datetime import datetime, UTC
from itertools import islice
from numbers import Number

import logging_util
from models.object_types import ObjectTypes
from persistence.in_memory.models.attachment import Attachment
from persistence.in_memory.models.note import Note
from persistence.in_memory.models.option import Option
from persistence.in_memory.models.tag import Tag
from persistence.in_memory.models.task import Task
from persistence.in_memory.models.user import User
from persistence.sqlalchemy.layer import is_iterable
from persistence.pager import Pager


class InMemoryPersistenceLayer(object):
    _logger = logging_util.get_logger_by_name(__name__,
                                              'InMemoryPersistenceLayer')

    def __init__(self):
        self._added_objects = set()
        self._deleted_objects = set()
        self._changed_objects = set()
        self._values_by_object = {}

        self._tasks = []  # TODO: change these to sets
        self._tasks_by_id = {}

        self._tags = []
        self._tags_by_id = {}
        self._tags_by_value = {}

        self._users = []
        self._users_by_id = {}
        self._users_by_email = {}

        self._options = []
        self._options_by_key = {}

        self._notes = []
        self._notes_by_id = {}

        self._attachments = []
        self._attachments_by_id = {}

        # Relationship dicts
        self._task_tags = {}  # task_id -> set of tag_ids
        self._tag_tasks = {}  # tag_id -> set of task_ids
        self._task_users = {}  # task_id -> set of user_ids
        self._user_tasks = {}  # user_id -> set of task_ids
        self._task_children = {}  # parent_id -> set of child_ids
        self._task_parent = {}  # child_id -> parent_id
        self._task_dependees = {}  # task_id -> set of dependee_ids
        self._dependee_dependants = {}  # dependee_id -> set of dependant_ids
        self._task_prioritize_before = {}  # task_id -> set of before_ids
        self._before_prioritize_after = {}  # before_id -> set of after_ids
        self._task_notes = {}  # task_id -> set of note_ids
        self._task_attachments = {}  # task_id -> set of attachment_ids

    UNSPECIFIED = object()

    ASCENDING = object()
    DESCENDING = object()

    TASK_ID = object()
    ORDER_NUM = object()
    DEADLINE = object()

    def create_all(self):
        pass

    def create_task(self, summary, description='', is_done=False,
                    is_deleted=False, deadline=None,
                    expected_duration_minutes=None, expected_cost=None,
                    is_public=False,
                    date_created=None,
                    date_last_updated=None):
        if date_created is None:
            from datetime import datetime
            date_created = datetime.now(UTC)
        if date_last_updated is None:
            date_last_updated = date_created
        return Task(summary=summary, description=description, is_done=is_done,
                    is_deleted=is_deleted, deadline=deadline,
                    expected_duration_minutes=expected_duration_minutes,
                    expected_cost=expected_cost, is_public=is_public,
                    date_created=date_created,
                    date_last_updated=date_last_updated)

    def get_task(self, task_id):
        stored = self._tasks_by_id.get(task_id)
        if stored is None:
            return None
        return Task.from_dict(stored.to_dict())

    def get_tasks(self, is_done=UNSPECIFIED, is_deleted=UNSPECIFIED,
                  parent_id=UNSPECIFIED, parent_id_in=UNSPECIFIED,
                  users_contains=UNSPECIFIED, task_id_in=UNSPECIFIED,
                  task_id_not_in=UNSPECIFIED, deadline_is_not_none=False,
                  tags_contains=UNSPECIFIED, is_public=UNSPECIFIED,
                  is_public_or_users_contains=UNSPECIFIED,
                  summary_description_search_term=UNSPECIFIED,
                  order_num_greq_than=UNSPECIFIED,
                  order_num_lesseq_than=UNSPECIFIED, order_by=UNSPECIFIED,
                  limit=UNSPECIFIED):

        query = self._tasks

        if is_done is not self.UNSPECIFIED:
            query = (_ for _ in query if _.is_done == is_done)

        if is_deleted is not self.UNSPECIFIED:
            query = (_ for _ in query if _.is_deleted == is_deleted)

        if is_public is not self.UNSPECIFIED:
            query = (_ for _ in query if _.is_public == is_public)

        if parent_id is not self.UNSPECIFIED:
            if parent_id is None:
                query = (_ for _ in query if self._task_parent.get(_.id) is None)
            else:
                query = (_ for _ in query if self._task_parent.get(_.id) == parent_id)

        if parent_id_in is not self.UNSPECIFIED:
            query = (_ for _ in query if self._task_parent.get(_.id) in parent_id_in)

        if users_contains is not self.UNSPECIFIED:
            query = (_ for _ in query if users_contains.id in self._task_users.get(_.id, set()))

        if is_public_or_users_contains is not self.UNSPECIFIED:
            query = (_ for _ in query if _.is_public or is_public_or_users_contains.id in self._task_users.get(_.id, set()))

        if task_id_in is not self.UNSPECIFIED:
            query = (_ for _ in query if _.id in task_id_in)

        if task_id_not_in is not self.UNSPECIFIED:
            query = (_ for _ in query if _.id not in task_id_not_in)

        if deadline_is_not_none:
            query = (_ for _ in query if _.deadline is not None)

        if tags_contains is not self.UNSPECIFIED:
            query = (_ for _ in query if tags_contains.id in self._task_tags.get(_.id, set()))

        if summary_description_search_term is not self.UNSPECIFIED:
            term = summary_description_search_term
            term_lower = term.casefold()
            query = (_ for _ in query if
                     term_lower in _.summary.casefold() or
                     term_lower in _.description.casefold())

        if order_num_greq_than is not self.UNSPECIFIED:
            query = (_ for _ in query if _.order_num >= order_num_greq_than)

        if order_num_lesseq_than is not self.UNSPECIFIED:
            query = (_ for _ in query if _.order_num <= order_num_lesseq_than)

        if order_by is not self.UNSPECIFIED:
            if not is_iterable(order_by):
                sort_key = self._get_sort_key_by_order_field(order_by)
                query = sorted(query, key=sort_key)
            else:
                for ordering in order_by:
                    direction = self.ASCENDING
                    if is_iterable(ordering):
                        order_field = ordering[0]
                        if len(ordering) > 1:
                            direction = ordering[1]
                    else:
                        order_field = ordering
                    sort_key = self._get_sort_key_by_order_field(order_field)
                    if direction is self.ASCENDING:
                        query = sorted(query, key=sort_key)
                    elif direction is self.DESCENDING:
                        query = sorted(query, key=sort_key, reverse=True)
                    else:
                        raise Exception(
                            'Unknown order_by direction: {}'.format(direction))

        if limit is not self.UNSPECIFIED:
            if limit < 0:
                raise Exception('limit must not be negative')
            query = islice(query, limit)

        return (Task.from_dict(_.to_dict()) for _ in query)

    def _get_sort_key_by_order_field(self, order_by):
        if order_by is self.ORDER_NUM:
            return lambda task: task.order_num
        if order_by is self.TASK_ID:
            return lambda task: task.id
        if order_by is self.DEADLINE:
            return lambda task: task.deadline
        raise Exception('Unhandled order_by field: {}'.format(order_by))

    def get_paginated_tasks(self, is_done=UNSPECIFIED, is_deleted=UNSPECIFIED,
                            parent_id=UNSPECIFIED, parent_id_in=UNSPECIFIED,
                            users_contains=UNSPECIFIED, task_id_in=UNSPECIFIED,
                            task_id_not_in=UNSPECIFIED,
                            deadline_is_not_none=False,
                            tags_contains=UNSPECIFIED, is_public=UNSPECIFIED,
                            is_public_or_users_contains=UNSPECIFIED,
                            summary_description_search_term=UNSPECIFIED,
                            order_num_greq_than=UNSPECIFIED,
                            order_num_lesseq_than=UNSPECIFIED,
                            order_by=UNSPECIFIED, limit=UNSPECIFIED,
                            page_num=None, tasks_per_page=None):

        if page_num is not None and not isinstance(page_num, Number):
            raise TypeError('page_num must be a number')
        if page_num is not None and page_num < 1:
            raise ValueError('page_num must be greater than zero')
        if tasks_per_page is not None and not isinstance(tasks_per_page,
                                                         Number):
            raise TypeError('tasks_per_page must be a number')
        if tasks_per_page is not None and tasks_per_page < 1:
            raise ValueError('tasks_per_page must be greater than zero')

        if page_num is None:
            page_num = 1
        if tasks_per_page is None:
            tasks_per_page = 20

        query = self.get_tasks(
            is_done=is_done, is_deleted=is_deleted, parent_id=parent_id,
            parent_id_in=parent_id_in, users_contains=users_contains,
            task_id_in=task_id_in, task_id_not_in=task_id_not_in,
            deadline_is_not_none=deadline_is_not_none,
            tags_contains=tags_contains, is_public=is_public,
            is_public_or_users_contains=is_public_or_users_contains,
            summary_description_search_term=summary_description_search_term,
            order_num_greq_than=order_num_greq_than,
            order_num_lesseq_than=order_num_lesseq_than, order_by=order_by,
            limit=limit)
        tasks = list(query)
        start_task = (page_num - 1) * tasks_per_page
        items = list(islice(tasks, start_task, start_task+tasks_per_page))
        total_tasks = len(tasks)
        num_pages = total_tasks // tasks_per_page
        if total_tasks % tasks_per_page > 0:
            num_pages += 1
        return Pager(page=page_num, per_page=tasks_per_page,
                     items=items, total=total_tasks,
                     num_pages=num_pages, _pager=None)

    def count_tasks(self, is_done=UNSPECIFIED, is_deleted=UNSPECIFIED,
                    parent_id=UNSPECIFIED, parent_id_in=UNSPECIFIED,
                    users_contains=UNSPECIFIED, task_id_in=UNSPECIFIED,
                    task_id_not_in=UNSPECIFIED, deadline_is_not_none=False,
                    tags_contains=UNSPECIFIED, is_public=UNSPECIFIED,
                    is_public_or_users_contains=UNSPECIFIED,
                    summary_description_search_term=UNSPECIFIED,
                    order_num_greq_than=UNSPECIFIED,
                    order_num_lesseq_than=UNSPECIFIED, order_by=UNSPECIFIED,
                    limit=UNSPECIFIED):

        return len(list(self.get_tasks(
            is_done=is_done, is_deleted=is_deleted, parent_id=parent_id,
            parent_id_in=parent_id_in, users_contains=users_contains,
            task_id_in=task_id_in, task_id_not_in=task_id_not_in,
            deadline_is_not_none=deadline_is_not_none,
            tags_contains=tags_contains, is_public=is_public,
            is_public_or_users_contains=is_public_or_users_contains,
            summary_description_search_term=summary_description_search_term,
            order_num_greq_than=order_num_greq_than,
            order_num_lesseq_than=order_num_lesseq_than, order_by=order_by,
            limit=limit)))

    def create_tag(self, value, description=None):
        return Tag(value=value, description=description)

    def get_tag(self, tag_id):
        if tag_id is None:
            raise ValueError('No tag_id provided.')
        stored = self._tags_by_id.get(tag_id)
        if stored is None:
            return None
        return Tag.from_dict(stored.to_dict())

    def get_tag_by_value(self, value):
        return self._tags_by_value.get(value)

    def get_tags(self, value=UNSPECIFIED, limit=None):
        query = self._tags
        if value is not self.UNSPECIFIED:
            query = (_ for _ in query if _.value == value)
        if limit is not None:
            query = islice(query, limit)
        return (Tag.from_dict(_.to_dict()) for _ in query)

    def count_tags(self, value=UNSPECIFIED, limit=None):
        return len(list(self.get_tags(value=value, limit=limit)))

    def create_attachment(self, path, description=None, timestamp=None,
                          filename=None):
        return Attachment(path=path, description=description,
                          timestamp=timestamp, filename=filename)

    def get_attachment(self, attachment_id):
        if attachment_id is None:
            raise ValueError('No attachment_id provided.')
        return self._attachments_by_id.get(attachment_id)

    def get_attachments(self, attachment_id_in=UNSPECIFIED):
        query = (_ for _ in self._attachments)
        if attachment_id_in is not self.UNSPECIFIED:
            query = (_ for _ in query if _.id in attachment_id_in)
        return (Attachment.from_dict(_.to_dict()) for _ in query)

    def count_attachments(self, attachment_id_in=UNSPECIFIED):
        return len(
            list(self.get_attachments(attachment_id_in=attachment_id_in)))

    def create_note(self, content, timestamp=None):
        return Note(content=content, timestamp=timestamp)

    def get_note(self, note_id):
        if note_id is None:
            raise ValueError('No note_id provided.')
        return self._notes_by_id.get(note_id)

    def get_notes(self, note_id_in=UNSPECIFIED):
        query = self._notes
        if note_id_in is not self.UNSPECIFIED:
            query = (_ for _ in query if _.id in note_id_in)
        return (Note.from_dict(_.to_dict()) for _ in query)

    def count_notes(self, note_id_in=UNSPECIFIED):
        return len(list(self.get_notes(note_id_in=note_id_in)))

    def create_option(self, key, value):
        return Option(key=key, value=value)

    def get_option(self, key):
        if key is None:
            raise ValueError('No option_id provided.')
        return self._options_by_key.get(key)

    def get_options(self, key_in=UNSPECIFIED):
        query = self._options
        if key_in is not self.UNSPECIFIED:
            query = (_ for _ in query if _.key in key_in)
        return (Option(key=_.key, value=_.value) for _ in query)

    def count_options(self, key_in=UNSPECIFIED):
        return len(list(self.get_options(key_in=key_in)))

    # Relationship getters
    def get_task_tags(self, task_id):
        return (Tag.from_dict(self._tags_by_id[tag_id].to_dict()) for tag_id in self._task_tags.get(task_id, set()))

    def get_task_users(self, task_id):
        return (User.from_dict(self._users_by_id[user_id].to_dict()) for user_id in self._task_users.get(task_id, set()))

    def get_task_children(self, task_id):
        return (Task.from_dict(self._tasks_by_id[child_id].to_dict()) for child_id in self._task_children.get(task_id, set()))

    def get_task_parent(self, task_id):
        parent_id = self._task_parent.get(task_id)
        if parent_id is None:
            return None
        return Task.from_dict(self._tasks_by_id[parent_id].to_dict())

    def get_task_dependees(self, task_id):
        return (Task.from_dict(self._tasks_by_id[dependee_id].to_dict()) for dependee_id in self._task_dependees.get(task_id, set()))

    def get_task_dependants(self, task_id):
        return (Task.from_dict(self._tasks_by_id[dependant_id].to_dict()) for dependant_id in self._dependee_dependants.get(task_id, set()))

    def get_task_prioritize_before(self, task_id):
        return (Task.from_dict(self._tasks_by_id[before_id].to_dict()) for before_id in self._task_prioritize_before.get(task_id, set()))

    def get_task_prioritize_after(self, task_id):
        return (Task.from_dict(self._tasks_by_id[after_id].to_dict()) for after_id in self._before_prioritize_after.get(task_id, set()))

    def get_task_notes(self, task_id):
        return (Note.from_dict(self._notes_by_id[note_id].to_dict()) for note_id in self._task_notes.get(task_id, set()))

    def get_task_attachments(self, task_id):
        return (Attachment.from_dict(self._attachments_by_id[attachment_id].to_dict()) for attachment_id in self._task_attachments.get(task_id, set()))

    def get_tag_tasks(self, tag_id):
        return (Task.from_dict(self._tasks_by_id[task_id].to_dict()) for task_id in self._tag_tasks.get(tag_id, set()))

    def get_user_tasks(self, user_id):
        return (Task.from_dict(self._tasks_by_id[task_id].to_dict()) for task_id in self._user_tasks.get(user_id, set()))

    # Relationship setters
    def associate_tag_with_task(self, task_id, tag_id):
        self._task_tags.setdefault(task_id, set()).add(tag_id)
        self._tag_tasks.setdefault(tag_id, set()).add(task_id)

    def disassociate_tag_from_task(self, task_id, tag_id):
        self._task_tags.get(task_id, set()).discard(tag_id)
        self._tag_tasks.get(tag_id, set()).discard(task_id)

    def associate_user_with_task(self, task_id, user_id):
        self._task_users.setdefault(task_id, set()).add(user_id)
        self._user_tasks.setdefault(user_id, set()).add(task_id)

    def disassociate_user_from_task(self, task_id, user_id):
        self._task_users.get(task_id, set()).discard(user_id)
        self._user_tasks.get(user_id, set()).discard(task_id)

    def set_task_parent(self, task_id, parent_id):
        old_parent = self._task_parent.get(task_id)
        if old_parent:
            self._task_children[old_parent].discard(task_id)
        self._task_parent[task_id] = parent_id
        if parent_id:
            self._task_children.setdefault(parent_id, set()).add(task_id)

    def associate_dependee_with_task(self, task_id, dependee_id):
        self._task_dependees.setdefault(task_id, set()).add(dependee_id)
        self._dependee_dependants.setdefault(dependee_id, set()).add(task_id)

    def associate_prioritize_before_with_task(self, task_id, before_id):
        self._task_prioritize_before.setdefault(task_id, set()).add(before_id)
        self._before_prioritize_after.setdefault(before_id, set()).add(task_id)

    def associate_note_with_task(self, task_id, note_id):
        self._task_notes.setdefault(task_id, set()).add(note_id)

    def associate_attachment_with_task(self, task_id, attachment_id):
        self._task_attachments.setdefault(task_id, set()).add(attachment_id)

    def create_user(self, email, hashed_password=None, is_admin=False):
        return User(email=email, hashed_password=hashed_password,
                    is_admin=is_admin)

    _guest_user = None

    def get_guest_user(self):
        if self._guest_user is None:
            self._guest_user = self.create_user('guest@guest')
            self._guest_user._is_authenticated = False
            self._guest_user._is_anonymous = True
            self._guest_user.is_admin = False
        return self._guest_user

    def get_user(self, user_id):
        if user_id is None:
            raise ValueError('No user_id provided.')
        return self._users_by_id.get(user_id)

    def get_user_by_email(self, email):
        return self._users_by_email.get(email)

    def get_users(self, email_in=UNSPECIFIED):
        query = self._users
        if email_in is not self.UNSPECIFIED:
            query = (_ for _ in query if _.email in email_in)
        return (User.from_dict(_.to_dict()) for _ in query)

    def count_users(self, email_in=UNSPECIFIED):
        return len(list(self.get_users(email_in=email_in)))

    def save(self, obj):
        if obj.id is None:
            obj.id = self._get_next_id(obj.object_type)
        self.add(obj)
        self.commit()

    def add(self, obj):
        if obj in self._added_objects:
            return
        if obj in self._deleted_objects:
            raise Exception(
                'The object (id={}) has already been deleted.'.format(obj.id))
        if (obj in self._tasks or obj in self._tags or obj in self._notes or
                obj in self._attachments or obj in self._users or
                obj in self._options):
            return
        d = obj.to_dict()
        self._values_by_object[obj] = d
        self._added_objects.add(obj)

    def delete(self, obj):
        if obj in self._deleted_objects:
            return
        if obj in self._added_objects:
            raise Exception(
                'The object (id={}) has already been added.'.format(obj.id))
        self._deleted_objects.add(obj)

    def commit(self):
        for domobj in list(self._added_objects):
            tt = self._get_object_type(domobj)
            if tt != ObjectTypes.Option and domobj.id is None:
                domobj.id = self._get_next_id(tt)
            if tt == ObjectTypes.Task and domobj.order_num is None:
                domobj.order_num = 0

            if tt == ObjectTypes.Attachment:
                if domobj.id in self._attachments_by_id:
                    raise Exception(
                        'There already exists an attachment with id '
                        '{}'.format(domobj.id))
                self._attachments.append(domobj)
                self._attachments_by_id[domobj.id] = domobj
            elif tt == ObjectTypes.Note:
                if domobj.id in self._notes_by_id:
                    raise Exception(
                        'There already exists a note with id {}'.format(
                            domobj.id))
                self._notes.append(domobj)
                self._notes_by_id[domobj.id] = domobj
            elif tt == ObjectTypes.Task:
                if domobj.id in self._tasks_by_id:
                    raise Exception(
                        'There already exists a task with id {}'.format(
                            domobj.id))
                self._tasks.append(domobj)
                self._tasks_by_id[domobj.id] = domobj
            elif tt == ObjectTypes.Tag:
                if domobj.id in self._tags_by_id:
                    raise Exception(
                        'There already exists a tag with id {}'.format(
                            domobj.id))
                if domobj.value in self._tags_by_value:
                    raise Exception(
                        'There already exists a tag with value "{}"'.format(
                            domobj.value))
                self._tags.append(domobj)
                self._tags_by_id[domobj.id] = domobj
                self._tags_by_value[domobj.value] = domobj
            elif tt == ObjectTypes.Option:
                if domobj.key in self._options_by_key:
                    raise Exception(
                        'There already exists an option with key {}'.format(
                            domobj.id))
                self._options.append(domobj)
                self._options_by_key[domobj.id] = domobj
            else:  # tt == ObjectTypes.User
                if domobj.id in self._users_by_id:
                    raise Exception(
                        'There already exists a user with id {}'.format(
                            domobj.id))
                if domobj.email in self._users_by_email:
                    raise Exception(
                        'There already exists a user with email "{}"'.format(
                            domobj.email))
                self._users.append(domobj)
                self._users_by_id[domobj.id] = domobj
                self._users_by_email[domobj.email] = domobj
            self._values_by_object[domobj] = domobj.to_dict()
            self._added_objects.remove(domobj)
        self._added_objects.clear()

        for domobj in list(self._deleted_objects):
            tt = self._get_object_type(domobj)
            if tt == ObjectTypes.Attachment:
                self._attachments.remove(domobj)
                del self._attachments_by_id[domobj.id]
            elif tt == ObjectTypes.Note:
                self._notes.remove(domobj)
                del self._notes_by_id[domobj.id]
            elif tt == ObjectTypes.Task:
                self._tasks.remove(domobj)
                del self._tasks_by_id[domobj.id]
            elif tt == ObjectTypes.Tag:
                self._tags.remove(domobj)
                del self._tags_by_id[domobj.id]
            elif tt == ObjectTypes.Option:
                self._options.remove(domobj)
                del self._options_by_key[domobj.key]
            else:  # tt == ObjectTypes.User
                self._users.remove(domobj)
                del self._users_by_id[domobj.id]
                del self._users_by_email[domobj.email]
            self._deleted_objects.remove(domobj)
        self._deleted_objects.clear()

        def _process_changed_attr(domobj, new_values, type_name, attr_name,
                                  collection):
            old_value = self._values_by_object[domobj][attr_name]
            new_value = new_values[attr_name]
            if old_value != new_value:
                if new_value in collection:
                    raise Exception(
                        'There already exists a {} with {} "{}"'.format(
                            type_name, attr_name, new_value))
                del collection[old_value]
                collection[new_value] = domobj

        for domobj in self._tasks:
            new_values = domobj.to_dict()
            _process_changed_attr(domobj, new_values, 'task', 'id',
                                  self._tasks_by_id)
            if 'order_num' in new_values and new_values['order_num'] is None:
                raise ValueError(
                    'order_num cannot be None, Task "{}" ({})'.format(
                        domobj.summary, domobj.id))
            self._values_by_object[domobj] = new_values
        for domobj in self._tags:
            new_values = domobj.to_dict()
            _process_changed_attr(domobj, new_values, 'tag', 'id',
                                  self._tags_by_id)
            _process_changed_attr(domobj, new_values, 'tag', 'value',
                                  self._tags_by_value)
            self._values_by_object[domobj] = new_values
        for domobj in self._notes:
            new_values = domobj.to_dict()
            _process_changed_attr(domobj, new_values, 'note', 'id',
                                  self._notes_by_id)
            self._values_by_object[domobj] = new_values
        for domobj in self._attachments:
            new_values = domobj.to_dict()
            _process_changed_attr(domobj, new_values, 'attachment', 'id',
                                  self._attachments_by_id)
            self._values_by_object[domobj] = new_values
        for domobj in self._users:
            new_values = domobj.to_dict()
            _process_changed_attr(domobj, new_values, 'user', 'id',
                                  self._users_by_id)
            _process_changed_attr(domobj, new_values, 'user', 'email',
                                  self._users_by_email)
            self._values_by_object[domobj] = new_values
        for domobj in self._options:
            new_values = domobj.to_dict()
            _process_changed_attr(domobj, new_values, 'option', 'key',
                                  self._options_by_key)
            self._values_by_object[domobj] = new_values

        self._clear_affected_objects()

    def _get_next_task_id(self):
        if not self._tasks_by_id:
            return 1
        return max(self._tasks_by_id.keys()) + 1

    def _get_next_tag_id(self):
        if not self._tags_by_id:
            return 1
        return max(self._tags_by_id.keys()) + 1

    def _get_next_note_id(self):
        if not self._notes_by_id:
            return 1
        return max(self._notes_by_id.keys()) + 1

    def _get_next_attachment_id(self):
        if not self._attachments_by_id:
            return 1
        return max(self._attachments_by_id.keys()) + 1

    def _get_next_user_id(self):
        if not self._users_by_id:
            return 1
        return max(self._users_by_id.keys()) + 1

    def _get_next_id(self, objtype):
        if objtype == ObjectTypes.Task:
            return self._get_next_task_id()
        if objtype == ObjectTypes.Tag:
            return self._get_next_tag_id()
        if objtype == ObjectTypes.Attachment:
            return self._get_next_attachment_id()
        if objtype == ObjectTypes.Note:
            return self._get_next_note_id()
        if objtype == ObjectTypes.User:
            return self._get_next_user_id()
        raise Exception(
            'Unknown object type: {}'.format(objtype))

    def rollback(self):
        for t, d in self._values_by_object.items():
            t.update_from_dict(d)
        for t in self._added_objects:
            del self._values_by_object[t]
        self._clear_affected_objects()

    def _clear_affected_objects(self):
        self._changed_objects.clear()
        self._added_objects.clear()
        self._deleted_objects.clear()

    def _get_object_type(self, domobj):
        try:
            tt = domobj.object_type
        except AttributeError:
            raise Exception(
                'Not a domain object: {}, {}'.format(domobj,
                                                     type(domobj).__name__))
        if tt not in ObjectTypes.all:
            raise Exception(
                'Unknown object type: {}, {}, "{}"'.format(
                    domobj, type(domobj).__name__, tt))
        return tt
