from itertools import islice

import logging_util
from models.attachment import Attachment
from models.note import Note
from models.option import Option
from models.tag import Tag
from models.task import Task
from models.user import User


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

    def create_all(self):
        pass

    def get_task(self, task_id):
        return self._tasks_by_id.get(task_id)

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
        if limit is not self.UNSPECIFIED:
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
        if obj in self._deleted_objects:
            raise Exception(
                'The object (id={}) has already been deleted.'.format(obj.id))
        d = obj.to_dict()
        self._values_by_object[obj] = d
        self._added_objects.add(obj)

    def delete(self, obj):
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
            if tt == Attachment:
                pass
            elif tt == Note:
                pass
            elif tt == Task:
                pass
            elif tt == Tag:
                pass
            elif tt == Option:
                pass
            elif tt == User:
                pass
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
