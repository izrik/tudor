import collections
from datetime import datetime, UTC
from numbers import Number

from sqlalchemy import or_, select, exists, false, func

from persistence.sqlalchemy.models.attachment import generate_attachment_class
from persistence.sqlalchemy.models.note import generate_note_class
from persistence.sqlalchemy.models.option import generate_option_class
from persistence.sqlalchemy.models.tag import generate_tag_class
from persistence.sqlalchemy.models.task import generate_task_class
from persistence.sqlalchemy.models.user import generate_user_class
from persistence.pager import Pager

import logging_util


def is_iterable(x):
    return isinstance(x, collections.abc.Iterable)


def as_iterable(x):
    if is_iterable(x):
        return x
    return (x,)


class SqlAlchemyPersistenceLayer(object):
    _logger = logging_util.get_logger_by_name(__name__,
                                              'SqlAlchemyPersistenceLayer')

    def __init__(self, db):
        self.db = db

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

    def add(self, dbobj):
        self._logger.debug('begin, dbobj: %s', dbobj)
        if not self._is_db_object(dbobj):
            raise Exception(
                'The object is not compatible with the PL: {}'.format(dbobj))

        self.db.session.add(dbobj)
        self._logger.debug('end')

    def delete(self, dbobj):
        self._logger.debug('begin, dbobj: %s', dbobj)
        if not self._is_db_object(dbobj):
            raise Exception(
                'The object is not compatible with the PL: {}'.format(dbobj))
        dbobj.clear_relationships()
        self.db.session.delete(dbobj)
        self._logger.debug('end')

    def commit(self):
        self._logger.debug('begin')
        ###############
        self._logger.debug('committing the db session/transaction')
        self.db.session.commit()
        self._logger.debug('committed the db session/transaction')
        ###############
        self._logger.debug('end')

    def rollback(self):
        self._logger.debug('begin')
        self.db.session.rollback()
        self._logger.debug('end')

    def execute(self, *args, **kwargs):
        self.db.session.execute(*args, **kwargs)

    def get_schema_version(self):
        try:
            stmt = select(self.DbOption).where(self.DbOption.key == '__version__')
            dbopt = self.db.session.execute(stmt).scalar_one_or_none()
        except Exception as e:
            print(f'got exception {e}')
            return None
        else:
            return dbopt

    def query(self, *args, **kwargs):
        # For backward compatibility, but deprecated in SQLAlchemy 2.0
        return self.db.session.query(*args, **kwargs)

    def _is_db_object(self, obj):
        return isinstance(obj, self.db.Model)

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
        # Deprecated in SQLAlchemy 2.0, but keeping for compatibility
        return self.DbTask.query

    def create_task(self, summary, description='', is_done=False,
                    is_deleted=False, deadline=None,
                    expected_duration_minutes=None, expected_cost=None,
                    is_public=False,
                    date_created=None,
                    date_last_updated=None,
                    lazy=None):
        if date_created is None:
            from datetime import datetime
            date_created = datetime.now(UTC)
        if date_last_updated is None:
            date_last_updated = date_created
        return self.DbTask(summary=summary, description=description,
                           is_done=is_done, is_deleted=is_deleted,
                           deadline=deadline,
                           expected_duration_minutes=expected_duration_minutes,
                           expected_cost=expected_cost, is_public=is_public,
                           date_created=date_created,
                           date_last_updated=date_last_updated,
                           lazy=lazy)

    def get_task(self, task_id):
        return self._get_db_task(task_id)

    def _get_db_task(self, task_id):
        if task_id is None:
            return None
        stmt = select(self.DbTask).where(self.DbTask.id == task_id)
        return self.db.session.execute(stmt).scalar_one_or_none()

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

        query = select(self.DbTask)

        if is_done is not self.UNSPECIFIED:
            query = query.where(self.DbTask.is_done == is_done)

        if is_deleted is not self.UNSPECIFIED:
            query = query.where(self.DbTask.is_deleted == is_deleted)

        if is_public is not self.UNSPECIFIED:
            query = query.where(self.DbTask.is_public == is_public)

        if parent_id is not self.UNSPECIFIED:
            if parent_id is None:
                query = query.where(self.DbTask.parent_id.is_(None))
            else:
                query = query.where(self.DbTask.parent_id == parent_id)

        if parent_id_in is not self.UNSPECIFIED:
            if parent_id_in:
                query = query.where(self.DbTask.parent_id.in_(parent_id_in))
            else:
                # avoid performance penalty
                query = query.where(false())

        if users_contains is not self.UNSPECIFIED:
            query = query.where(self.DbTask.users.any(id=users_contains.id))

        if is_public_or_users_contains is not self.UNSPECIFIED:
            db_user = is_public_or_users_contains
            query = query.outerjoin(
                self.users_tasks_table,
                self.users_tasks_table.c.task_id == self.DbTask.id).where(
                or_(
                    self.users_tasks_table.c.user_id == db_user.id,
                    self.DbTask.is_public
                )
            )

        if task_id_in is not self.UNSPECIFIED:
            # Using in_ on an empty set works but is expensive for some db
            # engines. In the case of an empty collection, just use a query
            # that always returns an empty set, without the performance
            # penalty.
            if task_id_in:
                query = query.where(self.DbTask.id.in_(task_id_in))
            else:
                query = query.where(false())

        if task_id_not_in is not self.UNSPECIFIED:
            # Using notin_ on an empty set works but is expensive for some db
            # engines. Moreover, it doesn't affect the actual set of selected
            # rows. In the case of an empty collection, just use the same query
            # object again, so we won't incur the performance penalty.
            if task_id_not_in:
                query = query.where(self.DbTask.id.notin_(task_id_not_in))
            else:
                query = query

        if deadline_is_not_none:
            query = query.where(self.DbTask.deadline.isnot(None))

        if tags_contains is not self.UNSPECIFIED:
            query = query.where(self.DbTask.tags.any(id=tags_contains.id))

        if summary_description_search_term is not self.UNSPECIFIED:
            like_term = '%{}%'.format(summary_description_search_term)
            query = query.where(
                self.DbTask.summary.ilike(like_term) |
                self.DbTask.description.ilike(like_term))

        if order_num_greq_than is not self.UNSPECIFIED:
            query = query.where(self.DbTask.order_num >= order_num_greq_than)

        if order_num_lesseq_than is not self.UNSPECIFIED:
            query = query.where(self.DbTask.order_num <=
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
        return (_ for _ in self.db.session.execute(query).scalars())

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
        pager = self.db.paginate(query, page=page_num, per_page=tasks_per_page)
        items = list(pager.items)
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
        count_query = select(func.count()).select_from(query.subquery())
        return self.db.session.execute(count_query).scalar()

    @property
    def tag_query(self):
        # Deprecated in SQLAlchemy 2.0
        return self.DbTag.query

    def create_tag(self, value, description=None, lazy=None):
        return self.DbTag(value=value, description=description, lazy=lazy)

    def _get_db_tag(self, tag_id):
        if tag_id is None:
            raise ValueError('tag_id cannot be None')
        stmt = select(self.DbTag).where(self.DbTag.id == tag_id)
        return self.db.session.execute(stmt).scalar_one_or_none()

    def get_tag(self, tag_id):
        if tag_id is None:
            raise ValueError('tag_id cannot be None')
        return self._get_db_tag(tag_id)

    def _get_tags_query(self, value=UNSPECIFIED, limit=None):
        query = select(self.DbTag)
        if value is not self.UNSPECIFIED:
            query = query.where(self.DbTag.value == value)
        if limit is not None:
            query = query.limit(limit)
        return query

    def get_tags(self, value=UNSPECIFIED, limit=None):
        query = self._get_tags_query(value=value, limit=limit)
        return (_ for _ in self.db.session.execute(query).scalars())

    def count_tags(self, value=UNSPECIFIED, limit=None):
        query = self._get_tags_query(value=value, limit=limit)
        count_query = select(func.count()).select_from(query.subquery())
        return self.db.session.execute(count_query).scalar()

    def get_tag_by_value(self, value):
        query = self._get_tags_query(value=value)
        return self.db.session.execute(query).scalars().first()

    @property
    def note_query(self):
        return self.DbNote.query

    def create_note(self, content, timestamp=None, lazy=None):
        return self.DbNote(content=content, timestamp=timestamp, lazy=lazy)

    def _get_db_note(self, note_id):
        if note_id is None:
            raise ValueError('note_id acannot be None')
        stmt = select(self.DbNote).where(self.DbNote.id == note_id)
        return self.db.session.execute(stmt).scalar_one_or_none()

    def get_note(self, note_id):
        if note_id is None:
            raise ValueError('note_id acannot be None')
        return self._get_db_note(note_id)

    def _get_notes_query(self, note_id_in=UNSPECIFIED):
        query = select(self.DbNote)
        if note_id_in is not self.UNSPECIFIED:
            if note_id_in:
                query = query.where(self.DbNote.id.in_(note_id_in))
            else:
                # performance improvement
                query = query.where(false())
        return query

    def get_notes(self, note_id_in=UNSPECIFIED):
        query = self._get_notes_query(note_id_in=note_id_in)
        return (_ for _ in self.db.session.execute(query).scalars())

    def count_notes(self, note_id_in=UNSPECIFIED):
        query = self._get_notes_query(note_id_in=note_id_in)
        count_query = select(func.count()).select_from(query.subquery())
        return self.db.session.execute(count_query).scalar()

    @property
    def attachment_query(self):
        return self.DbAttachment.query

    def create_attachment(self, path, description=None, timestamp=None,
                          filename=None, lazy=None):
        return self.DbAttachment(path=path, description=description,
                                 timestamp=timestamp, filename=filename,
                                 lazy=lazy)

    def _get_db_attachment(self, attachment_id):
        if attachment_id is None:
            raise ValueError('attachment_id acannot be None')
        stmt = select(self.DbAttachment).where(self.DbAttachment.id == attachment_id)
        return self.db.session.execute(stmt).scalar_one_or_none()

    def get_attachment(self, attachment_id):
        if attachment_id is None:
            raise ValueError('attachment_id acannot be None')
        return self._get_db_attachment(attachment_id)

    def _get_attachments_query(self, attachment_id_in=UNSPECIFIED):
        query = select(self.DbAttachment)
        if attachment_id_in is not self.UNSPECIFIED:
            if attachment_id_in:
                query = query.where(
                    self.DbAttachment.id.in_(attachment_id_in))
            else:
                query = query.where(false())
        return query

    def get_attachments(self, attachment_id_in=UNSPECIFIED):
        query = self._get_attachments_query(attachment_id_in=attachment_id_in)
        return (_ for _ in self.db.session.execute(query).scalars())

    def count_attachments(self, attachment_id_in=UNSPECIFIED):
        query = self._get_attachments_query(
            attachment_id_in=attachment_id_in)
        count_query = select(func.count()).select_from(query.subquery())
        return self.db.session.execute(count_query).scalar()

    @property
    def user_query(self):
        return self.DbUser.query

    def create_user(self, email, hashed_password=None, is_admin=False,
                    lazy=None):
        return self.DbUser(email=email, hashed_password=hashed_password,
                           is_admin=is_admin, lazy=lazy)

    _guest_user = None

    def get_guest_user(self):
        if self._guest_user is None:
            self._guest_user = self.create_user('guest@guest')
            self._guest_user._is_authenticated = False
            self._guest_user._is_anonymous = True
            self._guest_user.is_admin = False
        return self._guest_user

    def _get_db_user(self, user_id):
        if user_id is None:
            raise ValueError('user_id acannot be None')
        stmt = select(self.DbUser).where(self.DbUser.id == user_id)
        return self.db.session.execute(stmt).scalar_one_or_none()

    def get_user(self, user_id):
        if user_id is None:
            raise ValueError('user_id acannot be None')
        return self._get_db_user(user_id)

    def get_user_by_email(self, email):
        stmt = select(self.DbUser).where(self.DbUser.email == email)
        return self.db.session.execute(stmt).scalars().first()

    def _get_users_query(self, email_in=UNSPECIFIED):
        query = select(self.DbUser)
        if email_in is not self.UNSPECIFIED:
            if email_in:
                query = query.where(self.DbUser.email.in_(email_in))
            else:
                # avoid performance penalty
                query = query.where(false())
        return query

    def get_users(self, email_in=UNSPECIFIED):
        query = self._get_users_query(email_in=email_in)
        return (_ for _ in self.db.session.execute(query).scalars())

    def count_users(self, email_in=UNSPECIFIED):
        query = self._get_users_query(email_in=email_in)
        count_query = select(func.count()).select_from(query.subquery())
        return self.db.session.execute(count_query).scalar()

    @property
    def option_query(self):
        return self.DbOption.query

    def create_option(self, key, value):
        return self.DbOption(key=key, value=value)

    def _get_db_option(self, key):
        if key is None:
            raise ValueError('key acannot be None')
        stmt = select(self.DbOption).where(self.DbOption.key == key)
        return self.db.session.execute(stmt).scalar_one_or_none()

    def get_option(self, key):
        if key is None:
            raise ValueError('key acannot be None')
        return self._get_db_option(key)

    def _get_options_query(self, key_in=UNSPECIFIED):
        query = select(self.DbOption)
        if key_in is not self.UNSPECIFIED:
            if key_in:
                query = query.where(self.DbOption.key.in_(key_in))
            else:
                # avoid performance penalty
                query = query.where(false())
        return query

    def get_options(self, key_in=UNSPECIFIED):
        query = self._get_options_query(key_in=key_in)
        return (_ for _ in self.db.session.execute(query).scalars())

    def count_options(self, key_in=UNSPECIFIED):
        query = self._get_options_query(key_in=key_in)
        count_query = select(func.count()).select_from(query.subquery())
        return self.db.session.execute(count_query).scalar()
