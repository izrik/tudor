
def generate_task_user_link_class(db):
    class TaskUserLink(db.Model):
        task_id = db.Column(db.Integer, db.ForeignKey('task.id'),
                            primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                            primary_key=True)

        user = db.relationship('User',
                               backref=db.backref('tasks', lazy='dynamic'))

        @property
        def email(self):
            return self.user.email

        task = db.relationship('Task',
                               backref=db.backref('users', lazy='dynamic'))

        def __init__(self, task_id, user_id):
            self.task_id = task_id
            self.user_id = user_id

    return TaskUserLink
