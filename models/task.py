
import collections

from dateutil.parser import parse as dparse

from conversions import str_from_datetime
from changeable import Changeable


class TaskBase(object):
    depth = 0

    def __init__(self, summary, description='', is_done=False,
                 is_deleted=False, deadline=None,
                 expected_duration_minutes=None, expected_cost=None):
        self.summary = summary
        self.description = description
        self.is_done = not not is_done
        self.is_deleted = not not is_deleted
        self.deadline = self._clean_deadline(deadline)
        self.expected_duration_minutes = expected_duration_minutes
        self.expected_cost = expected_cost
        self.order_num = 0

    @staticmethod
    def _clean_deadline(deadline):
        if isinstance(deadline, basestring):
            return dparse(deadline)
        return deadline

    def to_dict(self):
        return {
            'id': self.id,
            'summary': self.summary,
            'description': self.description,
            'is_done': self.is_done,
            'is_deleted': self.is_deleted,
            'order_num': self.order_num,
            'deadline': str_from_datetime(self.deadline),
            'parent': self.parent,
            'parent_id': self.parent_id,
            'expected_duration_minutes':
                self.expected_duration_minutes,
            'expected_cost': self.get_expected_cost_for_export(),
            'children': list(self.children),
            'tag_ids': [tag.id for tag in self.tags],
            'user_ids': [user.id for user in self.users]
        }

    def update_from_dict(self, d):
        if 'id' in d and d['id'] is not None:
            self.id = d['id']
        if 'summary' in d:
            self.summary = d['summary']
        if 'description' in d:
            self.description = d['description']
        if 'is_done' in d:
            self.is_done = d['is_done']
        if 'is_deleted' in d:
            self.is_deleted = d['is_deleted']
        if 'order_num' in d:
            self.order_num = d['order_num']
        if 'deadline' in d:
            self.deadline = self._clean_deadline(d['deadline'])
        if 'expected_duration_minutes' in d:
            self.expected_duration_minutes = d['expected_duration_minutes']
        if 'expected_cost' in d:
            self.expected_cost = d['expected_cost']
        if 'parent' in d:
            self.parent = d['parent']
        if 'parent_id' in d:
            self.parent_id = d['parent_id']
        # if 'children' in d:
        #     self.children.clear()
        #     self.children.extend(d['children'])

    def get_expected_cost_for_export(self):
        if self.expected_cost is None:
            return None
        return '{:.2f}'.format(self.expected_cost)


class Task(Changeable, TaskBase):

    _id = None
    _summary = None
    _description = None
    _is_done = None
    _is_deleted = None
    _order_num = None
    _deadline = None
    _expected_duration_minutes = None
    _expected_cost = None
    _parent_id = None
    _parent = None

    def __init__(self, summary, description='', is_done=False,
                 is_deleted=False, deadline=None,
                 expected_duration_minutes=None, expected_cost=None):
        super(Task, self).__init__(
            summary, description, is_done, is_deleted, deadline,
            expected_duration_minutes, expected_cost)

        self._dependees = InterlinkedDependees(self)
        self._dependants = InterlinkedDependants(self)
        self._prioritize_before = InterlinkedPrioritizeBefore(self)
        self._prioritize_after = InterlinkedPrioritizeAfter(self)
        self._tags = InterlinkedTags(self)
        self._users = InterlinkedUsers(self)
        self._children = InterlinkedChildren(self)

        self.id = None
        self.parent = None
        self.parent_id = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
        self._on_attr_changed()

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        self._summary = value
        self._on_attr_changed()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
        self._on_attr_changed()

    @property
    def is_done(self):
        return self._is_done

    @is_done.setter
    def is_done(self, value):
        self._is_done = value
        self._on_attr_changed()

    @property
    def is_deleted(self):
        return self._is_deleted

    @is_deleted.setter
    def is_deleted(self, value):
        self._is_deleted = value
        self._on_attr_changed()

    @property
    def order_num(self):
        return self._order_num

    @order_num.setter
    def order_num(self, value):
        self._order_num = value
        self._on_attr_changed()

    @property
    def deadline(self):
        return self._deadline

    @deadline.setter
    def deadline(self, value):
        self._deadline = value
        self._on_attr_changed()

    @property
    def expected_duration_minutes(self):
        return self._expected_duration_minutes

    @expected_duration_minutes.setter
    def expected_duration_minutes(self, value):
        self._expected_duration_minutes = value
        self._on_attr_changed()

    @property
    def expected_cost(self):
        return self._expected_cost

    @expected_cost.setter
    def expected_cost(self, value):
        self._expected_cost = value
        self._on_attr_changed()

    @property
    def parent_id(self):
        return self._parent_id

    @parent_id.setter
    def parent_id(self, value):
        self._parent_id = value
        self._on_attr_changed()

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        if value is not self._parent:
            if self._parent is not None:
                self._parent.children.remove(self)
            self._parent = value
            if self._parent is not None:
                self._parent.children.append(self)
            self._on_attr_changed()

    @property
    def children(self):
        return self._children

    @property
    def tags(self):
        return self._tags

    @property
    def users(self):
        return self._users

    @property
    def dependees(self):
        return self._dependees

    @property
    def dependants(self):
        return self._dependants

    @property
    def prioritize_before(self):
        return self._prioritize_before

    @property
    def prioritize_after(self):
        return self._prioritize_after

    @staticmethod
    def from_dict(d):
        task_id = d.get('id', None)
        summary = d.get('summary')
        description = d.get('description', '')
        is_done = d.get('is_done', False)
        is_deleted = d.get('is_deleted', False)
        order_num = d.get('order_num', 0)
        deadline = d.get('deadline', None)
        parent_id = d.get('parent_id', None)
        expected_duration_minutes = d.get('expected_duration_minutes',
                                          None)
        expected_cost = d.get('expected_cost', None)
        # 'tag_ids': [tag.id for tag in self.tags],
        # 'user_ids': [user.id for user in self.users]

        task = Task(summary=summary, description=description,
                    is_done=is_done, is_deleted=is_deleted,
                    deadline=deadline,
                    expected_duration_minutes=expected_duration_minutes,
                    expected_cost=expected_cost)
        if task_id is not None:
            task.id = task_id
        task.order_num = order_num
        task.parent_id = parent_id
        return task

    def get_css_class(self):
        if self.is_deleted and self.is_done:
            return 'done-deleted'
        if self.is_deleted:
            return 'not-done-deleted'
        if self.is_done:
            return 'done-not-deleted'
        return ''

    def get_css_class_attr(self):
        cls = self.get_css_class()
        if cls:
            return ' class="{}" '.format(cls)
        return ''

    def get_tag_values(self):
        for tag in self.tags:
            yield tag.value

    def get_expected_duration_for_viewing(self):
        if self.expected_duration_minutes is None:
            return ''
        if self.expected_duration_minutes == 1:
            return '1 minute'
        return '{} minutes'.format(self.expected_duration_minutes)

    def get_expected_cost_for_viewing(self):
        if self.expected_cost is None:
            return ''
        return '{:.2f}'.format(self.expected_cost)

    def is_user_authorized(self, user):
        return user in self.users

    def contains_dependency_cycle(self, visited=None):
        if visited is None:
            visited = set()
        if self in visited:
            return True
        visited = set(visited)
        visited.add(self)
        for dependee in self.dependees:
            if dependee.contains_dependency_cycle(visited):
                return True

        return False

    def contains_priority_cycle(self, visited=None):
        if visited is None:
            visited = set()
        if self in visited:
            return True
        visited = set(visited)
        visited.add(self)
        for before in self.prioritize_before:
            if before.contains_priority_cycle(visited):
                return True
        return False


