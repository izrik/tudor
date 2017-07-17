
import collections
import random
import logging

from flask_sqlalchemy import SQLAlchemy
from models.task import Task, TaskBase
from models.tag import Tag, TagBase
from models.note import Note, NoteBase
from models.attachment import Attachment, AttachmentBase
from models.user import User, UserBase
from models.option import Option, OptionBase
from collections_util import clear, extend
import logging_util
from models.changeable import id2, Changeable


def is_iterable(x):
    return isinstance(x, collections.Iterable)


def as_iterable(x):
    if is_iterable(x):
        return x
    return (x,)


class Pager(object):
    page = None
    per_page = None
    items = None
    total = None

    def __init__(self, page, per_page, items, total, num_pages, _pager):
        self.page = page
        self.per_page = per_page
        self.items = list(items)
        self.total = total
        self.num_pages = num_pages
        self._pager = _pager

    def iter_pages(self, left_edge=2, left_current=2, right_current=5,
                   right_edge=2):

        if (left_edge < 1 or left_current < 1 or right_current < 1 or
                right_edge < 1):
            raise ValueError('Parameter must be positive')

        total_pages = self.total / self.per_page
        if self.total % self.per_page > 0:
            total_pages += 1

        left_of_current = max(self.page - left_current, left_edge + 1)
        right_of_current = min(self.page + right_current,
                               total_pages - right_edge + 1)

        for i in xrange(left_edge):
            yield i + 1

        if left_of_current > left_edge + 1:
            yield None

        for i in xrange(left_of_current, right_of_current):
            yield i

        if right_of_current < total_pages - right_edge + 1:
            yield None

        for i in xrange(right_edge):
            yield total_pages - right_edge + i + 1

    @property
    def pages(self):
        return self.num_pages

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def prev_num(self):
        return self.page - 1

    @property
    def has_next(self):
        return self.page < self.num_pages

    @property
    def next_num(self):
        return self.page + 1


