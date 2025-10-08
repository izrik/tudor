
import logging_util
from models.option_base import OptionBase


def generate_option_class(db):
    class DbOption(db.Model, OptionBase):
        _logger = logging_util.get_logger_by_name(__name__, 'DbOption')

        __tablename__ = 'option'

        key = db.Column(db.String(100), primary_key=True)
        value = db.Column(db.String(100), nullable=True)

        def __init__(self, key, value):
            db.Model.__init__(self)
            OptionBase.__init__(self, key, value)

        @classmethod
        def from_dict(cls, d):
            return super(DbOption, cls).from_dict(d=d)

        def clear_relationships(self):
            pass

    return DbOption
