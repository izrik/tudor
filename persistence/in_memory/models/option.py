
import logging_util
from models.option_base import OptionBase
from persistence.in_memory.models.changeable import Changeable


class Option(Changeable, OptionBase):
    _logger = logging_util.get_logger_by_name(__name__, 'Option')

    _key = None
    _value = None

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        if value != self._key:
            self._on_attr_changing(self.FIELD_KEY, self._key)
            self._key = value
            self._on_attr_changed(self.FIELD_KEY, self.OP_SET, self._key)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value != self._value:
            self._on_attr_changing(self.FIELD_VALUE,
                                   self._value)
            self._value = value
            self._on_attr_changed(self.FIELD_VALUE, self.OP_SET, self._value)

    def clear_relationships(self):
        pass
