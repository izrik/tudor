import collections

import logging_util
from changeable import Changeable


class OneToManySet(collections.MutableSet):

    __change_field__ = None
    __attr_counterpart__ = None

    def __init__(self, container):
        self._logger = logging_util.get_logger(__name__, self)
        if container is None:
            raise ValueError('container cannot be None')

        self.container = container
        self.set = set()

    def __repr__(self):
        cls = type(self).__name__
        return '{}({})'.format(cls, self.set)

    @property
    def c(self):
        return self.container

    def __len__(self):
        return len(self.set)

    def __contains__(self, item):
        return self.set.__contains__(item)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, item):
        self._logger.debug('{}: {}'.format(self.c.id2, item.id2))
        if item not in self.set:
            self.container._on_attr_changing(self.__change_field__, None)
            self.set.add(item)
            setattr(item, self.__attr_counterpart__, self.container)
            self.container._on_attr_changed(self.__change_field__,
                                            Changeable.OP_ADD, item)

    def append(self, item):
        self._logger.debug('{}: {}'.format(self.c.id2, item.id2))
        self.add(item)

    def discard(self, item):
        self._logger.debug('{}: {}'.format(self.c.id2, item.id2))
        if item in self.set:
            self.container._on_attr_changing(self.__change_field__, None)
            self.set.discard(item)
            setattr(item, self.__attr_counterpart__, None)
            self.container._on_attr_changed(self.__change_field__,
                                            Changeable.OP_REMOVE, item)

    def __str__(self):
        return str(self.set)


class ManyToManySet(collections.MutableSet):

    __change_field__ = None
    __attr_counterpart__ = None

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self._logger = logging_util.get_logger(__name__, self)

        self.container = container
        self.set = set()

    @property
    def c(self):
        return self.container

    def __len__(self):
        return len(self.set)

    def __contains__(self, item):
        return self.set.__contains__(item)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, item):
        self._logger.debug('{}: {}'.format(self.c.id2, item.id2))
        if item not in self.set:
            self.container._on_attr_changing(self.__change_field__, None)
            self.set.add(item)
            getattr(item, self.__attr_counterpart__).add(self.container)
            self.container._on_attr_changed(self.__change_field__,
                                            Changeable.OP_ADD, item)

    def append(self, item):
        self._logger.debug('{}: {}'.format(self.c.id2, item.id2))
        self.add(item)

    def discard(self, item):
        self._logger.debug('{}: {}'.format(self.c.id2, item.id2))
        if item in self.set:
            self.container._on_attr_changing(self.__change_field__, None)
            self.set.discard(item)
            getattr(item, self.__attr_counterpart__).discard(self.container)
            self.container._on_attr_changed(self.__change_field__,
                                            Changeable.OP_REMOVE, item)
