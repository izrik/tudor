
import logging_util
from models.user_base import UserBase


def generate_user_class(db, users_tasks_table):
    class DbUser(db.Model, UserBase):
        _logger = logging_util.get_logger_by_name(__name__, 'DbUser')

        __tablename__ = 'user'

        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(100), nullable=False, unique=True)
        hashed_password = db.Column(db.String(100))
        is_admin = db.Column(db.Boolean, nullable=False, default=False)

        tasks = db.relationship('DbTask', secondary=users_tasks_table,
                                back_populates='users')

        def __init__(self, email, hashed_password=None, is_admin=False,
                     lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            db.Model.__init__(self)
            UserBase.__init__(self, email=email,
                              hashed_password=hashed_password,
                              is_admin=is_admin)

        @classmethod
        def from_dict(cls, d, lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            return super(DbUser, cls).from_dict(d=d, lazy=None)

        def clear_relationships(self):
            self.tasks = []

    return DbUser
