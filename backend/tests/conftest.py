import pytest
from backend.app.core.database import init_db

# Initialize database schema before tests run
init_db()

@pytest.fixture(scope="session", autouse=True)
def test_db_setup():
    init_db()
    yield
