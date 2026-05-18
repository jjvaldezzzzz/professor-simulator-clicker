from sqlalchemy import text


def seed_jogador(db_session, nome="Jogador", email="inv@example.com", senha="123", saldo=0):
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


def test_comprar_item_sem_saldo(client, db_session):
    jogador_id = seed_jogador(db_session, saldo=5)
    item_id = seed_item(db_session, preco=100.0)

    response = client.post(f"/inventario/comprar/{jogador_id}/{item_id}")

    assert response.status_code == 400
    assert "Saldo insuficiente" in response.json()["detail"]
