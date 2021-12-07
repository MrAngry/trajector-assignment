import pytest
from starlette.testclient import TestClient
from tortoise import Tortoise
from tortoise.contrib.test import getDBConfig, _init_db

from main import app


@pytest.fixture(scope="function", autouse=True)
def setup_teardown_db(event_loop):
    _CONFIG = getDBConfig(app_label="models", modules=['models.item', 'models.tag'])
    loop = event_loop
    loop.run_until_complete(_init_db(_CONFIG))
    yield
    loop.run_until_complete(Tortoise._drop_databases())

@pytest.fixture(scope="session")
def client():
    return TestClient(app)