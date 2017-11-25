
class MockFileObject(object):
    def __init__(self, filename):
        self.filename = filename
        self.save_calls = []

    def save(self, filepath):
        self.save_calls.append(filepath)
