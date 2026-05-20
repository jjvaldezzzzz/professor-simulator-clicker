import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

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
        conn.execute(text("DROP TABLE IF EXISTS torneio_partida"))
        conn.execute(text("DROP TABLE IF EXISTS torneio_pokemon"))
        conn.execute(text("DROP TABLE IF EXISTS torneio_participante"))
        conn.execute(text("DROP TABLE IF EXISTS torneio"))
        conn.execute(text("DROP TABLE IF EXISTS pokemon_time"))
        conn.execute(text("DROP TABLE IF EXISTS time_pokemon"))
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
            CREATE TABLE time_pokemon (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jogador_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
                ativo INTEGER DEFAULT 1,
                FOREIGN KEY(jogador_id) REFERENCES jogador(id) ON DELETE CASCADE
            )
            """
        ))

        conn.execute(text(
            """
            CREATE TABLE pokemon_time (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jogador_id INTEGER NOT NULL,
                time_id INTEGER,
                pokemon_api_id INTEGER NOT NULL,
                nome_pokemon TEXT NOT NULL,
                sprite_url TEXT,
                apelido TEXT,
                data_obtido TEXT DEFAULT CURRENT_TIMESTAMP,
                ativo INTEGER DEFAULT 1,
                FOREIGN KEY(jogador_id) REFERENCES jogador(id) ON DELETE CASCADE,
                FOREIGN KEY(time_id) REFERENCES time_pokemon(id) ON DELETE SET NULL
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

        conn.execute(text(
            """
            CREATE TABLE torneio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jogador_id INTEGER NOT NULL,
                time_id INTEGER NOT NULL,
                tamanho INTEGER NOT NULL,
                custo REAL NOT NULL DEFAULT 1000.0,
                premio REAL NOT NULL DEFAULT 5000.0,
                status TEXT NOT NULL DEFAULT 'em_andamento',
                vencedor_participante_id INTEGER,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                finalizado_em TEXT,
                FOREIGN KEY(jogador_id) REFERENCES jogador(id) ON DELETE CASCADE,
                FOREIGN KEY(time_id) REFERENCES time_pokemon(id) ON DELETE RESTRICT
            )
            """
        ))

        conn.execute(text(
            """
            CREATE TABLE torneio_participante (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                torneio_id INTEGER NOT NULL,
                nome_treinador TEXT NOT NULL,
                nome_time TEXT NOT NULL,
                total_bst INTEGER NOT NULL DEFAULT 0,
                ordem INTEGER NOT NULL,
                is_bot INTEGER NOT NULL DEFAULT 1,
                jogador_id INTEGER,
                time_id INTEGER,
                FOREIGN KEY(torneio_id) REFERENCES torneio(id) ON DELETE CASCADE,
                FOREIGN KEY(jogador_id) REFERENCES jogador(id) ON DELETE SET NULL,
                FOREIGN KEY(time_id) REFERENCES time_pokemon(id) ON DELETE SET NULL
            )
            """
        ))

        conn.execute(text(
            """
            CREATE TABLE torneio_pokemon (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                torneio_participante_id INTEGER NOT NULL,
                pokemon_api_id INTEGER NOT NULL,
                nome_pokemon TEXT NOT NULL,
                sprite_url TEXT,
                bst INTEGER NOT NULL,
                FOREIGN KEY(torneio_participante_id) REFERENCES torneio_participante(id) ON DELETE CASCADE
            )
            """
        ))

        conn.execute(text(
            """
            CREATE TABLE torneio_partida (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                torneio_id INTEGER NOT NULL,
                rodada INTEGER NOT NULL,
                match_index INTEGER NOT NULL,
                participante_a_id INTEGER,
                participante_b_id INTEGER,
                vencedor_id INTEGER,
                resolvido_em TEXT,
                FOREIGN KEY(torneio_id) REFERENCES torneio(id) ON DELETE CASCADE,
                FOREIGN KEY(participante_a_id) REFERENCES torneio_participante(id) ON DELETE SET NULL,
                FOREIGN KEY(participante_b_id) REFERENCES torneio_participante(id) ON DELETE SET NULL,
                FOREIGN KEY(vencedor_id) REFERENCES torneio_participante(id) ON DELETE SET NULL
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
