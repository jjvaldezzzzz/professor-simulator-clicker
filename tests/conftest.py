import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite+pysqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON;"))
        conn.execute(text("DROP TABLE IF EXISTS transacao"))
        conn.execute(text("DROP TABLE IF EXISTS pokemon_time"))
        conn.execute(text("DROP TABLE IF EXISTS inventario"))
        conn.execute(text("DROP TABLE IF EXISTS item"))
        conn.execute(text("DROP TABLE IF EXISTS jogador"))

        conn.execute(text(
            """
            CREATE TABLE jogador (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                nome_exibicao TEXT DEFAULT 'Treinador Iniciante',
                saldo REAL DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                ultimo_login TEXT,
                ativo INTEGER DEFAULT 1
            )
            """
        ))

        conn.execute(text(
            """
            CREATE TABLE item (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                preco REAL NOT NULL,
                multiplicador REAL NOT NULL DEFAULT 1.0,
                tipo TEXT NOT NULL,
                raridade TEXT DEFAULT 'comum',
                vendivel INTEGER DEFAULT 1,
                ativo INTEGER DEFAULT 1
            )
            """
        ))

        conn.execute(text(
            """
            CREATE TABLE inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jogador_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                data_compra TEXT DEFAULT CURRENT_TIMESTAMP,
                ativo INTEGER DEFAULT 1,
                UNIQUE(jogador_id, item_id),
                FOREIGN KEY(jogador_id) REFERENCES jogador(id) ON DELETE CASCADE,
                FOREIGN KEY(item_id) REFERENCES item(id) ON DELETE RESTRICT
            )
            """
        ))

        conn.execute(text(
            """
            CREATE TABLE pokemon_time (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jogador_id INTEGER NOT NULL,
                pokemon_api_id INTEGER NOT NULL,
                nome_pokemon TEXT NOT NULL,
                sprite_url TEXT,
                apelido TEXT,
                data_obtido TEXT DEFAULT CURRENT_TIMESTAMP,
                ativo INTEGER DEFAULT 1,
                FOREIGN KEY(jogador_id) REFERENCES jogador(id) ON DELETE CASCADE
            )
            """
        ))

        conn.execute(text(
            """
            CREATE TABLE transacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jogador_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                valor REAL NOT NULL,
                descricao TEXT,
                data_transacao TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(jogador_id) REFERENCES jogador(id) ON DELETE CASCADE
            )
            """
        ))


@pytest.fixture()
def db_session():
    init_db()
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
