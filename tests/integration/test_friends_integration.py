import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

class TestAdicionarAmigo:
    def test_adicionar_amigo_bilateral_http_201(self, client: TestClient, db_session: Session):
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash) VALUES ('A', 'a@t.com', 'hash')"))
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash) VALUES ('B', 'b@t.com', 'hash')"))
        db_session.commit()

        j1 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'a@t.com'")).scalar()
        j2 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'b@t.com'")).scalar()

        # O endpoint /amigos/adicionar requer POST Body: { "jogador_id": ..., "amigo_id": ... }
        response = client.post("/amigos/adicionar", json={"jogador_id": j1, "amigo_id": j2})
        assert response.status_code in (200, 201)

class TestObterAmigos:
    def test_obter_amigos_com_dados_http_200(self, client: TestClient, db_session: Session):
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash) VALUES ('A', 'a@t.com', 'hash')"))
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash) VALUES ('B', 'b@t.com', 'hash')"))
        db_session.commit()
        j1 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'a@t.com'")).scalar()
        j2 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'b@t.com'")).scalar()

        # Inserindo com as colunas corretas (jogador_id, amigo_id)
        db_session.execute(text("INSERT INTO amizade (jogador_id, amigo_id) VALUES (:j1, :j2)"), {"j1": j1, "j2": j2})
        db_session.commit()

        response = client.get(f"/amigos/{j1}")
        assert response.status_code == 200
        assert len(response.json()["amigos"]) == 1

class TestFavoritarAmigo:
    def test_favoritartar_amigo_sucesso_http_200(self, client: TestClient, db_session: Session):
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash) VALUES ('A', 'a@t.com', 'hash')"))
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash) VALUES ('B', 'b@t.com', 'hash')"))
        db_session.commit()
        j1 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'a@t.com'")).scalar()
        j2 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'b@t.com'")).scalar()
        
        db_session.execute(text("INSERT INTO amizade (jogador_id, amigo_id, favorito) VALUES (:j1, :j2, 0)"), {"j1": j1, "j2": j2})
        db_session.commit()
        amizade_id = db_session.execute(text("SELECT id FROM amizade")).scalar()

        # Espera json: {"jogador_id": ...}
        response = client.put(f"/amigos/{amizade_id}/favoritar", json={"jogador_id": j1})
        assert response.status_code == 200

class TestDesfavoritarAmigo:
    def test_desfavoritar_amigo_sucesso_http_200(self, client: TestClient, db_session: Session):
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash) VALUES ('A', 'a@t.com', 'hash')"))
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash) VALUES ('B', 'b@t.com', 'hash')"))
        db_session.commit()
        j1 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'a@t.com'")).scalar()
        j2 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'b@t.com'")).scalar()
        
        db_session.execute(text("INSERT INTO amizade (jogador_id, amigo_id, favorito) VALUES (:j1, :j2, 1)"), {"j1": j1, "j2": j2})
        db_session.commit()
        amizade_id = db_session.execute(text("SELECT id FROM amizade")).scalar()

        response = client.put(f"/amigos/{amizade_id}/desfavoritar", json={"jogador_id": j1})
        assert response.status_code == 200

class TestRemoverAmigo:
    def test_remover_amigo_sucesso_http_200(self, client: TestClient, db_session: Session):
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash) VALUES ('A', 'a@t.com', 'hash')"))
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash) VALUES ('B', 'b@t.com', 'hash')"))
        db_session.commit()
        j1 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'a@t.com'")).scalar()
        j2 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'b@t.com'")).scalar()
        db_session.execute(text("INSERT INTO amizade (jogador_id, amigo_id) VALUES (:j1, :j2)"), {"j1": j1, "j2": j2})
        db_session.commit()
        amizade_id = db_session.execute(text("SELECT id FROM amizade")).scalar()

        response = client.request("DELETE", f"/amigos/{amizade_id}", json={"jogador_id": j1})
        assert response.status_code == 200

class TestBuscarJogador:
    def test_buscar_jogador_por_nome_http_200(self, client: TestClient, db_session: Session):
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash) VALUES ('A', 'teste@b.com', 'hash')"))
        db_session.commit()

        # O endpoint real utiliza query param `email`
        response = client.post("/amigos/buscar?email=teste@b.com")
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])