
class Changeable(object):
    def __init__(self, *args, **kwargs):
        self.attr_changed = list()
        super(Changeable, self).__init__(*args, **kwargs)

    def _on_attr_changed(self, field):
        if self.attr_changed:
            for callable in self.attr_changed:
                callable(self, field)

    def register_change_listener(self, callable):
        if callable not in self.attr_changed:
            self.attr_changed.append(callable)

    def unregister_change_listener(self, callable):
        if callable in self.attr_changed:
            self.attr_changed.remove(callable)


def id2(obj):
    if obj is None:
        return 'None'
    return obj.id2
