import pytest
from sqlalchemy import text

from app.routers.game import dar_aula


def seed_jogador(db_session, nome="Jogador", email="game@example.com", senha="123", saldo=0):
    db_session.execute(
        text(
            """
            INSERT INTO jogador (nome, email, senha_hash, saldo)
            VALUES (:nome, :email, :senha, :saldo)
            """
        ),
        {"nome": nome, "email": email, "senha": senha, "saldo": saldo},
    )
    db_session.commit()
    return db_session.execute(
        text("SELECT id FROM jogador WHERE email = :email"),
        {"email": email},
    ).scalar()


def seed_item(db_session, nome="Cafe", preco=100.0, multiplicador=1.0):
    db_session.execute(
        text(
            """
            INSERT INTO item (nome, descricao, preco, multiplicador, tipo, raridade, vendivel, ativo)
            VALUES (:nome, '', :preco, :multiplicador, 'equipamento', 'comum', 1, 1)
            """
        ),
        {"nome": nome, "preco": preco, "multiplicador": multiplicador},
    )
    db_session.commit()
    return db_session.execute(
        text("SELECT id FROM item WHERE nome = :nome"),
        {"nome": nome},
    ).scalar()


def seed_inventario(db_session, jogador_id, item_id):
    db_session.execute(
        text(
            """
            INSERT INTO inventario (jogador_id, item_id, ativo)
            VALUES (:jogador_id, :item_id, 1)
            """
        ),
        {"jogador_id": jogador_id, "item_id": item_id},
    )
    db_session.commit()


def test_dar_aula_ganho_base_sem_itens(db_session):
    jogador_id = seed_jogador(db_session, saldo=0)

    resposta = dar_aula(jogador_id, db_session)

    assert resposta["ganho"] == 10.0
    assert resposta["novo_saldo"] == 10.0


def test_dar_aula_soma_multiplicadores(db_session):
    jogador_id = seed_jogador(db_session, saldo=5)
    item_id = seed_item(db_session, nome="Cafe", multiplicador=2.0)
    item_id_2 = seed_item(db_session, nome="Lapis", multiplicador=1.5)
    seed_inventario(db_session, jogador_id, item_id)
    seed_inventario(db_session, jogador_id, item_id_2)

    resposta = dar_aula(jogador_id, db_session)

    assert resposta["ganho"] == pytest.approx(13.5)
    assert resposta["novo_saldo"] == pytest.approx(18.5)
