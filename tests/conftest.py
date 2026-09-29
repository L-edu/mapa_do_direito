"""Fixtures: banco SQLite em arquivo temporário, recriado a cada sessão de testes."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "teste.db")

from app.config import settings  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

engine_teste = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}, future=True
)
SessionTeste = sessionmaker(bind=engine_teste, autoflush=False, autocommit=False, future=True)


@pytest.fixture(scope="session", autouse=True)
def preparar_banco():
    Base.metadata.drop_all(bind=engine_teste)
    Base.metadata.create_all(bind=engine_teste)

    def get_db_teste():
        db = SessionTeste()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_db_teste

    from app.core.seguranca import gerar_hash_senha
    from app.models import Parametro, Programa, Regra, Usuario
    from app.seed import PARAMETROS, PROGRAMAS, USUARIOS

    db = SessionTeste()
    for dados in PARAMETROS:
        db.add(Parametro(**dados))
    for dados in USUARIOS:
        db.add(
            Usuario(
                nome=dados["nome"],
                email=dados["email"],
                senha_hash=gerar_hash_senha(dados["senha"]),
                papel=dados["papel"],
            )
        )
    for dados in PROGRAMAS:
        copia = dict(dados)
        regras = copia.pop("regras")
        programa = Programa(**copia)
        programa.regras = [Regra(**r) for r in regras]
        db.add(programa)
    db.commit()
    db.close()
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _token(client, email, senha):
    resposta = client.post("/api/v1/auth/login", json={"email": email, "senha": senha})
    assert resposta.status_code == 200, resposta.text
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


@pytest.fixture
def auth_admin(client):
    return _token(client, "admin@mapadodireito.org", "admin12345")


@pytest.fixture
def auth_assistente(client):
    return _token(client, "cras@mapadodireito.org", "cras12345")
