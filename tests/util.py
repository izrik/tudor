class MockFileObject(object):
    def __init__(self, filename, content=None):
        self.filename = filename
        self.content = content
        self.save_calls = []

    def save(self, filepath):
        self.save_calls.append(filepath)

    def read(self):
        return self.content
