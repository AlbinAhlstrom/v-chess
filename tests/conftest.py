import os
# Force a separate test database before importing app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_chess.db"

from hypothesis import strategies as st
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db

# ... (rest of imports)

# ... (strategies)

@pytest.fixture(scope="module", autouse=True)
async def setup_test_db():
    await init_db()
    yield
    # Optional: cleanup test db file after run
    if os.path.exists("test_chess.db"):
        try: os.remove("test_chess.db")
        except: pass

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
