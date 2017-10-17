
class TaskUserOps(object):
    @staticmethod
    def is_user_authorized_or_admin(task, user):
        if user is None:
            return False
        if user.is_admin:
            return True
        if task.is_user_authorized(user):
            return True
        return False