class PersistenceLayer(object):

    def __init__(self, app, db_uri, bcrypt):
        self._logger = logging_util.get_logger(__name__, self)

        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        self.db = SQLAlchemy(self.app)

        db = self.db
        self._added_objects = set()
        self._deleted_objects = set()
        self._changed_objects = set()
        self._changed_objects_original_values = {}
        self._fields_to_update_from_db_on_commit = {}

        tags_tasks_table = db.Table(
            'tags_tasks',
            db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'),
                      primary_key=True),
            db.Column('task_id', db.Integer, db.ForeignKey('task.id'),
                      primary_key=True))

        self.Tag = generate_tag_class(db, tags_tasks_table)

        users_tasks_table = db.Table(
            'users_tasks',
            db.Column('user_id', db.Integer, db.ForeignKey('user.id'),
                      index=True),
            db.Column('task_id', db.Integer, db.ForeignKey('task.id'),
                      index=True))

        task_dependencies_table = db.Table(
            'task_dependencies',
            db.Column('dependee_id', db.Integer, db.ForeignKey('task.id'),
                      primary_key=True),
            db.Column('dependant_id', db.Integer, db.ForeignKey('task.id'),
                      primary_key=True))

        task_prioritize_table = db.Table(
            'task_prioritize',
            db.Column('prioritize_before_id', db.Integer,
                      db.ForeignKey('task.id'), primary_key=True),
            db.Column('prioritize_after_id', db.Integer,
                      db.ForeignKey('task.id'), primary_key=True))

        self.Task = generate_task_class(self, tags_tasks_table,
                                        users_tasks_table,
                                        task_dependencies_table,
                                        task_prioritize_table)
        self.Note = generate_note_class(db)
        self.Attachment = generate_attachment_class(db)
        self.User = generate_user_class(db, bcrypt)
        self.Option = generate_option_class(db)

        self._db_by_domain = {}
        self._domain_by_db = {}

    def _get_fields_to_update_for_domobj(self, domobj):
        if domobj not in self._fields_to_update_from_db_on_commit:
            self._fields_to_update_from_db_on_commit[domobj] = set()
        return self._fields_to_update_from_db_on_commit[domobj]

    def add(self, domobj):
        self._logger.debug('begin, domobj: {}'.format(domobj))
        if domobj in self._deleted_objects:
            raise Exception(
                'The object has already been set to be deleted: {}'.format(
                    domobj))
        if domobj in self._added_objects or domobj in self._changed_objects:
            # silently ignore
            return

        dbobj = self._get_db_object_from_domain_object_in_cache(domobj)
        if dbobj is None:
            dbobj = self._create_db_object_from_domain_object(domobj)
        self._logger.debug('dbobj: {}'.format(dbobj))

        self._update_db_object_from_domain_object(domobj)

        self._register_domain_object(domobj)
        self._added_objects.add(domobj)
        self._changed_objects.add(domobj)

        fields_to_update = self._get_fields_to_update_for_domobj(domobj)
        fields_to_update.update(domobj.get_autochange_fields())

        self.db.session.add(dbobj)
        self._logger.debug('end')

    def delete(self, domobj):
        self._logger.debug('begin, domobj: {}'.format(domobj))
        dbobj = self._get_db_object_from_domain_object_in_cache(domobj)
        if dbobj is None:
            dbobj = self._get_db_object_from_domain_object_by_id(domobj)
            if dbobj is None:
                raise Exception(
                    'Untracked domain object: {} ({})'.format(domobj,
                                                              type(domobj)))
        self._logger.debug('begin, dbobj: {}'.format(dbobj))
        if domobj not in self._changed_objects_original_values:
            self._changed_objects_original_values[domobj] = domobj.to_dict()
        self._deleted_objects.add(domobj)

        domobj.clear_relationships()
        self.db.session.delete(dbobj)
        self._logger.debug('end')

    def commit(self):
        self._logger.debug('begin')

        added = list(self._added_objects)
        deleted = list(self._deleted_objects)
        fields_to_update = self._fields_to_update_from_db_on_commit.copy()

        self._clear_affected_objects()

        for domobj in deleted:
            domobj.clear_relationships()

        ###############
        self._logger.debug('committing the db session/transaction')
        self.db.session.commit()
        self._logger.debug('committed the db session/transaction')
        ###############

        for domobj in added:
            self._update_domain_object_from_db_object(domobj)

        for domobj, fields in fields_to_update.iteritems():
            self._update_domain_object_from_db_object(domobj, fields)

        self._clear_affected_objects()

        self._logger.debug('end')

    def rollback(self):
        self._logger.debug('begin')
        self.db.session.rollback()
        original_values = self._changed_objects_original_values.copy()
        for domobj, d in original_values.iteritems():
            self._update_domain_object_from_dict(domobj, d)
        deleted = list(self._deleted_objects)
        for domobj in deleted:
            self._update_domain_object_from_db_object(domobj)
        self._clear_affected_objects()
        self._logger.debug('end')

    def _clear_affected_objects(self):
        self._changed_objects.clear()
        self._added_objects.clear()
        self._deleted_objects.clear()
        self._changed_objects_original_values.clear()
        self._fields_to_update_from_db_on_commit.clear()

    def _is_db_object(self, obj):
        return isinstance(obj, self.db.Model)

    def _is_domain_object(self, obj):
        return isinstance(obj,
                          (Attachment, Task, Tag,
                           Note, User, Option))

    def _get_db_object_from_domain_object(self, domobj):
        self._logger.debug('begin, domobj: {}'.format(domobj))
        if not self._is_domain_object(domobj):
            raise Exception(
                'Not a domain object: {} ({})'.format(domobj, type(domobj)))
        dbobj = self._get_db_object_from_domain_object_in_cache(domobj)
        if dbobj is None and domobj.id is not None:
            dbobj = self._get_db_object_from_domain_object_by_id(domobj)
        if dbobj is None:
            dbobj = self._create_db_object_from_domain_object(domobj)
        self._logger.debug('end')
        return dbobj

    def _get_db_object_from_domain_object_in_cache(self, domobj):
        self._logger.debug('begin, domobj: {}'.format(domobj))
        if domobj is None:
            raise ValueError('domobj cannot be None')
        if not self._is_domain_object(domobj):
            raise Exception(
                'Not a domain object: {} ({})'.format(domobj, type(domobj)))

        if domobj not in self._db_by_domain:
            self._logger.debug('end (domobj not in cache)')
            return None

        self._logger.debug('end')
        return self._db_by_domain[domobj]

    def _get_db_object_from_domain_object_by_id(self, domobj):
        self._logger.debug('begin, domobj: {}'.format(domobj))
        if domobj is None:
            raise ValueError('domobj cannot be None')
        if not self._is_domain_object(domobj):
            raise Exception(
                'Not a domain object: {} ({})'.format(domobj, type(domobj)))

        if domobj.id is None:
            self._logger.debug('end (domobj.id is None)')
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
        elif isinstance(domobj, User):
            dbobj = self._get_db_user(domobj.id)
        else:
            raise Exception(
                'Unknown domain object: {} ({})'.format(domobj, type(domobj)))

        if dbobj is not None:
            self._logger.debug('dbobj is not None')
            self._domain_by_db[dbobj] = domobj
            self._db_by_domain[domobj] = dbobj
            if hasattr(domobj, '_dbobj'):
                domobj._dbobj = dbobj
                dbobj._domobj = domobj

        self._logger.debug('end')
        return dbobj

    def _create_db_object_from_domain_object(self, domobj):
        self._logger.debug('begin, domobj: {}'.format(domobj))
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
            dbclass = self.Attachment
        elif isinstance(domobj, Note):
            dbclass = self.Note
        elif isinstance(domobj, Option):
            dbclass = self.Option
        elif isinstance(domobj, Tag):
            dbclass = self.Tag
        elif isinstance(domobj, Task):
            dbclass = self.Task
        elif isinstance(domobj, User):
            dbclass = self.User
        else:
            raise Exception('Unknown domain object: {} ({})'.format(
                domobj, type(domobj)))

        domattrs = domobj.to_dict()
        dbattrs_nonrel = self._db_attrs_from_domain_no_links(domattrs)
        dbobj = dbclass.from_dict(dbattrs_nonrel)

        self._domain_by_db[dbobj] = domobj
        self._db_by_domain[domobj] = dbobj
        if hasattr(domobj, '_dbobj'):
            domobj._dbobj = dbobj
            dbobj._domobj = domobj

        # translate the relational attributes after storing the dbobj in the
        # cache. otherwise, graph cycles lead to infinite recursion trying to
        # continually create new db objects.
        dbattrs_rel = self._db_attrs_from_domain_links(domattrs)
        dbobj.update_from_dict(dbattrs_rel)

        self._logger.debug('end')
        return dbobj

    def _get_domain_object_from_db_object(self, dbobj):
        self._logger.debug('begin, dbobj: {}'.format(dbobj))
        if dbobj is None:
            return None
        if not self._is_db_object(dbobj):
            raise Exception(
                'Not a db object: {} ({})'.format(dbobj, type(dbobj)))

        domobj = self._get_domain_object_from_db_object_in_cache(dbobj)
        if domobj is None:
            domobj = self._create_domain_object_from_db_object(dbobj)

        self._logger.debug('end')
        return domobj

    def _get_domain_object_from_db_object_in_cache(self, dbobj):
        self._logger.debug('begin, dbobj: {}'.format(dbobj))
        if dbobj is None:
            raise ValueError('dbobj cannot be None')
        if not self._is_db_object(dbobj):
            raise Exception(
                'Not a db object: {} ({})'.format(dbobj, type(dbobj)))

        if dbobj not in self._domain_by_db:
            self._logger.debug('end (dbobj not in cache)')
            return None

        self._logger.debug('end')
        return self._domain_by_db[dbobj]

    def _create_domain_object_from_db_object(self, dbobj):
        self._logger.debug('begin, dbobj: {}'.format(dbobj))
        if dbobj is None:
            raise ValueError('dbobj cannot be None')
        if not self._is_db_object(dbobj):
            raise Exception(
                'Not a db object: {} ({})'.format(dbobj, type(dbobj)))
        if dbobj in self._domain_by_db:
            raise Exception(
                'Cannot create a new domain object; the DB object is already '
                'in the cache: {} ({})'.format(dbobj, type(dbobj)))

        if isinstance(dbobj, self.Attachment):
            domclass = Attachment
        elif isinstance(dbobj, self.Task):
            domclass = Task
        elif isinstance(dbobj, self.Tag):
            domclass = Tag
        elif isinstance(dbobj, self.Note):
            domclass = Note
        elif isinstance(dbobj, self.User):
            domclass = User
        elif isinstance(dbobj, self.Option):
            domclass = Option
        else:
            raise Exception(
                'Unknown db object type: {}, {}'.format(dbobj, type(dbobj)))

        attrs = dbobj.to_dict()
        attrs = self._domain_attrs_from_db(attrs)
        domobj = domclass.from_dict(attrs)

        self._domain_by_db[dbobj] = domobj
        self._db_by_domain[domobj] = dbobj
        if hasattr(domobj, '_dbobj'):
            domobj._dbobj = dbobj
            dbobj._domobj = domobj

        self._logger.debug('end')
        return domobj

    def _domain_attrs_from_db(self, d):
        self._logger.debug('d: {}'.format(d))
        d2 = d.copy()
        if 'parent' in d2 and d2['parent'] is not None:
            d2['parent'] = self._get_domain_object_from_db_object(d2['parent'])
        if 'children' in d2 and d2['children'] is not None:
            d2['children'] = [self._get_domain_object_from_db_object(dbobj) for
                              dbobj in d2['children']]
        if 'tags' in d2 and d2['tags'] is not None:
            d2['tags'] = [self._get_domain_object_from_db_object(dbobj) for
                          dbobj in d2['tags']]
        if 'tasks' in d2 and d2['tasks'] is not None:
            d2['tasks'] = [self._get_domain_object_from_db_object(dbobj) for
                           dbobj in d2['tasks']]
        if 'users' in d2 and d2['users'] is not None:
            d2['users'] = [self._get_domain_object_from_db_object(dbobj) for
                           dbobj in d2['users']]
        if 'dependees' in d2 and d2['dependees'] is not None:
            d2['dependees'] = [self._get_domain_object_from_db_object(dbobj)
                               for dbobj in d2['dependees']]
        if 'dependants' in d2 and d2['dependants'] is not None:
            d2['dependants'] = [self._get_domain_object_from_db_object(dbobj)
                                for dbobj in d2['dependants']]
        if 'prioritize_before' in d2 and d2['prioritize_before'] is not None:
            d2['prioritize_before'] = [
                self._get_domain_object_from_db_object(dbobj) for dbobj in
                d2['prioritize_before']]
        if 'prioritize_after' in d2 and d2['prioritize_after'] is not None:
            d2['prioritize_after'] = [
                self._get_domain_object_from_db_object(dbobj) for dbobj in
                d2['prioritize_after']]
        if 'notes' in d2 and d2['notes'] is not None:
            d2['notes'] = [
                self._get_domain_object_from_db_object(dbobj) for dbobj in
                d2['notes']]
        if 'attachments' in d2 and d2['attachments'] is not None:
            d2['attachments'] = [
                self._get_domain_object_from_db_object(dbobj) for dbobj in
                d2['attachments']]
        self._logger.debug('d2: {}'.format(d2))
        return d2

    def _update_domain_object_from_dict(self, domobj, d):
        self._logger.debug(
            'begin, domobj: {}, d: {}'.format(domobj, d))
        domobj.update_from_dict(d)
        self._logger.debug('end')

    def _update_domain_object_from_db_object(self, domobj, fields=None):
        self._logger.debug(
            'begin, domobj: {}, fields: {}'.format(domobj, fields))
        dbobj = self._get_db_object_from_domain_object(domobj)
        self._logger.debug(
            'got db obj {} -> {}'.format(id2(domobj), id2(dbobj)))
        d = dbobj.to_dict(fields)
        self._logger.debug('got db attrs {} -> {}'.format(id2(domobj), d))
        d = self._domain_attrs_from_db(d)
        self._logger.debug('got dom attrs {} -> {}'.format(id2(domobj), d))
        domobj.update_from_dict(d)
        self._logger.debug(
            'updated dom obj {} -> {}'.format(id2(domobj), id2(dbobj)))
        self._logger.debug('end')

    _relational_attrs = {'parent', 'children', 'tags', 'tasks', 'users',
                         'dependees', 'dependants', 'prioritize_before',
                         'prioritize_after', 'notes', 'attachments'}

    def _db_attrs_from_domain_all(self, d):
        self._logger.debug('d: {}'.format(d))
        d2 = {}
        self._db_attrs_from_domain_no_links(d, d2)
        self._db_attrs_from_domain_links(d, d2)
        self._logger.debug('d2: {}'.format(d2))
        return d2

    def _db_attrs_from_domain_no_links(self, d, d2=None):
        self._logger.debug('d: {}'.format(d))

        if d2 is None:
            d2 = {}

        for attrname in d.iterkeys():
            if attrname not in self._relational_attrs:
                d2[attrname] = d[attrname]

        self._logger.debug('d2: {}'.format(d2))
        return d2

    def _db_attrs_from_domain_links(self, d, d2=None):
        self._logger.debug('d: {}'.format(d))
        if d2 is None:
            d2 = {}
        if 'parent' in d and d['parent'] is not None:
            d2['parent'] = self._get_db_object_from_domain_object(d['parent'])
        if 'parent_id' in d and d['parent_id'] is not None:
            d2['parent_id'] = d['parent_id']
        if 'children' in d:
            d2['children'] = [self._get_db_object_from_domain_object(domobj)
                              for domobj in d['children']]
        if 'tags' in d:
            d2['tags'] = [self._get_db_object_from_domain_object(domobj) for
                          domobj in d['tags']]
        if 'tasks' in d:
            d2['tasks'] = [self._get_db_object_from_domain_object(domobj) for
                           domobj in d['tasks']]
        if 'task_id' in d and d['task_id'] is not None:
            d2['task_id'] = d['task_id']
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
        self._logger.debug('d2: {}'.format(d2))
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
        self._logger.debug(
            'begin, domobj: {}, fields: {}'.format(domobj, fields))
        dbobj = self._get_db_object_from_domain_object(domobj)
        self._logger.debug(
            'got db obj {} -> {}'.format(id2(domobj), id2(dbobj)))
        d = domobj.to_dict(fields)
        self._logger.debug('got dom attrs {} -> {}'.format(id2(domobj), d))
        d = self._db_attrs_from_domain_all(d)
        self._logger.debug('got db attrs {} -> {}'.format(id2(domobj), d))
        dbobj.update_from_dict(d)
        self._logger.debug(
            'updated db obj {} -> {}'.format(id2(domobj), id2(dbobj)))
        self._logger.debug('end')

    def _on_domain_object_attr_changing(self, domobj, field, value):
        self._logger.debug(
            'begin, domobj: {}, field: {}, value: {}'.format(domobj, field,
                                                             value))
        if domobj not in self._changed_objects_original_values:
            self._changed_objects_original_values[domobj] = domobj.to_dict()
        self._logger.debug('end')

    def _on_domain_object_attr_changed(self, domobj, field, operation, value):
        self._logger.debug(
            'begin, domobj: {}, field: {}, op: {}, value: {}'.format(
                domobj, field, operation, value))

        fields_to_update = self._get_fields_to_update_for_domobj(domobj)
        related_fields = domobj.get_related_fields(field)
        fields_to_update.update(related_fields)

        dbobj = self._get_db_object_from_domain_object(domobj)
        value2 = self._db_value_from_domain(field, value)
        dbobj.make_change(field, operation, value2)

        self._logger.debug('end')

    def _register_domain_object(self, domobj):
        self._logger.debug('begin, domobj: {}'.format(domobj))
        domobj.register_changing_listener(self._on_domain_object_attr_changing)
        domobj.register_changed_listener(self._on_domain_object_attr_changed)
        self._logger.debug('end')

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
            return self.Task.order_num
        if f is self.TASK_ID:
            return self.Task.id
        if f is self.DEADLINE:
            return self.Task.deadline
        raise Exception('Unhandled order_by field: {}'.format(f))

    @property
    def task_query(self):
        return self.Task.query

    def get_task(self, task_id):
        return self._get_domain_object_from_db_object(
            self._get_db_task(task_id))

    def _get_db_task(self, task_id):
        return self.task_query.get(task_id)

    def _get_tasks_query(self, is_done=UNSPECIFIED, is_deleted=UNSPECIFIED,
                         parent_id=UNSPECIFIED, parent_id_in=UNSPECIFIED,
                         users_contains=UNSPECIFIED, task_id_in=UNSPECIFIED,
                         task_id_not_in=UNSPECIFIED,
                         deadline_is_not_none=False, tags_contains=UNSPECIFIED,
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

        if parent_id is not self.UNSPECIFIED:
            if parent_id is None:
                query = query.filter(self.Task.parent_id.is_(None))
            else:
                query = query.filter_by(parent_id=parent_id)

        if parent_id_in is not self.UNSPECIFIED:
            if parent_id_in:
                query = query.filter(self.Task.parent_id.in_(parent_id_in))
            else:
                # avoid performance penalty
                query = query.filter(False)

        if users_contains is not self.UNSPECIFIED:
            users_contains2 = self._get_db_object_from_domain_object(
                users_contains)
            query = query.filter(self.Task.users.contains(users_contains2))

        if task_id_in is not self.UNSPECIFIED:
            # Using in_ on an empty set works but is expensive for some db
            # engines. In the case of an empty collection, just use a query
            # that always returns an empty set, without the performance
            # penalty.
            if task_id_in:
                query = query.filter(self.Task.id.in_(task_id_in))
            else:
                query = query.filter(False)

        if task_id_not_in is not self.UNSPECIFIED:
            # Using notin_ on an empty set works but is expensive for some db
            # engines. Moreover, it doesn't affect the actual set of selected
            # rows. In the case of an empty collection, just use the same query
            # object again, so we won't incur the performance penalty.
            if task_id_not_in:
                query = query.filter(self.Task.id.notin_(task_id_not_in))
            else:
                query = query

        if deadline_is_not_none:
            query = query.filter(self.Task.deadline.isnot(None))

        if tags_contains is not self.UNSPECIFIED:
            tags_contains2 = self._get_db_object_from_domain_object(
                tags_contains)
            query = query.filter(self.Task.tags.contains(tags_contains2))

        if summary_description_search_term is not self.UNSPECIFIED:
            like_term = '%{}%'.format(summary_description_search_term)
            query = query.filter(
                self.Task.summary.like(like_term) |
                self.Task.description.like(like_term))

        if order_num_greq_than is not self.UNSPECIFIED:
            query = query.filter(self.Task.order_num >= order_num_greq_than)

        if order_num_lesseq_than is not self.UNSPECIFIED:
            query = query.filter(self.Task.order_num <= order_num_lesseq_than)

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
                  tags_contains=UNSPECIFIED,
                  summary_description_search_term=UNSPECIFIED,
                  order_num_greq_than=UNSPECIFIED,
                  order_num_lesseq_than=UNSPECIFIED, order_by=UNSPECIFIED,
                  limit=UNSPECIFIED):
        query = self._get_tasks_query(
            is_done=is_done, is_deleted=is_deleted, parent_id=parent_id,
            parent_id_in=parent_id_in, users_contains=users_contains,
            task_id_in=task_id_in, task_id_not_in=task_id_not_in,
            deadline_is_not_none=deadline_is_not_none,
            tags_contains=tags_contains,
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
                            tags_contains=UNSPECIFIED,
                            summary_description_search_term=UNSPECIFIED,
                            order_num_greq_than=UNSPECIFIED,
                            order_num_lesseq_than=UNSPECIFIED,
                            order_by=UNSPECIFIED, limit=UNSPECIFIED,
                            page_num=None, tasks_per_page=None):
        if page_num is None:
            page_num = 1
        if tasks_per_page is None:
            tasks_per_page = 20

        query = self._get_tasks_query(
            is_done=is_done, is_deleted=is_deleted, parent_id=parent_id,
            parent_id_in=parent_id_in, users_contains=users_contains,
            task_id_in=task_id_in, task_id_not_in=task_id_not_in,
            deadline_is_not_none=deadline_is_not_none,
            tags_contains=tags_contains,
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
                    tags_contains=UNSPECIFIED,
                    summary_description_search_term=UNSPECIFIED,
                    order_num_greq_than=UNSPECIFIED,
                    order_num_lesseq_than=UNSPECIFIED, order_by=UNSPECIFIED,
                    limit=UNSPECIFIED):
        return self._get_tasks_query(
            is_done=is_done, is_deleted=is_deleted, parent_id=parent_id,
            parent_id_in=parent_id_in, users_contains=users_contains,
            task_id_in=task_id_in, task_id_not_in=task_id_not_in,
            deadline_is_not_none=deadline_is_not_none,
            tags_contains=tags_contains,
            summary_description_search_term=summary_description_search_term,
            order_num_greq_than=order_num_greq_than,
            order_num_lesseq_than=order_num_lesseq_than, order_by=order_by,
            limit=limit).count()

    @property
    def tag_query(self):
        return self.Tag.query

    def _get_db_tag(self, tag_id):
        return self.tag_query.get(tag_id)

    def get_tag(self, tag_id):
        return self._get_domain_object_from_db_object(self._get_db_tag(tag_id))

    def _get_tags_query(self, value=UNSPECIFIED, limit=None):
        query = self.Tag.query
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
        return self.Note.query

    def _get_db_note(self, note_id):
        return self.note_query.get(note_id)

    def get_note(self, note_id):
        return self._get_domain_object_from_db_object(
            self._get_db_note(note_id))

    def _get_notes_query(self, note_id_in=UNSPECIFIED):
        query = self.note_query
        if note_id_in is not self.UNSPECIFIED:
            if note_id_in:
                query = query.filter(self.Note.id.in_(note_id_in))
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
        return self.Attachment.query

    def _get_db_attachment(self, attachment_id):
        return self.attachment_query.get(attachment_id)

    def get_attachment(self, attachment_id):
        return self._get_domain_object_from_db_object(
            self._get_db_attachment(attachment_id))

    def _get_attachments_query(self, attachment_id_in=UNSPECIFIED):
        query = self.attachment_query
        if attachment_id_in is not self.UNSPECIFIED:
            if attachment_id_in:
                query = query.filter(self.Attachment.id.in_(attachment_id_in))
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
        return self.User.query

    def _get_db_user(self, user_id):
        return self.user_query.get(user_id)

    def get_user(self, user_id):
        return self._get_domain_object_from_db_object(
            self._get_db_user(user_id))

    def get_user_by_email(self, email):
        return self._get_domain_object_from_db_object(
            self.user_query.filter_by(email=email).first())

    def _get_users_query(self, email_in=UNSPECIFIED):
        query = self.user_query
        if email_in is not self.UNSPECIFIED:
            if email_in:
                query = query.filter(self.User.email.in_(email_in))
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
        return self.Option.query

    def _get_db_option(self, key):
        return self.option_query.get(key)

    def get_option(self, key):
        return self._get_domain_object_from_db_object(self._get_db_option(key))

    def _get_options_query(self, key_in=UNSPECIFIED):
        query = self.option_query
        if key_in is not self.UNSPECIFIED:
            if key_in:
                query = query.filter(self.Option.key.in_(key_in))
            else:
                # avoid performance penalty
                query = query.filter(False)
        return query

    def get_options(self, key_in=UNSPECIFIED):
        query = self._get_options_query(key_in=key_in)
        return (self._get_domain_object_from_db_object(_) for _ in query)

    def count_options(self, key_in=UNSPECIFIED):
        return self._get_options_query(key_in=key_in).count()


