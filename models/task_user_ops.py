
class TaskUserOps(object):
    @staticmethod
    def is_user_authorized_or_admin(task, user):
        if user is None:
            return False
        if user.is_anonymous:
            return False
        if user.is_admin:
            return True
        if task.is_user_authorized(user):
            return True
        return False

    @staticmethod
    def user_can_view_task(task, user):
        if TaskUserOps.is_user_authorized_or_admin(task, user):
            return True
        if task.is_public:
            return True
        return False

    @staticmethod
    def user_can_edit_task(task, user):
        if TaskUserOps.is_user_authorized_or_admin(task, user):
            return True
        return False
