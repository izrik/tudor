
class Changeable(object):

    OP_SET = 'SET'
    OP_ADD = 'ADD'
    OP_REMOVE = 'REMOVE'
    OP_CHANGING = 'CHANGING'

    def __init__(self, *args, **kwargs):
        self.changed_listener = None
        self.changing_listener = None
        super(Changeable, self).__init__(*args, **kwargs)

    def _on_attr_changing(self, field, value):
        if self.changing_listener:
            self.changing_listener(self, field, value)

    def _on_attr_changed(self, field, operation, value):
        if self.changed_listener:
            self.changed_listener(self, field, operation, value)

    def register_changing_listener(self, changing_listener):
        if (self.changing_listener and
                self.changing_listener != changing_listener):
            raise Exception('The "changing" listener has already been set.')
        self.changing_listener = changing_listener

    def register_changed_listener(self, changed_listener):
        if self.changed_listener and self.changed_listener != changed_listener:
            raise Exception('The "changed" listener has already been set.')
        self.changed_listener = changed_listener

    def unregister_change_listener(self, callable):
        self.change_listener = None


def id2(obj):
    if obj is None:
        return 'None'
    try:
        return obj.id2
    except AttributeError:
        return id(obj)
