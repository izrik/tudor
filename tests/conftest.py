import pytest

from .util import pop_app_contexts


@pytest.fixture(autouse=True)
def _pop_app_contexts():
    yield
    pop_app_contexts()
