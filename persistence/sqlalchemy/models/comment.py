
import logging_util
from models.comment_base import CommentBase


def generate_comment_class(db):
    class DbComment(db.Model, CommentBase):
        _logger = logging_util.get_logger_by_name(__name__, 'DbComment')

        __tablename__ = 'comment'

        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.Text)
        timestamp = db.Column(db.DateTime)

        task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
        task = db.relationship('DbTask',
                               backref=db.backref('comments', lazy='dynamic',
                                                  order_by=timestamp))

        def __init__(self, content, timestamp=None, lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            db.Model.__init__(self)
            CommentBase.__init__(self, content, timestamp)

        @classmethod
        def from_dict(cls, d, lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            return super(DbComment, cls).from_dict(d=d, lazy=None)

        def clear_relationships(self):
            self.task = None

    return DbComment
