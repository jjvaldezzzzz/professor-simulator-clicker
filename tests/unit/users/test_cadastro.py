import pytest
from fastapi import HTTPException
from sqlalchemy import text

from app import schemas
from app.routers.users import cadastrar_jogador


def fetch_jogador(db_session, email):
    return db_session.execute(
        text(
            """
            SELECT id, nome, email, nome_exibicao, saldo
            FROM jogador
            WHERE email = :email
            """
        ),
        {"email": email},
    ).fetchone()


def test_cadastrar_jogador_persiste_dados(db_session):
    jogador = schemas.JogadorCreate(nome="Ana", email="ana@example.com", senha="123")

    resposta = cadastrar_jogador(jogador, db_session)

    assert resposta["email"] == "ana@example.com"
    assert resposta["nome_exibicao"] == "Treinador Iniciante"

    row = fetch_jogador(db_session, "ana@example.com")
    assert row is not None
    assert row.nome == "Ana"
    assert row.nome_exibicao == "Treinador Iniciante"


def test_cadastrar_jogador_email_duplicado(db_session):
    jogador = schemas.JogadorCreate(nome="Ana", email="ana@example.com", senha="123")
    cadastrar_jogador(jogador, db_session)

    with pytest.raises(HTTPException) as exc:
        cadastrar_jogador(jogador, db_session)

    assert exc.value.status_code == 400
    assert "Email" in str(exc.value.detail)
