import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session

from backend.main import app
from backend.db.session import get_session

# SQLite em memória (zera a cada execução)
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    yield TestClient(app)

    app.dependency_overrides.clear()
