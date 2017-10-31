from itertools import islice

import logging_util
from models.attachment import Attachment
from models.note import Note
from models.option import Option
from models.tag import Tag
from models.task import Task
from models.user import User
from persistence_layer import is_iterable, Pager


class InMemoryPersistenceLayer(object):
    _logger = logging_util.get_logger_by_name(__name__,
                                              'InMemoryPersistenceLayer')

    def __init__(self):
        self._added_objects = set()
        self._deleted_objects = set()
        self._changed_objects = set()
        self._values_by_object = {}

        self._tasks = []
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

    UNSPECIFIED = object()

    ASCENDING = object()
    DESCENDING = object()

    TASK_ID = object()
    ORDER_NUM = object()
    DEADLINE = object()

    def create_all(self):
        pass

    def get_task(self, task_id):
        return self._tasks_by_id.get(task_id)

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
                query = (_ for _ in query if _.parent_id is None)
            else:
                query = (_ for _ in query if _.parent_id == parent_id)

        if parent_id_in is not self.UNSPECIFIED:
            query = (_ for _ in query if _.parent_id in parent_id_in)

        if users_contains is not self.UNSPECIFIED:
            query = (_ for _ in query if users_contains in _.users)

        if is_public_or_users_contains is not self.UNSPECIFIED:
            query = (_ for _ in query if _.is_public or
                     is_public_or_users_contains in _.users)

        if task_id_in is not self.UNSPECIFIED:
            query = (_ for _ in query if _.id in task_id_in)

        if task_id_not_in is not self.UNSPECIFIED:
            query = (_ for _ in query if _.id not in task_id_not_in)

        if deadline_is_not_none:
            query = (_ for _ in query if _.deadline is not None)

        if tags_contains is not self.UNSPECIFIED:
            query = (_ for _ in query if tags_contains in _.tags)

        if summary_description_search_term is not self.UNSPECIFIED:
            term = summary_description_search_term
            query = (_ for _ in query if
                     term in _.summary or term in _.description)

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

        if limit is not self.UNSPECIFIED and limit >= 0:
            query = islice(query, limit)

        return query

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

    def get_tag(self, tag_id):
        if tag_id is None:
            raise ValueError('No tag_id provided.')
        return self._tags_by_id.get(tag_id)

    def get_tag_by_value(self, value):
        return self._tags_by_value.get(value)

    def get_tags(self, value=UNSPECIFIED, limit=None):
        query = self._tags
        if value is not self.UNSPECIFIED:
            query = (_ for _ in query if _.value == value)
        if limit is not None:
            query = islice(query, limit)
        return query

    def count_tags(self, value=UNSPECIFIED, limit=None):
        return len(list(self.get_tags(value=value, limit=limit)))

    def get_attachment(self, attachment_id):
        if attachment_id is None:
            raise ValueError('No attachment_id provided.')
        return self._attachments_by_id.get(attachment_id)

    def get_attachments(self, attachment_id_in=UNSPECIFIED):
        query = (_ for _ in self._attachments)
        if attachment_id_in is not self.UNSPECIFIED:
            query = (_ for _ in query if _.id in attachment_id_in)
        return query

    def count_attachments(self, attachment_id_in=UNSPECIFIED):
        return len(
            list(self.get_attachments(attachment_id_in=attachment_id_in)))

    def get_note(self, note_id):
        if note_id is None:
            raise ValueError('No note_id provided.')
        return self._notes_by_id.get(note_id)

    def get_notes(self, note_id_in=UNSPECIFIED):
        query = self._notes
        if note_id_in is not self.UNSPECIFIED:
            query = (_ for _ in query if _.id in note_id_in)
        return query

    def count_notes(self, note_id_in=UNSPECIFIED):
        return len(list(self.get_notes(note_id_in=note_id_in)))

    def get_option(self, key):
        if key is None:
            raise ValueError('No option_id provided.')
        return self._options_by_key.get(key)

    def get_options(self, key_in=UNSPECIFIED):
        query = self._options
        if key_in is not self.UNSPECIFIED:
            query = (_ for _ in query if _.id in key_in)
        return query

    def count_options(self, key_in=UNSPECIFIED):
        return len(list(self.get_options(key_in=key_in)))

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
        return query

    def count_users(self, email_in=UNSPECIFIED):
        return len(list(self.get_users(email_in=email_in)))

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
            if tt == Attachment:
                if domobj.id is None:
                    domobj.id = self._get_next_attachment_id()
                else:
                    if domobj.id in self._attachments_by_id:
                        raise Exception(
                            'There already exists a attachment with id '
                            '{}'.format(domobj.id))
                self._attachments.append(domobj)
                self._attachments_by_id[domobj.id] = domobj
            elif tt == Note:
                if domobj.id is None:
                    domobj.id = self._get_next_note_id()
                else:
                    if domobj.id in self._notes_by_id:
                        raise Exception(
                            'There already exists a note with id {}'.format(
                                domobj.id))
                self._notes.append(domobj)
                self._notes_by_id[domobj.id] = domobj
            elif tt == Task:
                if domobj.id is None:
                    domobj.id = self._get_next_task_id()
                else:
                    if domobj.id in self._tasks_by_id:
                        raise Exception(
                            'There already exists a task with id {}'.format(
                                domobj.id))
                self._tasks.append(domobj)
                self._tasks_by_id[domobj.id] = domobj
            elif tt == Tag:
                if domobj.id is None:
                    domobj.id = self._get_next_tag_id()
                else:
                    if domobj.id in self._tags_by_id:
                        raise Exception(
                            'There already exists a tag with id {}'.format(
                                domobj.id))
                self._tags.append(domobj)
                self._tags_by_id[domobj.id] = domobj
                self._tags_by_value[domobj.value] = domobj
            elif tt == Option:
                # TODO: autogenerate key?
                self._options.append(domobj)
                self._options_by_key[domobj.id] = domobj
            elif tt == User:
                if domobj.id is None:
                    domobj.id = self._get_next_user_id()
                else:
                    if domobj.id in self._users_by_id:
                        raise Exception(
                            'There already exists a user with id {}'.format(
                                domobj.id))
                self._users.append(domobj)
                self._users_by_id[domobj.id] = domobj
                self._users_by_email[domobj.email] = domobj
                # TODO: update _users_by_email when a user's email changes
            self._added_objects.remove(domobj)
        self._added_objects.clear()

        for domobj in list(self._deleted_objects):
            tt = self._get_object_type(domobj)
            domobj.clear_relationships()

        for domobj in self._tasks:
            self._values_by_object[domobj] = domobj.to_dict()
        for domobj in self._tags:
            self._values_by_object[domobj] = domobj.to_dict()
        for domobj in self._notes:
            self._values_by_object[domobj] = domobj.to_dict()
        for domobj in self._attachments:
            self._values_by_object[domobj] = domobj.to_dict()
        for domobj in self._users:
            self._values_by_object[domobj] = domobj.to_dict()
        for domobj in self._options:
            self._values_by_object[domobj] = domobj.to_dict()

    def _get_next_task_id(self):
        if not self._tasks_by_id:
            return 1
        return max(self._tasks_by_id.iterkeys()) + 1

    def _get_next_tag_id(self):
        if not self._tags_by_id:
            return 1
        return max(self._tags_by_id.iterkeys()) + 1

    def _get_next_note_id(self):
        if not self._notes_by_id:
            return 1
        return max(self._notes_by_id.iterkeys()) + 1

    def _get_next_attachment_id(self):
        if not self._attachments_by_id:
            return 1
        return max(self._attachments_by_id.iterkeys()) + 1

    def _get_next_user_id(self):
        if not self._users_by_id:
            return 1
        return max(self._users_by_id.iterkeys()) + 1

    def rollback(self):
        for t in self._added_objects:
            del self._values_by_object[t]
        self._added_objects.clear()
        for t, d in self._values_by_object.iteritems():
            t.update_from_dict(d)

    def _get_object_type(self, domobj):
        if isinstance(domobj, Attachment):
            return Attachment
        if isinstance(domobj, Note):
            return Note
        if isinstance(domobj, Option):
            return Option
        if isinstance(domobj, Tag):
            return Tag
        if isinstance(domobj, Task):
            return Task
        if isinstance(domobj, User):
            return User
        raise Exception(
            'Unknown object type: {}, {}'.format(domobj,
                                                 type(domobj).__name__))
