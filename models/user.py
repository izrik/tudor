
import random


def generate_user_class(db, bcrypt):
    class User(db.Model):
        email = db.Column(db.String(100), primary_key=True, nullable=False)
        hashed_password = db.Column(db.String(100), nullable=False)
        is_admin = db.Column(db.Boolean, nullable=False, default=False)
        authenticated = True

        def __init__(self, email, hashed_password=None, is_admin=False):
            if hashed_password is None:
                digits = '0123456789abcdef'
                key = ''.join((random.choice(digits) for x in xrange(48)))
                hashed_password = bcrypt.generate_password_hash(key)

            self.email = email
            self.hashed_password = hashed_password
            self.is_admin = is_admin

        def to_dict(self):
            return {
                'email': self.email,
                'hashed_password': self.hashed_password,
                'is_admin': self.is_admin
            }

        def is_active(self):
            return True

        def get_id(self):
            return self.email

        def is_authenticated(self):
            return self.authenticated

        def is_anonymous(self):
            return False

    return User