def generate_task_class(pl, tags_tasks_table, users_tasks_table,
                        task_dependencies_table, task_prioritize_table):
    db = pl.db

    class DbTask(Changeable, db.Model, TaskBase):

        __tablename__ = 'task'

        _domobj = None

        id = db.Column(db.Integer, primary_key=True)
        summary = db.Column(db.String(100))
        description = db.Column(db.String(4000))
        is_done = db.Column(db.Boolean)
        is_deleted = db.Column(db.Boolean)
        order_num = db.Column(db.Integer, nullable=False, default=0)
        deadline = db.Column(db.DateTime)
        expected_duration_minutes = db.Column(db.Integer)
        expected_cost = db.Column(db.Numeric)
        tags = db.relationship('DbTag', secondary=tags_tasks_table,
                               back_populates="tasks")

        @property
        def tags2(self):
            return list(self.tags)
        users = db.relationship('DbUser', secondary=users_tasks_table,
                                backref=db.backref('tasks', lazy='dynamic'))

        parent_id = db.Column(db.Integer, db.ForeignKey('task.id'),
                              nullable=True)
        parent = db.relationship('DbTask', remote_side=[id],
                                 backref=db.backref('children',
                                                    lazy='dynamic'))

        # self depends on self.dependees
        # self.dependants depend on self
        dependees = db.relationship(
            'DbTask', secondary=task_dependencies_table,
            primaryjoin=task_dependencies_table.c.dependant_id == id,
            secondaryjoin=task_dependencies_table.c.dependee_id == id,
            backref='dependants')

        # self is after self.prioritize_before's
        # self has lower priority that self.prioritize_before's
        # self is before self.prioritize_after's
        # self has higher priority that self.prioritize_after's
        prioritize_before = db.relationship(
            'DbTask', secondary=task_prioritize_table,
            primaryjoin=task_prioritize_table.c.prioritize_after_id == id,
            secondaryjoin=task_prioritize_table.c.prioritize_before_id == id,
            backref='prioritize_after')

        def __init__(self, summary, description='', is_done=False,
                     is_deleted=False, deadline=None,
                     expected_duration_minutes=None, expected_cost=None):
            db.Model.__init__(self)
            TaskBase.__init__(
                self, summary=summary, description=description,
                is_done=is_done, is_deleted=is_deleted, deadline=deadline,
                expected_duration_minutes=expected_duration_minutes,
                expected_cost=expected_cost)

        @staticmethod
        def from_dict(d):
            task_id = d.get('id', None)
            summary = d.get('summary')
            description = d.get('description', '')
            is_done = d.get('is_done', False)
            is_deleted = d.get('is_deleted', False)
            order_num = d.get('order_num', 0)
            deadline = d.get('deadline', None)
            expected_duration_minutes = d.get('expected_duration_minutes',
                                              None)
            expected_cost = d.get('expected_cost', None)
            # 'tag_ids': [tag.id for tag in self.tags],
            # 'user_ids': [user.id for user in self.users]

            task = DbTask(summary=summary, description=description,
                          is_done=is_done, is_deleted=is_deleted,
                          deadline=deadline,
                          expected_duration_minutes=expected_duration_minutes,
                          expected_cost=expected_cost)
            if task_id is not None:
                task.id = task_id
            task.order_num = order_num
            if 'parent' in d:
                task.parent = d['parent']
            elif 'parent_id' in d:
                task.parent_id = d['parent_id']
            if 'children' in d:
                clear(task.users)
                task.children.extend(d['children'])
            if 'tags' in d:
                clear(task.users)
                extend(task.tags, d['tags'])
            if 'users' in d:
                clear(task.users)
                extend(task.users, d['users'])
            if 'dependees' in d:
                clear(task.dependees)
                extend(task.dependees, d['dependees'])
            if 'dependants' in d:
                clear(task.dependants)
                extend(task.dependants, d['dependants'])
            if 'prioritize_before' in d:
                clear(task.prioritize_before)
                extend(task.prioritize_before, d['prioritize_before'])
            if 'prioritize_after' in d:
                clear(task.prioritize_after)
                extend(task.prioritize_after, d['prioritize_after'])
            if 'notes' in d:
                clear(task.notes)
                extend(task.notes, d['notes'])
            if 'attachments' in d:
                clear(task.attachments)
                extend(task.attachments, d['attachments'])
            return task

        def make_change(self, field, operation, value):
            if field in (self.FIELD_ID, self.FIELD_SUMMARY,
                         self.FIELD_DESCRIPTION, self.FIELD_IS_DONE,
                         self.FIELD_IS_DELETED, self.FIELD_DEADLINE,
                         self.FIELD_EXPECTED_DURATION_MINUTES,
                         self.FIELD_EXPECTED_COST, self.FIELD_ORDER_NUM,
                         self.FIELD_PARENT, self.FIELD_PARENT_ID):
                if operation != Changeable.OP_SET:
                    raise ValueError(
                        'Invalid operation "{}" for field "{}"'.format(
                            operation, field))
            elif field in (self.FIELD_CHILDREN, self.FIELD_DEPENDEES,
                           self.FIELD_DEPENDANTS, self.FIELD_PRIORITIZE_BEFORE,
                           self.FIELD_PRIORITIZE_AFTER, self.FIELD_TAGS,
                           self.FIELD_USERS, self.FIELD_NOTES,
                           self.FIELD_ATTACHMENTS):
                if operation not in (Changeable.OP_ADD, Changeable.OP_REMOVE):
                    raise ValueError(
                        'Invalid operation "{}" for field "{}"'.format(
                            operation, field))
            else:
                raise ValueError('Unknown field "{}"'.format(field))

            if field == self.FIELD_ID:
                self.id = value
            elif field == self.FIELD_SUMMARY:
                self.summary = value
            elif field == self.FIELD_DESCRIPTION:
                self.description = value
            elif field == self.FIELD_IS_DONE:
                self.is_done = value
            elif field == self.FIELD_IS_DELETED:
                self.is_deleted = value
            elif field == self.FIELD_DEADLINE:
                self.deadline = value
            elif field == self.FIELD_EXPECTED_DURATION_MINUTES:
                self.expected_duration_minutes = value
            elif field == self.FIELD_EXPECTED_COST:
                self.expected_cost = value
            elif field == self.FIELD_ORDER_NUM:
                self.order_num = value
            elif field == self.FIELD_PARENT:
                self.parent = value
            elif field == self.FIELD_PARENT_ID:
                self.parent_id = value
            elif field == self.FIELD_CHILDREN:
                collection = self.children
            elif field == self.FIELD_DEPENDEES:
                collection = self.dependees
            elif field == self.FIELD_DEPENDANTS:
                collection = self.dependants
            elif field == self.FIELD_PRIORITIZE_BEFORE:
                collection = self.prioritize_before
            elif field == self.FIELD_PRIORITIZE_AFTER:
                collection = self.prioritize_after
            elif field == self.FIELD_TAGS:
                collection = self.tags
            elif field == self.FIELD_USERS:
                collection = self.users
            elif field == self.FIELD_NOTES:
                collection = self.notes
            elif field == self.FIELD_ATTACHMENTS:
                collection = self.attachments

            if operation == Changeable.OP_ADD:
                if value not in collection:
                    collection.append(value)
            elif operation == Changeable.OP_REMOVE:
                if value in collection:
                    collection.remove(value)

    return DbTask


