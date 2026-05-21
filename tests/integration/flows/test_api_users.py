import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Evita a abordagem "Big Bang": cria um banco SQLite em memória isolado apenas para o contexto dos testes
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_registro_usuario_integracao_banco():
    payload = {"email": "carvalho@lab.com", "senha": "123", "nome": "Carvalho"}
    response = client.post("/users/register", json=payload)
    
    assert response.status_code in [200, 201]
    assert response.json()["email"] == payload["email"]

    # Valida comportamento da API contra a restrição UNIQUE do banco
    response_duplicado = client.post("/users/register", json=payload)
    assert response_duplicado.status_code == 400