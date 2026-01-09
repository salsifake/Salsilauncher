import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from backend.main import app
from backend.db.session import get_session

# Fixtures
from fixtures.jogo_fixtures import *
from fixtures.colecao_fixtures import *


# ---------------------------------------------------------------------
# Banco de dados de testes (SQLite em memória)
# ---------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# ---------------------------------------------------------------------
# Fixture de session (escopo por teste)
# ---------------------------------------------------------------------

@pytest.fixture()
def session():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


# ---------------------------------------------------------------------
# Override da dependência do FastAPI
# ---------------------------------------------------------------------

@pytest.fixture()
def client(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