def generate_tag_class(db, tags_tasks_table):
    class DbTag(db.Model, TagBase):

        __tablename__ = 'tag'

        _domobj = None

        id = db.Column(db.Integer, primary_key=True)
        value = db.Column(db.String(100), nullable=False, unique=True)
        description = db.Column(db.String(4000), nullable=True)

        tasks = db.relationship('DbTask', secondary=tags_tasks_table,
                                back_populates='tags')

        @property
        def tasks2(self):
            return list(self.tasks)

        def __init__(self, value, description=None):
            db.Model.__init__(self)
            TagBase.__init__(self, value, description)

        @staticmethod
        def from_dict(d):
            logger = logging_util.get_logger_by_class(__name__, Tag)
            logger.debug('d: {}'.format(d))

            tag_id = d.get('id', None)
            value = d.get('value')
            description = d.get('description', None)

            tag = DbTag(value, description)
            if tag_id is not None:
                tag.id = tag_id
            logger.debug('tag: {}'.format(tag))
            return tag

        def make_change(self, field, operation, value):
            if operation == Changeable.OP_CHANGING:
                raise ValueError('Invalid operation "{}"'.format(operation))

            if field in (self.FIELD_ID, self.FIELD_VALUE,
                         self.FIELD_DESCRIPTION):
                if operation != Changeable.OP_SET:
                    raise ValueError(
                        'Invalid operation "{}" for field "{}"'.format(
                            operation, field))
            elif field == self.FIELD_TASKS:
                if operation not in (Changeable.OP_ADD, Changeable.OP_REMOVE):
                    raise ValueError(
                        'Invalid operation "{}" for field "{}"'.format(
                            operation, field))
            else:
                raise ValueError('Unknown field "{}"'.format(field))

            if field == self.FIELD_ID:
                self.id = value
            elif field == self.FIELD_VALUE:
                self.value = value
            elif field == self.FIELD_DESCRIPTION:
                self.description = value
            else:  # field == self.FIELD_TASKS
                if operation == Changeable.OP_ADD:
                    if value not in self.tasks:
                        self.tasks.append(value)
                elif operation == Changeable.OP_REMOVE:
                    if value in self.tasks:
                        self.tasks.remove(value)

    return DbTag


