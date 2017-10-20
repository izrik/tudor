
class UserCannotViewTaskException(Exception):
    def __init__(self, user, task):
        super(UserCannotViewTaskException, self).__init__(
            'User "{}" (id {}) cannot view task "{}" (id {})'.format(
                user.email, user.id, task.summary, task.id))
        self.user = user
        self.task = task
