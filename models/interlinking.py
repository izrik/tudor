import collections

import logging_util
from changeable import Changeable, id2


class InterlinkedSet(collections.MutableSet):
    _logger = logging_util.get_logger_by_name(__name__, 'InterlinkedSet')

    __change_field__ = None
    __attr_counterpart__ = None

    def __init__(self, container, lazy=None):
        if container is None:
            raise ValueError('container cannot be None')

        self.container = container
        self.set = set()
        self._lazy = lazy

    def __repr__(self):
        cls = type(self).__name__
        if self._lazy:
            return '{}(<lazy>)'.format(cls)
        return '{}({})'.format(cls, self.set)

    def _populate(self):
        if self._lazy:
            self.set.update(self._lazy)
            self._lazy = None

    @property
    def c(self):
        return self.container

    def __len__(self):
        self._populate()
        return len(self.set)

    def __contains__(self, item):
        self._populate()
        return self.set.__contains__(item)

    def __iter__(self):
        self._populate()
        return self.set.__iter__()

    def append(self, item):
        self._logger.debug('{}: {}'.format(id2(self.c), id2(item)))
        self._populate()
        self.add(item)

    def __str__(self):
        if self._lazy:
            return 'set(<lazy>)'
        return str(self.set)

    def _add(self, item):
        self._populate()
        self.set.add(item)

    def _discard(self, item):
        self._populate()
        self.set.discard(item)


class OneToManySet(InterlinkedSet):
    _logger = logging_util.get_logger_by_name(__name__, 'OneToManySet')

    def add(self, item):
        self._logger.debug('{}: {}'.format(id2(self.c), id2(item)))
        if item not in self:
            self.container._on_attr_changing(self.__change_field__, None)
            self._add(item)
            setattr(item, self.__attr_counterpart__, self.container)
            self.container._on_attr_changed(self.__change_field__,
                                            Changeable.OP_ADD, item)

    def discard(self, item):
        self._logger.debug('{}: {}'.format(id2(self.c), id2(item)))
        if item in self:
            self.container._on_attr_changing(self.__change_field__, None)
            self._discard(item)
            setattr(item, self.__attr_counterpart__, None)
            self.container._on_attr_changed(self.__change_field__,
                                            Changeable.OP_REMOVE, item)


class ManyToManySet(InterlinkedSet):
    _logger = logging_util.get_logger_by_name(__name__, 'ManyToManySet')

    def add(self, item):
        self._logger.debug('{}: {}'.format(id2(self.c), id2(item)))
        if item not in self:
            self.container._on_attr_changing(self.__change_field__, None)
            self._add(item)
            getattr(item, self.__attr_counterpart__).add(self.container)
            self.container._on_attr_changed(self.__change_field__,
                                            Changeable.OP_ADD, item)

    def discard(self, item):
        self._logger.debug('{}: {}'.format(id2(self.c), id2(item)))
        if item in self:
            self.container._on_attr_changing(self.__change_field__, None)
            self._discard(item)
            getattr(item, self.__attr_counterpart__).discard(self.container)
            self.container._on_attr_changed(self.__change_field__,
                                            Changeable.OP_REMOVE, item)
