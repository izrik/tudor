import collections

import logging_util
from persistence.in_memory.models.changeable import Changeable


class InterlinkedSet(collections.MutableSet):
    _logger = logging_util.get_logger_by_name(__name__, 'InterlinkedSet')

    __change_field__ = None
    __attr_counterpart__ = None

    def __init__(self, container, lazy=None):
        self._logger.debug('__init__')
        if container is None:
            raise ValueError('container cannot be None')

        self.container = container
        self.set = set()
        self._lazy = lazy

    def __repr__(self):
        self._logger.debug('__repr__')
        cls = type(self).__name__
        if self._lazy:
            return '{}(<lazy>)'.format(cls)
        return '{}({})'.format(cls, self.set)

    def _populate(self):
        self._logger.debug('_populate')
        if self._lazy:
            self._logger.debug('populating the collection')
            self.set.update(self._lazy)
            self._lazy = None

    @property
    def c(self):
        return self.container

    def __len__(self):
        self._logger.debug('__len__')
        self._populate()
        return len(self.set)

    def __contains__(self, item):
        self._logger.debug('__contains__')
        self._populate()
        return self.set.__contains__(item)

    def __iter__(self):
        self._logger.debug('__iter__')
        self._populate()
        return self.set.__iter__()

    def append(self, item):
        self._logger.debug('append')
        self._logger.debug('%s: %s', self.c, item)
        self._populate()
        self.add(item)

    def __str__(self):
        self._logger.debug('__str__')
        if self._lazy:
            return 'set(<lazy>)'
        return str(self.set)

    def _add(self, item):
        self._logger.debug('_add')
        self._populate()
        self.set.add(item)

    def _discard(self, item):
        self._logger.debug('_discard')
        self._populate()
        self.set.discard(item)

    def count(self):
        return len(self)


class OneToManySet(InterlinkedSet):
    _logger = logging_util.get_logger_by_name(__name__, 'OneToManySet')

    def add(self, item):
        self._logger.debug('add')
        self._logger.debug('%s: %s', self.c, item)
        if item not in self:
            self._logger.debug('adding the item')
            self.container._on_attr_changing(self.__change_field__, None)
            self._add(item)
            setattr(item, self.__attr_counterpart__, self.container)
            self.container._on_attr_changed(self.__change_field__,
                                            Changeable.OP_ADD, item)

    def discard(self, item):
        self._logger.debug('discard')
        self._logger.debug('%s: %s', self.c, item)
        if item in self:
            self._logger.debug('discarding the item')
            self.container._on_attr_changing(self.__change_field__, None)
            self._discard(item)
            setattr(item, self.__attr_counterpart__, None)
            self.container._on_attr_changed(self.__change_field__,
                                            Changeable.OP_REMOVE, item)


class ManyToManySet(InterlinkedSet):
    _logger = logging_util.get_logger_by_name(__name__, 'ManyToManySet')

    def add(self, item):
        self._logger.debug('add')
        self._logger.debug('%s: %s', self.c, item)
        if item not in self:
            self._logger.debug('adding the item')
            self.container._on_attr_changing(self.__change_field__, None)
            self._add(item)
            getattr(item, self.__attr_counterpart__).add(self.container)
            self.container._on_attr_changed(self.__change_field__,
                                            Changeable.OP_ADD, item)

    def discard(self, item):
        self._logger.debug('discard')
        self._logger.debug('%s: %s', self.c, item)
        if item in self:
            self._logger.debug('discarding the item')
            self.container._on_attr_changing(self.__change_field__, None)
            self._discard(item)
            getattr(item, self.__attr_counterpart__).discard(self.container)
            self.container._on_attr_changed(self.__change_field__,
                                            Changeable.OP_REMOVE, item)
