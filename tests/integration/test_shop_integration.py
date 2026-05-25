# tests/integration/test_shop_integration.py
"""
Testes de Integração para Shop/Inventory (UC05-UC11)

Validam cadastro, leitura, atualização, exclusão de items e compras.
Meta de cobertura: 75%+
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


class TestCadastroItem:
    """IT-UC05-001, IT-UC05-002, IT-UC05-003: Admin cadastro items"""

    def test_admin_cadastra_item_sucesso_http_201(self, client: TestClient, db_session: Session):
        """IT-UC05-001: Admin cadastra item com sucesso retorna HTTP 201"""
        # Criar admin
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, is_admin)
                VALUES (:nome, :email, :senha, 1)
            """),
            {"nome": "Admin", "email": "admin@test.com", "senha": "hash"}
        )
        db_session.commit()

        # Headers com admin (em produção seria JWT)
        headers = {"X-Admin-Token": "valid_token"}

        payload = {
            "nome": "Poção de Vida",
            "descricao": "Restaura 20 pontos de vida",
            "preco": 50.0
        }
        response = client.post("/loja/itens", json=payload, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == "Poção de Vida"
        assert data["preco"] == 50.0

    def test_nao_admin_cadastra_item_http_403(self, client: TestClient):
        """IT-UC05-002: Não-admin não consegue cadastrar item"""
        payload = {
            "nome": "Poção de Vida",
            "descricao": "Restaura 20 pontos de vida",
            "preco": 50.0
        }
        response = client.post("/loja/itens", json=payload)

        assert response.status_code == 403
        assert "permissao" in response.json()["detail"].lower()

    def test_cadastro_item_preco_negativo_http_400(self, client: TestClient):
        """IT-UC05-003: Rejeitar preço negativo"""
        headers = {"X-Admin-Token": "valid_token"}
        payload = {
            "nome": "Item Invalido",
            "descricao": "Descrição",
            "preco": -10.0
        }
        response = client.post("/loja/itens", json=payload, headers=headers)

        assert response.status_code == 400
        assert "preco" in response.json()["detail"].lower()


class TestListarLoja:
    """IT-UC06-001, IT-UC06-002: Listar items da loja"""

    def test_listar_loja_vazia_http_200(self, client: TestClient):
        """IT-UC06-001: Listar loja vazia retorna lista vazia"""
        response = client.get("/loja/itens")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_listar_loja_com_items_http_200(self, client: TestClient, db_session: Session):
        """IT-UC06-002: Listar loja com items retorna lista com dados"""
        # Inserir items
        db_session.execute(
            text("""
                INSERT INTO item (nome, descricao, preco)
                VALUES (:nome, :descricao, :preco)
            """),
            {
                "nome": "Poção de Vida",
                "descricao": "Restaura 20 HP",
                "preco": 50.0
            }
        )
        db_session.execute(
            text("""
                INSERT INTO item (nome, descricao, preco)
                VALUES (:nome, :descricao, :preco)
            """),
            {
                "nome": "Super Poção",
                "descricao": "Restaura 50 HP",
                "preco": 100.0
            }
        )
        db_session.commit()

        response = client.get("/loja/itens")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["nome"] == "Poção de Vida"
        assert data[1]["nome"] == "Super Poção"


class TestAtualizacaoItem:
    """IT-UC07-001, IT-UC07-002, IT-UC07-003: Admin atualiza items"""

    def test_admin_atualiza_item_sucesso_http_200(self, client: TestClient, db_session: Session):
        """IT-UC07-001: Admin atualiza item com sucesso"""
        # Inserir item
        db_session.execute(
            text("""
                INSERT INTO item (nome, descricao, preco)
                VALUES (:nome, :descricao, :preco)
            """),
            {"nome": "Poção", "descricao": "HP", "preco": 50.0}
        )
        db_session.commit()
        item_id = db_session.execute(
            text("SELECT id FROM item WHERE nome = 'Poção'")
        ).scalar()

        headers = {"X-Admin-Token": "valid_token"}
        payload = {
            "nome": "Poção Atualizada",
            "descricao": "Nova descrição",
            "preco": 75.0
        }
        response = client.put(f"/loja/itens/{item_id}", json=payload, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "Poção Atualizada"
        assert data["preco"] == 75.0

    def test_nao_admin_atualiza_item_http_403(self, client: TestClient, db_session: Session):
        """IT-UC07-002: Não-admin não consegue atualizar item"""
        # Inserir item
        db_session.execute(
            text("""
                INSERT INTO item (nome, descricao, preco)
                VALUES (:nome, :descricao, :preco)
            """),
            {"nome": "Poção", "descricao": "HP", "preco": 50.0}
        )
        db_session.commit()
        item_id = db_session.execute(
            text("SELECT id FROM item WHERE nome = 'Poção'")
        ).scalar()

        payload = {"nome": "Nova Nome", "descricao": "Desc", "preco": 60.0}
        response = client.put(f"/loja/itens/{item_id}", json=payload)

        assert response.status_code == 403

    def test_atualizar_item_inexistente_http_404(self, client: TestClient):
        """IT-UC07-003: Tentar atualizar item inexistente retorna 404"""
        headers = {"X-Admin-Token": "valid_token"}
        payload = {"nome": "Item", "descricao": "Desc", "preco": 10.0}
        response = client.put("/loja/itens/99999", json=payload, headers=headers)

        assert response.status_code == 404


class TestAlterarPreco:
    """IT-UC08-001, IT-UC08-002: Admin altera preço"""

    def test_admin_altera_preco_sucesso_http_200(self, client: TestClient, db_session: Session):
        """IT-UC08-001: Admin altera preço com sucesso"""
        # Inserir item
        db_session.execute(
            text("""
                INSERT INTO item (nome, descricao, preco)
                VALUES (:nome, :descricao, :preco)
            """),
            {"nome": "Poção", "descricao": "HP", "preco": 50.0}
        )
        db_session.commit()
        item_id = db_session.execute(
            text("SELECT id FROM item WHERE nome = 'Poção'")
        ).scalar()

        headers = {"X-Admin-Token": "valid_token"}
        payload = {"novo_preco": 100.0}
        response = client.put(f"/loja/itens/{item_id}/preco", json=payload, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["preco"] == 100.0

    def test_altera_preco_negativo_http_400(self, client: TestClient, db_session: Session):
        """IT-UC08-002: Rejeitar preço negativo"""
        # Inserir item
        db_session.execute(
            text("""
                INSERT INTO item (nome, descricao, preco)
                VALUES (:nome, :descricao, :preco)
            """),
            {"nome": "Poção", "descricao": "HP", "preco": 50.0}
        )
        db_session.commit()
        item_id = db_session.execute(
            text("SELECT id FROM item WHERE nome = 'Poção'")
        ).scalar()

        headers = {"X-Admin-Token": "valid_token"}
        payload = {"novo_preco": -50.0}
        response = client.put(f"/loja/itens/{item_id}/preco", json=payload, headers=headers)

        assert response.status_code == 400


class TestDeletarItem:
    """IT-UC09-001, IT-UC09-002: Admin deleta items"""

    def test_admin_deleta_item_sucesso_http_200(self, client: TestClient, db_session: Session):
        """IT-UC09-001: Admin deleta item com sucesso"""
        # Inserir item
        db_session.execute(
            text("""
                INSERT INTO item (nome, descricao, preco)
                VALUES (:nome, :descricao, :preco)
            """),
            {"nome": "Poção", "descricao": "HP", "preco": 50.0}
        )
        db_session.commit()
        item_id = db_session.execute(
            text("SELECT id FROM item WHERE nome = 'Poção'")
        ).scalar()

        headers = {"X-Admin-Token": "valid_token"}
        response = client.delete(f"/loja/itens/{item_id}", headers=headers)

        assert response.status_code == 200
        assert "deletado" in response.json()["mensagem"].lower()

        # Validar que foi deletado
        item = db_session.execute(
            text("SELECT id FROM item WHERE id = :id"),
            {"id": item_id}
        ).fetchone()
        assert item is None

    def test_nao_admin_deleta_item_http_403(self, client: TestClient, db_session: Session):
        """IT-UC09-002: Não-admin não consegue deletar item"""
        # Inserir item
        db_session.execute(
            text("""
                INSERT INTO item (nome, descricao, preco)
                VALUES (:nome, :descricao, :preco)
            """),
            {"nome": "Poção", "descricao": "HP", "preco": 50.0}
        )
        db_session.commit()
        item_id = db_session.execute(
            text("SELECT id FROM item WHERE nome = 'Poção'")
        ).scalar()

        response = client.delete(f"/loja/itens/{item_id}")

        assert response.status_code == 403


class TestCompraItem:
    """IT-UC10-001, IT-UC10-002, IT-UC10-003: Jogador compra items"""

    def test_jogador_compra_item_saldo_suficiente_http_200(self, client: TestClient, db_session: Session):
        """IT-UC10-001: Jogador compra item com saldo suficiente"""
        # Criar jogador com saldo
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, saldo)
                VALUES (:nome, :email, :senha, :saldo)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash", "saldo": 100.0}
        )
        db_session.commit()
        jogador_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'joao@test.com'")
        ).scalar()

        # Criar item
        db_session.execute(
            text("""
                INSERT INTO item (nome, descricao, preco)
                VALUES (:nome, :descricao, :preco)
            """),
            {"nome": "Poção", "descricao": "HP", "preco": 50.0}
        )
        db_session.commit()
        item_id = db_session.execute(
            text("SELECT id FROM item WHERE nome = 'Poção'")
        ).scalar()

        # Comprar
        response = client.post(f"/inventario/comprar/{jogador_id}/{item_id}")

        assert response.status_code == 200
        assert "comprado com sucesso" in response.json()["mensagem"].lower()

        # Validar saldo foi debitado
        jogador = db_session.execute(
            text("SELECT saldo FROM jogador WHERE id = :id"),
            {"id": jogador_id}
        ).fetchone()
        assert jogador.saldo == 50.0  # 100 - 50

    def test_jogador_compra_item_saldo_insuficiente_http_400(self, client: TestClient, db_session: Session):
        """IT-UC10-002: Rejeitar compra com saldo insuficiente"""
        # Criar jogador com saldo baixo
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, saldo)
                VALUES (:nome, :email, :senha, :saldo)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash", "saldo": 10.0}
        )
        db_session.commit()
        jogador_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'joao@test.com'")
        ).scalar()

        # Criar item caro
        db_session.execute(
            text("""
                INSERT INTO item (nome, descricao, preco)
                VALUES (:nome, :descricao, :preco)
            """),
            {"nome": "Poção", "descricao": "HP", "preco": 100.0}
        )
        db_session.commit()
        item_id = db_session.execute(
            text("SELECT id FROM item WHERE nome = 'Poção'")
        ).scalar()

        # Tentar comprar
        response = client.post(f"/inventario/comprar/{jogador_id}/{item_id}")

        assert response.status_code == 400
        assert "saldo insuficiente" in response.json()["detail"].lower()

    def test_jogador_compra_item_inexistente_http_404(self, client: TestClient, db_session: Session):
        """IT-UC10-003: Tentar comprar item inexistente retorna 404"""
        # Criar jogador
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, saldo)
                VALUES (:nome, :email, :senha, :saldo)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash", "saldo": 100.0}
        )
        db_session.commit()
        jogador_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'joao@test.com'")
        ).scalar()

        # Tentar comprar item inexistente
        response = client.post(f"/inventario/comprar/{jogador_id}/99999")

        assert response.status_code == 404