def generate_note_class(db):
    class DbNote(db.Model, NoteBase):

        __tablename__ = 'note'

        _domobj = None

        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.String(4000))
        timestamp = db.Column(db.DateTime)

        task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
        task = db.relationship('DbTask',
                               backref=db.backref('notes', lazy='dynamic',
                                                  order_by=timestamp))

        def __init__(self, content, timestamp=None):
            db.Model.__init__(self)
            NoteBase.__init__(self, content, timestamp)

        @staticmethod
        def from_dict(d):
            note_id = d.get('id', None)
            content = d.get('content')
            timestamp = d.get('timestamp', None)
            task_id = d.get('task_id')

            note = DbNote(content, timestamp)
            if note_id is not None:
                note.id = note_id
            note.task_id = task_id
            return note

        def make_change(self, field, operation, value):
            if field in (self.FIELD_ID, self.FIELD_CONTENT,
                         self.FIELD_TIMESTAMP, self.FIELD_TASK_ID,
                         self.FIELD_TASK):
                if operation != Changeable.OP_SET:
                    raise ValueError(
                        'Invalid operation "{}" for field "{}"'.format(
                            operation, field))
            else:
                raise ValueError('Unknown field "{}"'.format(field))

            if field == self.FIELD_ID:
                self.id = value
            elif field == self.FIELD_CONTENT:
                self.content = value
            elif field == self.FIELD_TIMESTAMP:
                self.timestamp = value
            elif field == self.FIELD_TASK_ID:
                self.task_id = value
            else:  # field == self.FIELD_TASK
                self.task = value

    return DbNote


