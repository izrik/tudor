
from models.attachment_base import AttachmentBase


class GenericAttachment(AttachmentBase):
    id = None
    timestamp = None
    path = None
    filename = None
    description = None
    task = None

    def __init__(self, path=None, description=None, timestamp=None,
                 filename=None, id=None, task=None):
        super(GenericAttachment, self).__init__(
            path=path, description=description, timestamp=timestamp,
            filename=filename)
        self.id = id
        self.task = task
