
import logging_util
from models.tag_base import TagBase


def generate_tag_class(db, tags_tasks_table):
    class DbTag(db.Model, TagBase):
        _logger = logging_util.get_logger_by_name(__name__, 'DbTag')

        __tablename__ = 'tag'

        id = db.Column(db.Integer, primary_key=True)
        value = db.Column(db.String(100), nullable=False, unique=True)
        description = db.Column(db.String(4000), nullable=True)

        tasks = db.relationship('DbTask', secondary=tags_tasks_table,
                                back_populates='tags')

        def __init__(self, value, description=None):
            db.Model.__init__(self)
            TagBase.__init__(self, value, description)

        @classmethod
        def from_dict(cls, d):
            return super(DbTag, cls).from_dict(d=d)

        def clear_relationships(self):
            self.tasks = []

    return DbTag
