from sqlalchemy import text


def seed_jogador(db_session, nome="Jogador", email="flow@example.com", senha="123", saldo=0):
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


def seed_item(db_session, nome="Cafe", preco=100.0, multiplicador=2.0):
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


def test_fluxo_dar_aula_atualiza_saldo_e_transacao(client, db_session):
    jogador_id = seed_jogador(db_session, saldo=0)
    item_id = seed_item(db_session, multiplicador=2.0)
    seed_inventario(db_session, jogador_id, item_id)

    response = client.post(f"/jogo/{jogador_id}/dar-aula")

    assert response.status_code == 200
    data = response.json()
    assert data["ganho"] == 12.0
    assert data["novo_saldo"] == 12.0

    saldo = db_session.execute(
        text("SELECT saldo FROM jogador WHERE id = :id"),
        {"id": jogador_id},
    ).scalar()
    assert saldo == 12.0

    transacoes = db_session.execute(
        text("SELECT tipo, valor FROM transacao WHERE jogador_id = :id"),
        {"id": jogador_id},
    ).fetchall()

    assert len(transacoes) == 1
    assert transacoes[0].tipo == "ganho_aula"
    assert transacoes[0].valor == 12.0