def generate_attachment_class(db):
    class DbAttachment(db.Model, AttachmentBase):

        __tablename__ = 'attachment'

        _domobj = None

        id = db.Column(db.Integer, primary_key=True)
        timestamp = db.Column(db.DateTime, nullable=False)
        path = db.Column(db.String(1000), nullable=False)
        filename = db.Column(db.String(100), nullable=False)
        description = db.Column(db.String(100), nullable=False, default='')

        task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
        task = db.relationship('DbTask',
                               backref=db.backref('attachments',
                                                  lazy='dynamic',
                                                  order_by=timestamp))

        def __init__(self, path, description=None, timestamp=None,
                     filename=None):
            db.Model.__init__(self)
            AttachmentBase.__init__(self, path, description, timestamp,
                                    filename)

        @staticmethod
        def from_dict(d):
            attachment_id = d.get('id', None)
            timestamp = d.get('timestamp', None)
            path = d.get('path')
            filename = d.get('filename', None)
            description = d.get('description', None)
            task_id = d.get('task_id')

            attachment = DbAttachment(path, description, timestamp, filename)
            if attachment_id is not None:
                attachment.id = attachment_id
            attachment.task_id = task_id
            return attachment

        def make_change(self, field, operation, value):
            if field in (self.FIELD_ID, self.FIELD_PATH,
                         self.FIELD_DESCRIPTION, self.FIELD_TIMESTAMP,
                         self.FIELD_FILENAME, self.FIELD_TASK_ID,
                         self.FIELD_TASK):
                if operation != Changeable.OP_SET:
                    raise ValueError(
                        'Invalid operation "{}" for field "{}"'.format(
                            operation, field))
            else:
                raise ValueError('Unknown field "{}"'.format(field))

            if field == self.FIELD_ID:
                self.id = value
            elif field == self.FIELD_PATH:
                self.path = value
            elif field == self.FIELD_DESCRIPTION:
                self.description = value
            elif field == self.FIELD_TIMESTAMP:
                self.timestamp = value
            elif field == self.FIELD_FILENAME:
                self.filename = value
            elif field == self.FIELD_TASK_ID:
                self.task_id = value
            else:  # field == self.FIELD_TASK
                self.task = value

    return DbAttachment


