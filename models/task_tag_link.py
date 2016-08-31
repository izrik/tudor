
def generate_task_tag_link_class(db):
    class TaskTagLink(db.Model):
        task_id = db.Column(db.Integer, db.ForeignKey('task.id'),
                            primary_key=True)
        tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'),
                           primary_key=True)

        tag = db.relationship('Tag',
                              backref=db.backref('tasks', lazy='dynamic'))

        @property
        def value(self):
            return self.tag.value

        task = db.relationship('Task',
                               backref=db.backref('tags', lazy='dynamic'))

        def __init__(self, task_id, tag_id):
            self.task_id = task_id
            self.tag_id = tag_id

    return TaskTagLink
