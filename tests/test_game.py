from sqlalchemy import text


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


def test_dar_aula_sem_itens(client, db_session):
	jogador_id = seed_jogador(db_session, saldo=0)

	response = client.post(f"/jogo/{jogador_id}/dar-aula")

	assert response.status_code == 200
	data = response.json()
	assert data["ganho"] == 10.0
	assert data["novo_saldo"] == 10.0
