
from models.task_user_ops import TaskUserOps


class CommentUserOps(object):
    @staticmethod
    def user_can_edit_comment(comment, task, user):
        """Whether the user may change the content of the comment.

        Only the comment's author may edit it. Admins may edit any comment,
        which is also the only way to edit the comments that pre-date
        authorship and so have no author at all.
        """
        if comment is None:
            return False
        if not TaskUserOps.is_user_authorized_or_admin(task, user):
            return False
        if user.is_admin:
            return True
        return (comment.author_id is not None and
                comment.author_id == user.id)
