
class Changeable(object):
    def __init__(self, *args, **kwargs):
        self.attr_changed = list()
        super(Changeable, self).__init__(*args, **kwargs)

    def _on_attr_changed(self):
        if self.attr_changed:
            for callable in self.attr_changed:
                callable(self)