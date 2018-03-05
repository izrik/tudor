
from __future__ import absolute_import

import logging_util
from models.option_base import OptionBase


def generate_option_class(db):
    class DbOption(db.Model, OptionBase):
        _logger = logging_util.get_logger_by_name(__name__, 'DbOption')

        __tablename__ = 'option'

        key = db.Column(db.String(100), primary_key=True)
        value = db.Column(db.String(100), nullable=True)

        def __init__(self, key, value, lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            db.Model.__init__(self)
            OptionBase.__init__(self, key, value)

        @classmethod
        def from_dict(cls, d, lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            return super(DbOption, cls).from_dict(d=d, lazy=None)

        def clear_relationships(self):
            pass

    return DbOption
