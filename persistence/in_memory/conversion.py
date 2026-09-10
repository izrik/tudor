from models.attachment import Attachment
from models.comment import Comment
from models.option import Option
from models.tag import Tag
from models.task import Task
from models.user import User


def to_task(stored_task):
    if stored_task is None:
        return None
    return Task(
        id=stored_task.id,
        summary=stored_task.summary,
        description=stored_task.description,
        is_done=stored_task.is_done,
        is_deleted=stored_task.is_deleted,
        deadline=stored_task.deadline,
        expected_duration_minutes=stored_task.expected_duration_minutes,
        expected_cost=stored_task.expected_cost,
        order_num=stored_task.order_num or 0,
        parent_id=stored_task.parent_id,
        is_public=stored_task.is_public,
        date_created=stored_task.date_created,
        date_last_updated=stored_task.date_last_updated)


def apply_task_to_stored(task, stored_task):
    if task.id is not None:
        stored_task.id = task.id
    stored_task.summary = task.summary
    stored_task.description = task.description
    stored_task.is_done = task.is_done
    stored_task.is_deleted = task.is_deleted
    stored_task.deadline = task.deadline
    stored_task.expected_duration_minutes = task.expected_duration_minutes
    stored_task.expected_cost = task.expected_cost
    stored_task.order_num = task.order_num
    stored_task.is_public = task.is_public
    stored_task.date_created = task.date_created
    stored_task.date_last_updated = task.date_last_updated


def to_tag(stored_tag):
    if stored_tag is None:
        return None
    return Tag(id=stored_tag.id, value=stored_tag.value,
               description=stored_tag.description)


def apply_tag_to_stored(tag, stored_tag):
    if tag.id is not None:
        stored_tag.id = tag.id
    stored_tag.value = tag.value
    stored_tag.description = tag.description


def to_comment(stored_comment):
    if stored_comment is None:
        return None
    task_id = stored_comment.task.id if stored_comment.task else None
    return Comment(
        id=stored_comment.id,
        content=stored_comment.content,
        timestamp=stored_comment.timestamp,
        date_last_updated=stored_comment.date_last_updated,
        task_id=task_id)


def apply_comment_to_stored(comment, stored_comment):
    if comment.id is not None:
        stored_comment.id = comment.id
    stored_comment.content = comment.content
    stored_comment.timestamp = comment.timestamp
    stored_comment.date_last_updated = comment.date_last_updated


def to_attachment(stored_attachment):
    if stored_attachment is None:
        return None
    task_id = stored_attachment.task.id if stored_attachment.task else None
    return Attachment(
        id=stored_attachment.id,
        path=stored_attachment.path,
        description=stored_attachment.description or '',
        timestamp=stored_attachment.timestamp,
        filename=stored_attachment.filename,
        task_id=task_id)


def apply_attachment_to_stored(attachment, stored_attachment):
    if attachment.id is not None:
        stored_attachment.id = attachment.id
    stored_attachment.path = attachment.path
    stored_attachment.description = attachment.description
    stored_attachment.timestamp = attachment.timestamp
    stored_attachment.filename = attachment.filename


def to_user(stored_user):
    if stored_user is None:
        return None
    return User(
        id=stored_user.id,
        email=stored_user.email,
        hashed_password=stored_user.hashed_password,
        is_admin=stored_user.is_admin)


def apply_user_to_stored(user, stored_user):
    if user.id is not None:
        stored_user.id = user.id
    stored_user.email = user.email
    stored_user.hashed_password = user.hashed_password
    stored_user.is_admin = user.is_admin


def to_option(stored_option):
    if stored_option is None:
        return None
    return Option(key=stored_option.key, value=stored_option.value)


def apply_option_to_stored(option, stored_option):
    stored_option.key = option.key
    stored_option.value = option.value
