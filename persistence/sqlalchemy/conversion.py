from models.attachment import Attachment
from models.comment import Comment
from models.option import Option
from models.tag import Tag
from models.task import Task
from models.user import User


def to_task(db_task):
    if db_task is None:
        return None
    return Task(
        id=db_task.id,
        summary=db_task.summary,
        description=db_task.description,
        is_done=db_task.is_done,
        is_deleted=db_task.is_deleted,
        deadline=db_task.deadline,
        expected_duration_minutes=db_task.expected_duration_minutes,
        expected_cost=db_task.expected_cost,
        order_num=db_task.order_num or 0,
        parent_id=db_task.parent_id,
        is_public=db_task.is_public,
        date_created=db_task.date_created,
        date_last_updated=db_task.date_last_updated)


def apply_task_to_db(task, db_task):
    if task.id is not None:
        db_task.id = task.id
    db_task.summary = task.summary
    db_task.description = task.description
    db_task.is_done = task.is_done
    db_task.is_deleted = task.is_deleted
    db_task.deadline = task.deadline
    db_task.expected_duration_minutes = task.expected_duration_minutes
    db_task.expected_cost = task.expected_cost
    db_task.order_num = task.order_num
    db_task.parent_id = task.parent_id
    db_task.is_public = task.is_public
    db_task.date_created = task.date_created
    db_task.date_last_updated = task.date_last_updated


def to_tag(db_tag):
    if db_tag is None:
        return None
    return Tag(id=db_tag.id, value=db_tag.value, description=db_tag.description)


def apply_tag_to_db(tag, db_tag):
    if tag.id is not None:
        db_tag.id = tag.id
    db_tag.value = tag.value
    db_tag.description = tag.description


def to_comment(db_comment):
    if db_comment is None:
        return None
    return Comment(
        id=db_comment.id,
        content=db_comment.content,
        timestamp=db_comment.timestamp,
        date_last_updated=db_comment.date_last_updated,
        task_id=db_comment.task_id)


def apply_comment_to_db(comment, db_comment):
    if comment.id is not None:
        db_comment.id = comment.id
    db_comment.content = comment.content
    db_comment.timestamp = comment.timestamp
    db_comment.date_last_updated = comment.date_last_updated
    db_comment.task_id = comment.task_id


def to_attachment(db_attachment):
    if db_attachment is None:
        return None
    return Attachment(
        id=db_attachment.id,
        path=db_attachment.path,
        description=db_attachment.description or '',
        timestamp=db_attachment.timestamp,
        filename=db_attachment.filename,
        task_id=db_attachment.task_id)


def apply_attachment_to_db(attachment, db_attachment):
    if attachment.id is not None:
        db_attachment.id = attachment.id
    db_attachment.path = attachment.path
    db_attachment.description = attachment.description
    db_attachment.timestamp = attachment.timestamp
    db_attachment.filename = attachment.filename
    db_attachment.task_id = attachment.task_id


def to_user(db_user):
    if db_user is None:
        return None
    return User(
        id=db_user.id,
        email=db_user.email,
        hashed_password=db_user.hashed_password,
        is_admin=db_user.is_admin)


def apply_user_to_db(user, db_user):
    if user.id is not None:
        db_user.id = user.id
    db_user.email = user.email
    db_user.hashed_password = user.hashed_password
    db_user.is_admin = user.is_admin


def to_option(db_option):
    if db_option is None:
        return None
    return Option(key=db_option.key, value=db_option.value)


def apply_option_to_db(option, db_option):
    db_option.key = option.key
    db_option.value = option.value