def generate_user_class(db, bcrypt):
    class DbUser(db.Model, UserBase):

        __tablename__ = 'user'

        _domobj = None

        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(100), nullable=False, unique=True)
        hashed_password = db.Column(db.String(100), nullable=False)
        is_admin = db.Column(db.Boolean, nullable=False, default=False)

        def __init__(self, email, hashed_password=None, is_admin=False):
            if hashed_password is None:
                digits = '0123456789abcdef'
                key = ''.join((random.choice(digits) for x in xrange(48)))
                hashed_password = bcrypt.generate_password_hash(key)
            db.Model.__init__(self)
            UserBase.__init__(self, email=email,
                              hashed_password=hashed_password,
                              is_admin=is_admin)

        @staticmethod
        def from_dict(d):
            user_id = d.get('id', None)
            email = d.get('email')
            hashed_password = d.get('hashed_password', None)
            is_admin = d.get('is_admin', False)

            user = DbUser(email, hashed_password, is_admin)
            if user_id is not None:
                user.id = user_id
            return user

        def make_change(self, field, operation, value):
            if field in (self.FIELD_ID, self.FIELD_EMAIL,
                         self.FIELD_HASHED_PASSWORD, self.FIELD_IS_ADMIN):
                if operation != Changeable.OP_SET:
                    raise ValueError(
                        'Invalid operation "{}" for field "{}"'.format(
                            operation, field))
            elif field == self.FIELD_TASKS:
                if operation not in (Changeable.OP_ADD, Changeable.OP_REMOVE):
                    raise ValueError(
                        'Invalid operation "{}" for field "{}"'.format(
                            operation, field))
            else:
                raise ValueError('Unknown field "{}"'.format(field))

            if field == self.FIELD_ID:
                self.id = value
            elif field == self.FIELD_EMAIL:
                self.email = value
            elif field == self.FIELD_HASHED_PASSWORD:
                self.hashed_password = value
            elif field == self.FIELD_IS_ADMIN:
                self.is_admin = value
            else:  # field == self.FIELD_TASKS
                if operation == Changeable.OP_ADD:
                    self.tasks.append(value)
                elif operation == Changeable.OP_REMOVE:
                    self.tasks.remove(value)

    return DbUser


def generate_option_class(db):
    class DbOption(db.Model, OptionBase):

        __tablename__ = 'option'

        _domobj = None

        key = db.Column(db.String(100), primary_key=True)
        value = db.Column(db.String(100), nullable=True)

        def __init__(self, key, value):
            db.Model.__init__(self)
            OptionBase.__init__(self, key, value)

        @staticmethod
        def from_dict(d):
            key = d.get('key')
            value = d.get('value', None)
            return DbOption(key, value)

        def make_change(self, field, operation, value):
            if field in (self.FIELD_KEY, self.FIELD_VALUE):
                if operation != Changeable.OP_SET:
                    raise ValueError(
                        'Invalid operation "{}" for field "{}"'.format(
                            operation, field))
            else:
                raise ValueError('Unknown field "{}"'.format(field))

            if field == self.FIELD_KEY:
                self.key = value
            else:  # field == self.FIELD_VALUE:
                self.value = value

    return DbOption
