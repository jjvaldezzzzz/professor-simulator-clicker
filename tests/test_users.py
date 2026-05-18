from sqlalchemy import text


def seed_jogador(db_session, nome="Jogador", email="jogador@example.com", senha="123"):
	db_session.execute(
		text(
			"""
			INSERT INTO jogador (nome, email, senha_hash)
			VALUES (:nome, :email, :senha)
			"""
		),
		{"nome": nome, "email": email, "senha": senha},
	)
	db_session.commit()
	return db_session.execute(
		text("SELECT id FROM jogador WHERE email = :email"),
		{"email": email},
	).scalar()


def test_atualizar_perfil_valido(client, db_session):
	jogador_id = seed_jogador(db_session)

	response = client.put(
		f"/jogadores/{jogador_id}/perfil",
		json={"nome_exibicao": "Mestre do Postgres"},
	)

	assert response.status_code == 200
	data = response.json()
	assert data["novo_nome_exibicao"] == "Mestre do Postgres"


def test_atualizar_perfil_invalido(client, db_session):
	jogador_id = seed_jogador(db_session, email="outro@example.com")

	response = client.put(
		f"/jogadores/{jogador_id}/perfil",
		json={"nome_exibicao": "Nome@Invalido"},
	)

	assert response.status_code == 400
	assert "caracteres invalidos" in response.json()["detail"]
