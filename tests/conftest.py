import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock, patch

os.environ["API_KEY"] = "test-secret"

from database import Base, get_db
from main import app

TEST_API_HEADERS = {"X-API-Key": "test-secret"}

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    yield
    from dependencies import limiter
    limiter._storage.reset()


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, headers=TEST_API_HEADERS) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def mock_task():
    mock_result = MagicMock()
    mock_result.id = "test-job-id"
    with patch("routers.messages.process_message") as mock:
        mock.delay.return_value = mock_result
        yield mock


@pytest.fixture
def mock_chat():
    with patch("tasks.chat", return_value="mocked assistant reply") as m:
        yield m