class InterlinkedChildren(collections.MutableSequence):
    def __init__(self, container, *args):
        if container is None:
            raise ValueError('container cannot be None')

        self.container = container
        self.list = list()
        self.extend(list(args))

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __delitem__(self, i):
        self.remove(self[i])

    def __setitem__(self, i, v):
        del self[i]
        self.insert(i, v)

    def __contains__(self, value):
        return self.list.__contains__(value)

    def append(self, value):
        if value not in self:
            self.list.append(value)
            value.parent = self.container
            self.container._on_attr_changed()

    def remove(self, value):
        if value in self:
            self.list.remove(value)
            value.parent = None
            self.container._on_attr_changed()

    def insert(self, i, v):
        if v in self:
            if self.index(v) < i:
                i -= 1
            self.remove(v)

        v.parent = None
        self.list.insert(i, v)
        v.parent = self.container
        self.container._on_attr_changed()

    def __str__(self):
        return str(self.list)


class InterlinkedTags(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self.container = container
        self.set = set()

    def __len__(self):
        return len(self.set)

    def __contains__(self, tag):
        return self.set.__contains__(tag)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, tag):
        if tag not in self.set:
            self.set.add(tag)
            tag.tasks.add(self.container)

    def discard(self, tag):
        if tag in self.set:
            self.set.discard(tag)
            tag.tasks.discard(self.container)


class InterlinkedUsers(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self.container = container
        self.set = set()

    def __len__(self):
        return len(self.set)

    def __contains__(self, user):
        return self.set.__contains__(user)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, user):
        if user not in self.set:
            self.set.add(user)
            user.tasks.add(self.container)

    def discard(self, user):
        if user in self.set:
            self.set.discard(user)
            user.tasks.discard(self.container)


class InterlinkedDependees(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self.container = container
        self.set = set()

    def __len__(self):
        return len(self.set)

    def __contains__(self, dependee):
        return self.set.__contains__(dependee)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, dependee):
        if dependee not in self.set:
            self.set.add(dependee)
            dependee.dependants.add(self.container)

    def discard(self, dependee):
        if dependee in self.set:
            self.set.discard(dependee)
            dependee.dependants.discard(self.container)


class InterlinkedDependants(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self.container = container
        self.set = set()

    def __len__(self):
        return len(self.set)

    def __contains__(self, dependant):
        return self.set.__contains__(dependant)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, dependant):
        if dependant not in self.set:
            self.set.add(dependant)
            dependant.dependees.add(self.container)

    def discard(self, dependant):
        if dependant in self.set:
            self.set.discard(dependant)
            dependant.dependees.discard(self.container)


class InterlinkedPrioritizeBefore(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self.container = container
        self.set = set()

    def __len__(self):
        return len(self.set)

    def __contains__(self, before):
        return self.set.__contains__(before)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, before):
        if before not in self.set:
            self.set.add(before)
            before.prioritize_after.add(self.container)

    def discard(self, before):
        if before in self.set:
            self.set.discard(before)
            before.prioritize_after.discard(self.container)


class InterlinkedPrioritizeAfter(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self.container = container
        self.set = set()

    def __len__(self):
        return len(self.set)

    def __contains__(self, after):
        return self.set.__contains__(after)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, after):
        if after not in self.set:
            self.set.add(after)
            after.prioritize_before.add(self.container)

    def discard(self, after):
        if after in self.set:
            self.set.discard(after)
            after.prioritize_before.discard(self.container)