class TestListarInventario:
    """IT-UC11-001: Listar inventário do jogador"""

    def test_listar_inventario_vazio_http_200(self, client: TestClient, db_session: Session):
        """IT-UC11-001: Listar inventário vazio retorna lista vazia"""
        # Criar jogador
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash"}
        )
        db_session.commit()
        jogador_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'joao@test.com'")
        ).scalar()

        response = client.get(f"/inventario/{jogador_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_listar_inventario_com_items_http_200(self, client: TestClient, db_session: Session):
        """Listar inventário com items"""
        # Criar jogador com saldo
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, saldo)
                VALUES (:nome, :email, :senha, :saldo)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash", "saldo": 200.0}
        )
        db_session.commit()
        jogador_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'joao@test.com'")
        ).scalar()

        # Criar items
        db_session.execute(
            text("""
                INSERT INTO item (nome, descricao, preco)
                VALUES (:nome, :descricao, :preco)
            """),
            {"nome": "Poção 1", "descricao": "HP", "preco": 50.0}
        )
        db_session.execute(
            text("""
                INSERT INTO item (nome, descricao, preco)
                VALUES (:nome, :descricao, :preco)
            """),
            {"nome": "Poção 2", "descricao": "HP", "preco": 75.0}
        )
        db_session.commit()

        item_id_1 = db_session.execute(
            text("SELECT id FROM item WHERE nome = 'Poção 1'")
        ).scalar()
        item_id_2 = db_session.execute(
            text("SELECT id FROM item WHERE nome = 'Poção 2'")
        ).scalar()

        # Comprar items
        client.post(f"/inventario/comprar/{jogador_id}/{item_id_1}")
        client.post(f"/inventario/comprar/{jogador_id}/{item_id_2}")

        # Listar inventário
        response = client.get(f"/inventario/{jogador_id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(item["nome"] == "Poção 1" for item in data)
        assert any(item["nome"] == "Poção 2" for item in data)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
