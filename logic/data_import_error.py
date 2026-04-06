
class DataImportError(Exception):
    def __init__(self, message, obj=None, exc=None):
        if obj:
            message = f'{message}: {obj}'
        if exc:
            message = f'{message}: {exc}'
        super().__init__(message)
        self.obj = obj
        self.exc = exc
