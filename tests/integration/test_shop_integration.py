import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

class TestCadastroItem:
    def test_admin_cadastra_item_sucesso_http_201(self, client: TestClient, db_session: Session):
        db_session.execute(
            text("INSERT INTO jogador (nome, email, senha_hash, is_admin) VALUES (:nome, :email, :senha, 1)"),
            {"nome": "Admin", "email": "admin@test.com", "senha": "hash"}
        )
        db_session.commit()
        admin_id = db_session.execute(text("SELECT id FROM jogador WHERE email = 'admin@test.com'")).scalar()

        payload = {"nome": "Poção de Vida", "descricao": "Restaura 20 HP", "preco": 50.0, "tipo": "consumivel"}
        response = client.post(f"/loja/itens?jogador_id={admin_id}", json=payload)

        assert response.status_code == 201
        assert response.json()["nome"] == "Poção de Vida"

    def test_nao_admin_cadastra_item_http_403(self, client: TestClient, db_session: Session):
        db_session.execute(
            text("INSERT INTO jogador (nome, email, senha_hash, is_admin) VALUES (:nome, :email, :senha, 0)"),
            {"nome": "Comum", "email": "comum@test.com", "senha": "hash"}
        )
        db_session.commit()
        comum_id = db_session.execute(text("SELECT id FROM jogador WHERE email = 'comum@test.com'")).scalar()

        payload = {"nome": "Poção de Vida", "descricao": "Restaura 20 HP", "preco": 50.0, "tipo": "consumivel"}
        response = client.post(f"/loja/itens?jogador_id={comum_id}", json=payload)
        assert response.status_code == 403

    def test_cadastro_item_preco_negativo_http_400(self, client: TestClient, db_session: Session):
        db_session.execute(
            text("INSERT INTO jogador (nome, email, senha_hash, is_admin) VALUES (:nome, :email, :senha, 1)"),
            {"nome": "Admin", "email": "admin@test.com", "senha": "hash"}
        )
        db_session.commit()
        admin_id = db_session.execute(text("SELECT id FROM jogador WHERE email = 'admin@test.com'")).scalar()

        payload = {"nome": "Item", "descricao": "Desc", "preco": -10.0, "tipo": "consumivel"}
        response = client.post(f"/loja/itens?jogador_id={admin_id}", json=payload)
        assert response.status_code == 400

class TestListarLoja:
    def test_listar_loja_vazia_http_200(self, client: TestClient):
        response = client.get("/loja/itens")
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_listar_loja_com_items_http_200(self, client: TestClient, db_session: Session):
        db_session.execute(text("INSERT INTO item (nome, descricao, preco, tipo) VALUES ('Poção', 'Restaura HP', 50.0, 'consumivel')"))
        db_session.commit()
        response = client.get("/loja/itens")
        assert response.status_code == 200
        assert len(response.json()) == 1

class TestAtualizacaoItem:
    def test_admin_atualiza_item_sucesso_http_200(self, client: TestClient, db_session: Session):
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash, is_admin) VALUES ('Admin', 'admin@t.com', 'h', 1)"))
        db_session.execute(text("INSERT INTO item (nome, descricao, preco, tipo) VALUES ('Poção', 'HP', 50.0, 'consumivel')"))
        db_session.commit()
        admin_id = db_session.execute(text("SELECT id FROM jogador WHERE email = 'admin@t.com'")).scalar()
        item_id = db_session.execute(text("SELECT id FROM item WHERE nome = 'Poção'")).scalar()

        payload = {"nome": "Poção Atualizada", "preco": 75.0, "tipo": "consumivel"}
        response = client.put(f"/loja/itens/{item_id}?jogador_id={admin_id}", json=payload)
        assert response.status_code == 200
        assert response.json()["nome"] == "Poção Atualizada"

class TestAlterarPreco:
    def test_admin_altera_preco_sucesso_http_200(self, client: TestClient, db_session: Session):
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash, is_admin) VALUES ('Admin', 'admin@t.com', 'h', 1)"))
        db_session.execute(text("INSERT INTO item (nome, descricao, preco, tipo) VALUES ('Poção', 'HP', 50.0, 'consumivel')"))
        db_session.commit()
        admin_id = db_session.execute(text("SELECT id FROM jogador WHERE email = 'admin@t.com'")).scalar()
        item_id = db_session.execute(text("SELECT id FROM item WHERE nome = 'Poção'")).scalar()

        response = client.put(f"/loja/itens/{item_id}/preco?novo_preco=100.0&jogador_id={admin_id}")
        assert response.status_code == 200
        assert response.json()["preco"] == 100.0

class TestDeletarItem:
    def test_admin_deleta_item_sucesso_http_200(self, client: TestClient, db_session: Session):
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash, is_admin) VALUES ('Admin', 'admin@t.com', 'h', 1)"))
        db_session.execute(text("INSERT INTO item (nome, descricao, preco, tipo) VALUES ('Poção', 'HP', 50.0, 'consumivel')"))
        db_session.commit()
        admin_id = db_session.execute(text("SELECT id FROM jogador WHERE email = 'admin@t.com'")).scalar()
        item_id = db_session.execute(text("SELECT id FROM item WHERE nome = 'Poção'")).scalar()

        response = client.delete(f"/loja/itens/{item_id}?jogador_id={admin_id}")
        assert response.status_code == 200

class TestCompraItem:
    def test_jogador_compra_item_saldo_suficiente_http_200(self, client: TestClient, db_session: Session):
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash, saldo) VALUES ('Joao', 'j@t.com', 'h', 100.0)"))
        db_session.execute(text("INSERT INTO item (nome, descricao, preco, tipo) VALUES ('Poção', 'HP', 50.0, 'consumivel')"))
        db_session.commit()
        j_id = db_session.execute(text("SELECT id FROM jogador")).scalar()
        i_id = db_session.execute(text("SELECT id FROM item")).scalar()

        response = client.post(f"/inventario/comprar/{j_id}/{i_id}")
        assert response.status_code == 200

class TestListarInventario:
    def test_listar_inventario_com_items_http_200(self, client: TestClient, db_session: Session):
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash, saldo) VALUES ('Joao', 'j@t.com', 'h', 200.0)"))
        db_session.execute(text("INSERT INTO item (nome, descricao, preco, tipo) VALUES ('Poção', 'HP', 50.0, 'consumivel')"))
        db_session.commit()
        j_id = db_session.execute(text("SELECT id FROM jogador")).scalar()
        i_id = db_session.execute(text("SELECT id FROM item")).scalar()

        client.post(f"/inventario/comprar/{j_id}/{i_id}")
        response = client.get(f"/inventario/{j_id}")
        assert response.status_code == 200
        assert len(response.json()) == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])