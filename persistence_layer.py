
class PersistenceLayer(object):
    def __init__(self, ds, db):
        self.ds = ds
        self.db = db

    def add(self, obj):
        self.db.session.add(obj)

    def delete(self, obj):
        self.db.session.delete(obj)

    def commit(self):
        self.db.session.commit()
