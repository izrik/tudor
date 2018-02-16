import unittest

from tudor import generate_app


class PersistenceLayerTestBase(unittest.TestCase):
    def generate_pl(self, db_uri='sqlite://'):
        app = generate_app(db_uri=db_uri)
        return app.pl
