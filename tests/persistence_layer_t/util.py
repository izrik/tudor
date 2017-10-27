import unittest

from tudor import generate_app


def generate_pl(db_uri='sqlite://'):
    app = generate_app(db_uri=db_uri)
    return app.pl


class PersistenceLayerTestBase(unittest.TestCase):
    pass