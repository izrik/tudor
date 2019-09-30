from io import StringIO


class MockFileObject(object):
    def __init__(self, filename, content=None):
        self.filename = filename
        self.content = content
        self._s = StringIO(content)
        self.save_calls = []

    def save(self, filepath):
        self.save_calls.append(filepath)

    def read(self, *args, **kwargs):
        return self._s.read(*args, **kwargs)
