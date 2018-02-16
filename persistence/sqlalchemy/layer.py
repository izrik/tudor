
from __future__ import absolute_import

import collections
from numbers import Number

from sqlalchemy import or_

from persistence.in_memory.models.task import Task
from persistence.in_memory.models.tag import Tag
from persistence.in_memory.models.note import Note
from persistence.in_memory.models.attachment import Attachment
from persistence.in_memory.models.user import User
from persistence.in_memory.models.option import Option
from persistence.sqlalchemy.models.attachment import generate_attachment_class
from persistence.sqlalchemy.models.note import generate_note_class
from persistence.sqlalchemy.models.option import generate_option_class
from persistence.sqlalchemy.models.tag import generate_tag_class
from persistence.sqlalchemy.models.task import generate_task_class
from persistence.sqlalchemy.models.user import generate_user_class
from persistence.pager import Pager

import logging_util


def is_iterable(x):
    return isinstance(x, collections.Iterable)


def as_iterable(x):
    if is_iterable(x):
        return x
    return (x,)


class SqlAlchemyPersistenceLayer(object):
    _logger = logging_util.get_logger_by_name(__name__,
                                              'SqlAlchemyPersistenceLayer')

    def __init__(self, db):
        self.db = db

        self._added_objects = set()
        self._deleted_objects = set()
        self._changed_objects = set()
        self._changed_objects_original_values = {}
        self._committed_objects = set()

        tags_tasks_table = db.Table(
            'tags_tasks',
            db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'),
                      primary_key=True),
            db.Column('task_id', db.Integer, db.ForeignKey('task.id'),
                      primary_key=True))
        self.tags_tasks_table = tags_tasks_table

        self.DbTag = generate_tag_class(db, tags_tasks_table)

        users_tasks_table = db.Table(
            'users_tasks',
            db.Column('user_id', db.Integer, db.ForeignKey('user.id'),
                      index=True),
            db.Column('task_id', db.Integer, db.ForeignKey('task.id'),
                      index=True))
        self.users_tasks_table = users_tasks_table

        task_dependencies_table = db.Table(
            'task_dependencies',
            db.Column('dependee_id', db.Integer, db.ForeignKey('task.id'),
                      primary_key=True),
            db.Column('dependant_id', db.Integer, db.ForeignKey('task.id'),
                      primary_key=True))
        self.task_dependencies_table = task_dependencies_table

        task_prioritize_table = db.Table(
            'task_prioritize',
            db.Column('prioritize_before_id', db.Integer,
                      db.ForeignKey('task.id'), primary_key=True),
            db.Column('prioritize_after_id', db.Integer,
                      db.ForeignKey('task.id'), primary_key=True))
        self.task_prioritize_table = task_prioritize_table

        self.DbTask = generate_task_class(self, tags_tasks_table,
                                          users_tasks_table,
                                          task_dependencies_table,
                                          task_prioritize_table)
        self.DbNote = generate_note_class(db)
        self.DbAttachment = generate_attachment_class(db)
        self.DbUser = generate_user_class(db, users_tasks_table)
        self.DbOption = generate_option_class(db)

        self._db_by_domain = {}
        self._domain_by_db = {}

    def add(self, domobj):
        self._logger.debug(u'begin, domobj: %s', domobj)
        if domobj in self._deleted_objects:
            raise Exception(
                'The object has already been set to be deleted: {}'.format(
                    domobj))
        if domobj in self._added_objects or domobj in self._changed_objects:
            # silently ignore
            return
        if domobj in self._committed_objects:
            # silently ignore
            return

        dbobj = self._get_db_object_from_domain_object_in_cache(domobj)
        if dbobj is None:
            dbobj = self._create_db_object_from_domain_object(domobj)
        self._logger.debug(u'dbobj: %s', dbobj)

        self._update_db_object_from_domain_object(domobj)

        self._register_domain_object(domobj)
        self._added_objects.add(domobj)
        self._changed_objects.add(domobj)

        self.db.session.add(dbobj)
        self._logger.debug(u'end')

    def delete(self, domobj):
        self._logger.debug(u'begin, domobj: %s', domobj)
        if domobj in self._added_objects:
            raise Exception(
                'The object has been added but not yet committed: {}'.format(
                    domobj))
        dbobj = self._get_db_object_from_domain_object_in_cache(domobj)
        if dbobj is None:
            dbobj = self._get_db_object_from_domain_object_by_id(domobj)
            if dbobj is None:
                raise Exception(
                    'Untracked domain object: {} ({})'.format(domobj,
                                                              type(domobj)))
        self._logger.debug(u'begin, dbobj: %s', dbobj)
        if domobj not in self._changed_objects_original_values:
            self._changed_objects_original_values[domobj] = domobj.to_dict()
        self._deleted_objects.add(domobj)

        domobj.clear_relationships()
        self.db.session.delete(dbobj)
        self._logger.debug(u'end')

    def commit(self):
        self._logger.debug(u'begin')

        added = list(self._added_objects)
        deleted = list(self._deleted_objects)

        self._clear_affected_objects()

        for domobj in deleted:
            domobj.clear_relationships()
        self._committed_objects.difference_update(deleted)

        ###############
        self._logger.debug(u'committing the db session/transaction')
        self.db.session.commit()
        self._logger.debug(u'committed the db session/transaction')
        ###############

        for domobj in added:
            self._update_domain_object_from_db_object(domobj)
        self._committed_objects.update(added)

        self._clear_affected_objects()

        self._logger.debug(u'end')

    def rollback(self):
        self._logger.debug(u'begin')
        self.db.session.rollback()
        original_values = self._changed_objects_original_values.copy()
        for domobj, d in original_values.iteritems():
            self._update_domain_object_from_dict(domobj, d)
        deleted = list(self._deleted_objects)
        for domobj in deleted:
            self._update_domain_object_from_db_object(domobj)
        self._clear_affected_objects()
        self._logger.debug(u'end')

    def _clear_affected_objects(self):
        self._changed_objects.clear()
        self._added_objects.clear()
        self._deleted_objects.clear()
        self._changed_objects_original_values.clear()

    def _is_db_object(self, obj):
        return isinstance(obj, self.db.Model)

    def _is_domain_object(self, obj):
        return isinstance(obj,
                          (Attachment, Task, Tag,
                           Note, User, Option))

    def _get_db_object_from_domain_object(self, domobj):
        self._logger.debug(u'begin, domobj: %s', domobj)
        if not self._is_domain_object(domobj):
            raise Exception(
                'Not a domain object: {} ({})'.format(domobj, type(domobj)))
        dbobj = self._get_db_object_from_domain_object_in_cache(domobj)
        if dbobj is None and domobj.id is not None:
            dbobj = self._get_db_object_from_domain_object_by_id(domobj)
        if dbobj is None:
            dbobj = self._create_db_object_from_domain_object(domobj)
        self._logger.debug(u'end')
        return dbobj

    def _get_db_object_from_domain_object_in_cache(self, domobj):
        self._logger.debug(u'begin, domobj: %s', domobj)
        if domobj is None:
            raise ValueError('domobj cannot be None')
        if not self._is_domain_object(domobj):
            raise Exception(
                'Not a domain object: {} ({})'.format(domobj, type(domobj)))

        if domobj not in self._db_by_domain:
            self._logger.debug(u'end (domobj not in cache)')
            return None

        self._logger.debug(u'end')
        return self._db_by_domain[domobj]

    def _get_db_object_from_domain_object_by_id(self, domobj):
        self._logger.debug(u'begin, domobj: %s', domobj)
        if domobj is None:
            raise ValueError('domobj cannot be None')
        if not self._is_domain_object(domobj):
            raise Exception(
                'Not a domain object: {} ({})'.format(domobj, type(domobj)))

        if domobj.id is None:
            self._logger.debug(u'end (domobj.id is None)')
            return None

        if isinstance(domobj, Attachment):
            dbobj = self._get_db_attachment(domobj.id)
        elif isinstance(domobj, Note):
            dbobj = self._get_db_note(domobj.id)
        elif isinstance(domobj, Option):
            dbobj = self._get_db_option(domobj.id)
        elif isinstance(domobj, Tag):
            dbobj = self._get_db_tag(domobj.id)
        elif isinstance(domobj, Task):
            dbobj = self._get_db_task(domobj.id)
        else:  # isinstance(domobj, User):
            # _is_domain_object above means domobj can't be any other type
            dbobj = self._get_db_user(domobj.id)

        if dbobj is not None:
            self._logger.debug(u'dbobj is not None')
            self._domain_by_db[dbobj] = domobj
            self._db_by_domain[domobj] = dbobj

        self._logger.debug(u'end')
        return dbobj

    def _create_db_object_from_domain_object(self, domobj):
        self._logger.debug(u'begin, domobj: %s', domobj)
        if domobj is None:
            raise ValueError('domobj cannot be None')
        if not self._is_domain_object(domobj):
            raise Exception(
                'Not a domain object: {} ({})'.format(domobj, type(domobj)))
        if domobj in self._db_by_domain:
            raise Exception(
                'Cannot create a new DB object; the domain object is already '
                'in the cache: {} ({})'.format(domobj, type(domobj)))

        if isinstance(domobj, Attachment):
            dbclass = self.DbAttachment
        elif isinstance(domobj, Note):
            dbclass = self.DbNote
        elif isinstance(domobj, Option):
            dbclass = self.DbOption
        elif isinstance(domobj, Tag):
            dbclass = self.DbTag
        elif isinstance(domobj, Task):
            dbclass = self.DbTask
        else:  # isinstance(domobj, User):
            # _is_domain_object above means domobj can't be any other type
            dbclass = self.DbUser

        domattrs = domobj.to_dict()
        dbattrs_nonrel = self._db_attrs_from_domain_no_links(domattrs)
        dbobj = dbclass.from_dict(dbattrs_nonrel)

        self._domain_by_db[dbobj] = domobj
        self._db_by_domain[domobj] = dbobj

        # translate the relational attributes after storing the dbobj in the
        # cache. otherwise, graph cycles lead to infinite recursion trying to
        # continually create new db objects.
        dbattrs_rel = self._db_attrs_from_domain_links(domattrs)
        dbobj.update_from_dict(dbattrs_rel)

        self._logger.debug(u'end')
        return dbobj

    def _get_domain_object_from_db_object(self, dbobj):
        self._logger.debug(u'begin, dbobj: %s', dbobj)
        if dbobj is None:
            return None
        if not self._is_db_object(dbobj):
            raise Exception(
                'Not a db object: {} ({})'.format(dbobj, type(dbobj)))

        domobj = self._get_domain_object_from_db_object_in_cache(dbobj)
        if domobj is None:
            domobj = self._create_domain_object_from_db_object(dbobj)

        self._logger.debug(u'end')
        return domobj

    def _get_domain_object_from_db_object_in_cache(self, dbobj):
        self._logger.debug(u'begin, dbobj: %s', dbobj)
        if dbobj is None:
            raise ValueError('dbobj cannot be None')
        if not self._is_db_object(dbobj):
            raise Exception(
                'Not a db object: {} ({})'.format(dbobj, type(dbobj)))

        if dbobj not in self._domain_by_db:
            self._logger.debug(u'end (dbobj not in cache)')
            return None

        self._logger.debug(u'end')
        return self._domain_by_db[dbobj]

    def _create_domain_object_from_db_object(self, dbobj):
        self._logger.debug(u'begin, dbobj: %s', dbobj)
        if dbobj is None:
            raise ValueError('dbobj cannot be None')
        if not self._is_db_object(dbobj):
            raise Exception(
                'Not a db object: {} ({})'.format(dbobj, type(dbobj)))
        if dbobj in self._domain_by_db:
            raise Exception(
                'Cannot create a new domain object; the DB object is already '
                'in the cache: {} ({})'.format(dbobj, type(dbobj)))

        if isinstance(dbobj, self.DbAttachment):
            domclass = Attachment
        elif isinstance(dbobj, self.DbTask):
            domclass = Task
        elif isinstance(dbobj, self.DbTag):
            domclass = Tag
        elif isinstance(dbobj, self.DbNote):
            domclass = Note
        elif isinstance(dbobj, self.DbUser):
            domclass = User
        else:  # isinstance(dbobj, self.DbOption):
            # _is_db_object above means dbobj can't be any other type
            domclass = Option

        dbattrs = dbobj.to_dict()
        domattrs_nonrel = self._domain_attrs_from_db_no_links(dbattrs)
        domattrs_rel = self._domain_attrs_from_db_links_lazy(dbattrs)

        # lazily load the relational attributes. this prevents graph cycles
        # from leading to infinite recursion trying to continually create new
        # domain objects. also prevents loading the entire object graph when
        # all we need is one object.
        domobj = domclass.from_dict(domattrs_nonrel, lazy=domattrs_rel)
        self._register_domain_object(domobj)

        self._domain_by_db[dbobj] = domobj
        self._db_by_domain[domobj] = dbobj

        self._logger.debug(u'end')
        return domobj

    def _domain_attrs_from_db_all(self, d):
        if d is None:
            raise ValueError('d must not be None')
        self._logger.debug(u'd: %s', d)
        d2 = {}
        self._domain_attrs_from_db_no_links(d, d2)
        self._domain_attrs_from_db_links(d, d2)
        self._logger.debug(u'd2: %s', d2)
        return d2

    def _domain_attrs_from_db_no_links(self, d, d2=None):
        if d is None:
            raise ValueError('d must not be None')
        self._logger.debug(u'd: %s', d)

        if d2 is None:
            d2 = {}

        for attrname in d.iterkeys():
            if attrname not in self._relational_attrs:
                d2[attrname] = d[attrname]

        self._logger.debug(u'd2: %s', d2)
        return d2

    def _domain_attrs_from_db_links(self, d, d2=None):
        if d is None:
            raise ValueError('d must not be None')
        # self._logger.debug(u'd: %s', d)
        if d2 is None:
            d2 = {}
        if 'parent' in d and d['parent'] is not None:
            d2['parent'] = self._get_domain_object_from_db_object(d['parent'])
        if 'children' in d and d['children'] is not None:
            d2['children'] = [self._get_domain_object_from_db_object(dbobj) for
                              dbobj in d['children']]
        if 'tags' in d and d['tags'] is not None:
            d2['tags'] = [self._get_domain_object_from_db_object(dbobj) for
                          dbobj in d['tags']]
        if 'tasks' in d and d['tasks'] is not None:
            d2['tasks'] = [self._get_domain_object_from_db_object(dbobj) for
                           dbobj in d['tasks']]
        if 'users' in d and d['users'] is not None:
            d2['users'] = [self._get_domain_object_from_db_object(dbobj) for
                           dbobj in d['users']]
        if 'dependees' in d and d['dependees'] is not None:
            d2['dependees'] = [self._get_domain_object_from_db_object(dbobj)
                               for dbobj in d['dependees']]
        if 'dependants' in d and d['dependants'] is not None:
            d2['dependants'] = [self._get_domain_object_from_db_object(dbobj)
                                for dbobj in d['dependants']]
        if 'prioritize_before' in d and d['prioritize_before'] is not None:
            d2['prioritize_before'] = [
                self._get_domain_object_from_db_object(dbobj) for dbobj in
                d['prioritize_before']]
        if 'prioritize_after' in d and d['prioritize_after'] is not None:
            d2['prioritize_after'] = [
                self._get_domain_object_from_db_object(dbobj) for dbobj in
                d['prioritize_after']]
        if 'notes' in d and d['notes'] is not None:
            d2['notes'] = [
                self._get_domain_object_from_db_object(dbobj) for dbobj in
                d['notes']]
        if 'attachments' in d and d['attachments'] is not None:
            d2['attachments'] = [
                self._get_domain_object_from_db_object(dbobj) for dbobj in
                d['attachments']]
        if 'task' in d and d['task'] is not None:
            d2['task'] = self._get_domain_object_from_db_object(d['task'])
        self._logger.debug(u'd2: %s', d2)
        return d2

    def _domain_attrs_from_db_links_lazy(self, d, d2=None):
        if d is None:
            raise ValueError('d must not be None')
        # self._logger.debug(u'd: %s', d)
        if d2 is None:
            d2 = {}
        if 'parent' in d and d['parent'] is not None:
            d2['parent'] = \
                lambda: self._get_domain_object_from_db_object(d['parent'])
        if 'children' in d and d['children'] is not None:
            d2['children'] = (self._get_domain_object_from_db_object(dbobj) for
                              dbobj in d['children'])
        if 'tags' in d and d['tags'] is not None:
            d2['tags'] = (self._get_domain_object_from_db_object(dbobj) for
                          dbobj in d['tags'])
        if 'tasks' in d and d['tasks'] is not None:
            d2['tasks'] = (self._get_domain_object_from_db_object(dbobj) for
                           dbobj in d['tasks'])
        if 'users' in d and d['users'] is not None:
            d2['users'] = (self._get_domain_object_from_db_object(dbobj) for
                           dbobj in d['users'])
        if 'dependees' in d and d['dependees'] is not None:
            d2['dependees'] = (self._get_domain_object_from_db_object(dbobj)
                               for dbobj in d['dependees'])
        if 'dependants' in d and d['dependants'] is not None:
            d2['dependants'] = (self._get_domain_object_from_db_object(dbobj)
                                for dbobj in d['dependants'])
        if 'prioritize_before' in d and d['prioritize_before'] is not None:
            d2['prioritize_before'] = (
                self._get_domain_object_from_db_object(dbobj) for dbobj in
                d['prioritize_before'])
        if 'prioritize_after' in d and d['prioritize_after'] is not None:
            d2['prioritize_after'] = (
                self._get_domain_object_from_db_object(dbobj) for dbobj in
                d['prioritize_after'])
        if 'notes' in d and d['notes'] is not None:
            d2['notes'] = (
                self._get_domain_object_from_db_object(dbobj) for dbobj in
                d['notes'])
        if 'attachments' in d and d['attachments'] is not None:
            d2['attachments'] = (
                self._get_domain_object_from_db_object(dbobj) for dbobj in
                d['attachments'])
        if 'task' in d and d['task'] is not None:
            d2['task'] = \
                lambda: self._get_domain_object_from_db_object(d['task'])
        self._logger.debug(u'd2: %s', d2)
        return d2

    def _update_domain_object_from_dict(self, domobj, d):
        self._logger.debug(u'begin, domobj: %s, d: %s', domobj, d)
        domobj.update_from_dict(d)
        self._logger.debug(u'end')

    def _update_domain_object_from_db_object(self, domobj, fields=None):
        if domobj is None:
            raise ValueError('domobj cannot be None')
        self._logger.debug(u'begin, domobj: %s, fields: %s', domobj, fields)
        dbobj = self._get_db_object_from_domain_object(domobj)
        self._logger.debug(u'got db obj %s -> %s', domobj, dbobj)
        d = dbobj.to_dict(fields)
        self._logger.debug(u'got db attrs %s -> %s', domobj, d)
        d = self._domain_attrs_from_db_all(d)
        self._logger.debug(u'got dom attrs %s -> %s', domobj, d)
        domobj.update_from_dict(d)
        self._logger.debug(u'updated dom obj %s -> %s', domobj, dbobj)
        self._logger.debug(u'end')

    _relational_attrs = {'parent', 'children', 'tags', 'tasks', 'users',
                         'dependees', 'dependants', 'prioritize_before',
                         'prioritize_after', 'notes', 'attachments', 'task'}

    def _db_attrs_from_domain_all(self, d):
        self._logger.debug(u'd: %s', d)
        d2 = {}
        self._db_attrs_from_domain_no_links(d, d2)
        self._db_attrs_from_domain_links(d, d2)
        self._logger.debug(u'd2: %s', d2)
        return d2

    def _db_attrs_from_domain_no_links(self, d, d2=None):
        self._logger.debug(u'd: %s', d)

        if d2 is None:
            d2 = {}

        for attrname in d.iterkeys():
            if attrname not in self._relational_attrs:
                d2[attrname] = d[attrname]

        self._logger.debug(u'd2: %s', d2)
        return d2

    def _db_attrs_from_domain_links(self, d, d2=None):
        self._logger.debug(u'd: %s', d)
        if d2 is None:
            d2 = {}
        if 'parent' in d and d['parent'] is not None:
            d2['parent'] = self._get_db_object_from_domain_object(d['parent'])
        if 'children' in d:
            d2['children'] = [self._get_db_object_from_domain_object(domobj)
                              for domobj in d['children']]
        if 'tags' in d:
            d2['tags'] = [self._get_db_object_from_domain_object(domobj) for
                          domobj in d['tags']]
        if 'tasks' in d:
            d2['tasks'] = [self._get_db_object_from_domain_object(domobj) for
                           domobj in d['tasks']]
        if 'task' in d and d['task'] is not None:
            d2['task'] = self._get_db_object_from_domain_object(d['task'])
        if 'users' in d:
            d2['users'] = [self._get_db_object_from_domain_object(domobj) for
                           domobj in d['users']]
        if 'dependees' in d:
            d2['dependees'] = [self._get_db_object_from_domain_object(domobj)
                               for domobj in d['dependees']]
        if 'dependants' in d:
            d2['dependants'] = [self._get_db_object_from_domain_object(domobj)
                                for domobj in d['dependants']]
        if 'prioritize_before' in d:
            d2['prioritize_before'] = [
                self._get_db_object_from_domain_object(domobj) for domobj in
                d['prioritize_before']]
        if 'prioritize_after' in d:
            d2['prioritize_after'] = [
                self._get_db_object_from_domain_object(domobj) for domobj in
                d['prioritize_after']]
        if 'notes' in d:
            d2['notes'] = [
                self._get_db_object_from_domain_object(domobj) for domobj in
                d['notes']]
        if 'attachments' in d:
            d2['attachments'] = [
                self._get_db_object_from_domain_object(domobj) for domobj in
                d['attachments']]
        self._logger.debug(u'd2: %s', d2)
        return d2

    def _db_value_from_domain(self, field, value):
        if value is None:
            return None
        if field in ('PARENT', 'CHILDREN', 'TAGS', 'TASKS', 'USERS',
                     'DEPENDEES', 'DEPENDANTS', 'PRIORITIZE_BEFORE',
                     'PRIORITIZE_AFTER', 'NOTES', 'ATTACHMENTS'):
            return self._get_db_object_from_domain_object(value)
        return value

    def _update_db_object_from_domain_object(self, domobj, fields=None):
        if domobj is None:
            raise ValueError('domobj cannot be None')
        self._logger.debug(u'begin, domobj: %s, fields: %s', domobj, fields)
        dbobj = self._get_db_object_from_domain_object(domobj)
        self._logger.debug(u'got db obj %s -> %s', domobj, dbobj)
        d = domobj.to_dict(fields)
        self._logger.debug(u'got dom attrs %s -> %s', domobj, d)
        d = self._db_attrs_from_domain_all(d)
        self._logger.debug(u'got db attrs %s -> %s', domobj, d)
        dbobj.update_from_dict(d)
        self._logger.debug(u'updated db obj %s -> %s', domobj, dbobj)
        self._logger.debug(u'end')

    def _on_domain_object_attr_changing(self, domobj, field, value):
        self._logger.debug(u'begin, domobj: %s, field: %s, value: %s',
                           domobj, field, value)
        if domobj not in self._changed_objects_original_values:
            self._changed_objects_original_values[domobj] = domobj.to_dict()
        self._logger.debug(u'end')

    def _on_domain_object_attr_changed(self, domobj, field, operation, value):
        self._logger.debug(u'begin, domobj: %s, field: %s, op: %s, value: %s',
                           domobj, field, operation, value)

        dbobj = self._get_db_object_from_domain_object(domobj)
        value2 = self._db_value_from_domain(field, value)
        dbobj.make_change(field, operation, value2)

        self._logger.debug(u'end')

    def _register_domain_object(self, domobj):
        self._logger.debug(u'begin, domobj: %s', domobj)
        domobj.register_changing_listener(self._on_domain_object_attr_changing)
        domobj.register_changed_listener(self._on_domain_object_attr_changed)
        self._logger.debug(u'end')

    def create_all(self):
        self.db.create_all()

    UNSPECIFIED = object()

    ASCENDING = object()
    DESCENDING = object()

    TASK_ID = object()
    ORDER_NUM = object()
    DEADLINE = object()

    def get_db_field_by_order_field(self, f):
        if f is self.ORDER_NUM:
            return self.DbTask.order_num
        if f is self.TASK_ID:
            return self.DbTask.id
        if f is self.DEADLINE:
            return self.DbTask.deadline
        raise Exception('Unhandled order_by field: {}'.format(f))

    @property
    def task_query(self):
        return self.DbTask.query

    def get_task(self, task_id):
        return self._get_domain_object_from_db_object(
            self._get_db_task(task_id))

    def _get_db_task(self, task_id):
        if task_id is None:
            return None
        return self.task_query.get(task_id)

    def _get_tasks_query(self, is_done=UNSPECIFIED, is_deleted=UNSPECIFIED,
                         parent_id=UNSPECIFIED, parent_id_in=UNSPECIFIED,
                         users_contains=UNSPECIFIED, task_id_in=UNSPECIFIED,
                         task_id_not_in=UNSPECIFIED,
                         deadline_is_not_none=False, tags_contains=UNSPECIFIED,
                         is_public=UNSPECIFIED,
                         is_public_or_users_contains=UNSPECIFIED,
                         summary_description_search_term=UNSPECIFIED,
                         order_num_greq_than=UNSPECIFIED,
                         order_num_lesseq_than=UNSPECIFIED,
                         order_by=UNSPECIFIED, limit=UNSPECIFIED):

        """order_by is a list of order directives. Each such directive is
         either a field (e.g. ORDER_NUM) or a sequence of field and direction
          (e.g. [ORDER_NUM, ASCENDING]). Default direction is ASCENDING if not
           specified."""

        query = self.task_query

        if is_done is not self.UNSPECIFIED:
            query = query.filter_by(is_done=is_done)

        if is_deleted is not self.UNSPECIFIED:
            query = query.filter_by(is_deleted=is_deleted)

        if is_public is not self.UNSPECIFIED:
            query = query.filter_by(is_public=is_public)

        if parent_id is not self.UNSPECIFIED:
            if parent_id is None:
                query = query.filter(self.DbTask.parent_id.is_(None))
            else:
                query = query.filter_by(parent_id=parent_id)

        if parent_id_in is not self.UNSPECIFIED:
            if parent_id_in:
                query = query.filter(self.DbTask.parent_id.in_(parent_id_in))
            else:
                # avoid performance penalty
                query = query.filter(False)

        if users_contains is not self.UNSPECIFIED:
            users_contains2 = self._get_db_object_from_domain_object(
                users_contains)
            query = query.filter(self.DbTask.users.contains(users_contains2))

        if is_public_or_users_contains is not self.UNSPECIFIED:
            db_user = self._get_db_object_from_domain_object(
                is_public_or_users_contains)
            query_m1 = query.outerjoin(
                self.users_tasks_table,
                self.users_tasks_table.c.task_id == self.DbTask.id)
            query_m2 = query_m1.filter(
                or_(
                    self.users_tasks_table.c.user_id == db_user.id,
                    self.DbTask.is_public
                )
            )
            query = query_m2

        if task_id_in is not self.UNSPECIFIED:
            # Using in_ on an empty set works but is expensive for some db
            # engines. In the case of an empty collection, just use a query
            # that always returns an empty set, without the performance
            # penalty.
            if task_id_in:
                query = query.filter(self.DbTask.id.in_(task_id_in))
            else:
                query = query.filter(False)

        if task_id_not_in is not self.UNSPECIFIED:
            # Using notin_ on an empty set works but is expensive for some db
            # engines. Moreover, it doesn't affect the actual set of selected
            # rows. In the case of an empty collection, just use the same query
            # object again, so we won't incur the performance penalty.
            if task_id_not_in:
                query = query.filter(self.DbTask.id.notin_(task_id_not_in))
            else:
                query = query

        if deadline_is_not_none:
            query = query.filter(self.DbTask.deadline.isnot(None))

        if tags_contains is not self.UNSPECIFIED:
            tags_contains2 = self._get_db_object_from_domain_object(
                tags_contains)
            query = query.filter(self.DbTask.tags.contains(tags_contains2))

        if summary_description_search_term is not self.UNSPECIFIED:
            like_term = '%{}%'.format(summary_description_search_term)
            query = query.filter(
                self.DbTask.summary.like(like_term) |
                self.DbTask.description.like(like_term))

        if order_num_greq_than is not self.UNSPECIFIED:
            query = query.filter(self.DbTask.order_num >= order_num_greq_than)

        if order_num_lesseq_than is not self.UNSPECIFIED:
            query = query.filter(self.DbTask.order_num <=
                                 order_num_lesseq_than)

        if order_by is not self.UNSPECIFIED:
            if not is_iterable(order_by):
                db_field = self.get_db_field_by_order_field(order_by)
                query = query.order_by(db_field)
            else:
                for ordering in order_by:
                    direction = self.ASCENDING
                    if is_iterable(ordering):
                        order_field = ordering[0]
                        if len(ordering) > 1:
                            direction = ordering[1]
                    else:
                        order_field = ordering
                    db_field = self.get_db_field_by_order_field(order_field)
                    if direction is self.ASCENDING:
                        query = query.order_by(db_field.asc())
                    elif direction is self.DESCENDING:
                        query = query.order_by(db_field.desc())
                    else:
                        raise Exception(
                            'Unknown order_by direction: {}'.format(direction))

        if limit is not self.UNSPECIFIED:
            query = query.limit(limit)

        return query

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
        query = self._get_tasks_query(
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
        return (self._get_domain_object_from_db_object(_) for _ in query)

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

        query = self._get_tasks_query(
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
        pager = query.paginate(page=page_num, per_page=tasks_per_page)
        items = list(self._get_domain_object_from_db_object(item) for item in
                     pager.items)
        return Pager(page=pager.page, per_page=pager.per_page,
                     items=items, total=pager.total,
                     num_pages=pager.pages, _pager=pager)

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
        return self._get_tasks_query(
            is_done=is_done, is_deleted=is_deleted, parent_id=parent_id,
            parent_id_in=parent_id_in, users_contains=users_contains,
            task_id_in=task_id_in, task_id_not_in=task_id_not_in,
            deadline_is_not_none=deadline_is_not_none,
            tags_contains=tags_contains, is_public=is_public,
            is_public_or_users_contains=is_public_or_users_contains,
            summary_description_search_term=summary_description_search_term,
            order_num_greq_than=order_num_greq_than,
            order_num_lesseq_than=order_num_lesseq_than, order_by=order_by,
            limit=limit).count()

    @property
    def tag_query(self):
        return self.DbTag.query

    def _get_db_tag(self, tag_id):
        if tag_id is None:
            raise ValueError('tag_id cannot be None')
        return self.tag_query.get(tag_id)

    def get_tag(self, tag_id):
        if tag_id is None:
            raise ValueError('tag_id cannot be None')
        return self._get_domain_object_from_db_object(self._get_db_tag(tag_id))

    def _get_tags_query(self, value=UNSPECIFIED, limit=None):
        query = self.DbTag.query
        if value is not self.UNSPECIFIED:
            query = query.filter_by(value=value)
        if limit is not None:
            query = query.limit(limit)
        return query

    def get_tags(self, value=UNSPECIFIED, limit=None):
        query = self._get_tags_query(value=value, limit=limit)
        return (self._get_domain_object_from_db_object(_) for _ in query)

    def count_tags(self, value=UNSPECIFIED, limit=None):
        return self._get_tags_query(value=value, limit=limit).count()

    def get_tag_by_value(self, value):
        return self._get_domain_object_from_db_object(
            self._get_tags_query(value=value).first())

    @property
    def note_query(self):
        return self.DbNote.query

    def _get_db_note(self, note_id):
        if note_id is None:
            raise ValueError('note_id acannot be None')
        return self.note_query.get(note_id)

    def get_note(self, note_id):
        if note_id is None:
            raise ValueError('note_id acannot be None')
        return self._get_domain_object_from_db_object(
            self._get_db_note(note_id))

    def _get_notes_query(self, note_id_in=UNSPECIFIED):
        query = self.note_query
        if note_id_in is not self.UNSPECIFIED:
            if note_id_in:
                query = query.filter(self.DbNote.id.in_(note_id_in))
            else:
                # performance improvement
                query = query.filter(False)
        return query

    def get_notes(self, note_id_in=UNSPECIFIED):
        query = self._get_notes_query(note_id_in=note_id_in)
        return (self._get_domain_object_from_db_object(_) for _ in query)

    def count_notes(self, note_id_in=UNSPECIFIED):
        return self._get_notes_query(note_id_in=note_id_in).count()

    @property
    def attachment_query(self):
        return self.DbAttachment.query

    def _get_db_attachment(self, attachment_id):
        if attachment_id is None:
            raise ValueError('attachment_id acannot be None')
        return self.attachment_query.get(attachment_id)

    def get_attachment(self, attachment_id):
        if attachment_id is None:
            raise ValueError('attachment_id acannot be None')
        return self._get_domain_object_from_db_object(
            self._get_db_attachment(attachment_id))

    def _get_attachments_query(self, attachment_id_in=UNSPECIFIED):
        query = self.attachment_query
        if attachment_id_in is not self.UNSPECIFIED:
            if attachment_id_in:
                query = query.filter(
                    self.DbAttachment.id.in_(attachment_id_in))
            else:
                query = query.filter(False)
        return query

    def get_attachments(self, attachment_id_in=UNSPECIFIED):
        query = self._get_attachments_query(attachment_id_in=attachment_id_in)
        return (self._get_domain_object_from_db_object(_) for _ in query)

    def count_attachments(self, attachment_id_in=UNSPECIFIED):
        return self._get_attachments_query(
            attachment_id_in=attachment_id_in).count()

    @property
    def user_query(self):
        return self.DbUser.query

    def _get_db_user(self, user_id):
        if user_id is None:
            raise ValueError('user_id acannot be None')
        return self.user_query.get(user_id)

    def get_user(self, user_id):
        if user_id is None:
            raise ValueError('user_id acannot be None')
        return self._get_domain_object_from_db_object(
            self._get_db_user(user_id))

    def get_user_by_email(self, email):
        return self._get_domain_object_from_db_object(
            self.user_query.filter_by(email=email).first())

    def _get_users_query(self, email_in=UNSPECIFIED):
        query = self.user_query
        if email_in is not self.UNSPECIFIED:
            if email_in:
                query = query.filter(self.DbUser.email.in_(email_in))
            else:
                # avoid performance penalty
                query = query.filter(False)
        return query

    def get_users(self, email_in=UNSPECIFIED):
        query = self._get_users_query(email_in=email_in)
        return (self._get_domain_object_from_db_object(_) for _ in query)

    def count_users(self, email_in=UNSPECIFIED):
        return self._get_users_query(email_in=email_in).count()

    @property
    def option_query(self):
        return self.DbOption.query

    def _get_db_option(self, key):
        if key is None:
            raise ValueError('key acannot be None')
        return self.option_query.get(key)

    def get_option(self, key):
        if key is None:
            raise ValueError('key acannot be None')
        return self._get_domain_object_from_db_object(self._get_db_option(key))

    def _get_options_query(self, key_in=UNSPECIFIED):
        query = self.option_query
        if key_in is not self.UNSPECIFIED:
            if key_in:
                query = query.filter(self.DbOption.key.in_(key_in))
            else:
                # avoid performance penalty
                query = query.filter(False)
        return query

    def get_options(self, key_in=UNSPECIFIED):
        query = self._get_options_query(key_in=key_in)
        return (self._get_domain_object_from_db_object(_) for _ in query)

    def count_options(self, key_in=UNSPECIFIED):
        return self._get_options_query(key_in=key_in).count()