import unittest
import pytest
from sqlalchemy import create_engine

from tudor import generate_app


def get_postgresql_url(postgresql):
    info = postgresql.info
    return f"postgresql://{info.user}:{info.password}@{info.host}:{info.port}/{info.dbname}"


class PersistenceLayerTestBase(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def _setup(self, postgresql):
        url = get_postgresql_url(postgresql)
        self.pl = self.generate_pl(db_uri=url)
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
