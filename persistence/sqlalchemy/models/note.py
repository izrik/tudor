
import logging_util
from models.note_base import NoteBase


def generate_note_class(db):
    class DbNote(db.Model, NoteBase):
        _logger = logging_util.get_logger_by_name(__name__, 'DbNote')

        __tablename__ = 'note'

        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.String(4000))
        timestamp = db.Column(db.DateTime)

        task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
        task = db.relationship('DbTask',
                               backref=db.backref('notes', lazy='dynamic',
                                                  order_by=timestamp))

        def __init__(self, content, timestamp=None):
            db.Model.__init__(self)
            NoteBase.__init__(self, content, timestamp)

        @classmethod
        def from_dict(cls, d):
            return super(DbNote, cls).from_dict(d=d)

        def clear_relationships(self):
            self.task = None

    return DbNote
