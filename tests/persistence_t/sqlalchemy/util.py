import unittest

from tudor import generate_app


class PersistenceLayerTestBase(unittest.TestCase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.pl.create_all()

    def tearDown(self):
        if hasattr(self, 'app_context'):
            self.app_context.pop()

    def generate_pl(self, db_uri='sqlite://'):
        app = generate_app(db_uri=db_uri)
        self.app = app
        return app.pl
