
from models.attachment_base import AttachmentBase


class GenericAttachment(AttachmentBase):
    id = None
    timestamp = None
    path = None
    filename = None
    description = None
    task = None

    def __init__(self):
        super(GenericAttachment, self).__init__(None)
