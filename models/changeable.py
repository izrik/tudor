
class Changeable(object):
    def __init__(self, *args, **kwargs):
        self.change_listener = None
        super(Changeable, self).__init__(*args, **kwargs)

    def _on_attr_changed(self, field):
        if self.change_listener:
            self.change_listener(self, field)

    def register_change_listener(self, callable):
        if self.change_listener and self.change_listener != callable:
            raise Exception('The change listener has already been set.')
        self.change_listener = callable

    def unregister_change_listener(self, callable):
        self.change_listener = None


def id2(obj):
    if obj is None:
        return 'None'
    return obj.id2
