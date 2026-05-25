# tests/integration/test_friends_integration.py
"""
Testes de Integração para Amigos (UC24-UC28)

Validam adição bilateral, listagem, favoritos e remoção de amigos.
Meta de cobertura: 75%+
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


class TestAdicionarAmigo:
    """IT-UC24-001, IT-UC24-002, IT-UC24-003: Adicionar amigo (bilateral)"""

    def test_adicionar_amigo_bilateral_http_201(self, client: TestClient, db_session: Session):
        """IT-UC24-001: Adicionar amigo cria amizade bilateral (A→B e B→A)"""
        # Criar 2 jogadores
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash"}
        )
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "Maria", "email": "maria@test.com", "senha": "hash"}
        )
        db_session.commit()

        jogador1_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'joao@test.com'")
        ).scalar()
        jogador2_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'maria@test.com'")
        ).scalar()

        # Adicionar amigo
        payload = {"amigo_id": jogador2_id}
        response = client.post(f"/amigos/adicionar/{jogador1_id}", json=payload)

        assert response.status_code == 201
        assert "amizade criada" in response.json()["mensagem"].lower()

        # Validar amizade bilateral
        amizades_forward = db_session.execute(
            text("""
                SELECT COUNT(*) FROM amizade 
                WHERE jogador_id = :j1_id AND amigo_id = :j2_id AND ativo = 1
            """),
            {"j1_id": jogador1_id, "j2_id": jogador2_id}
        ).scalar()
        
        amizades_backward = db_session.execute(
            text("""
                SELECT COUNT(*) FROM amizade 
                WHERE jogador_id = :j2_id AND amigo_id = :j1_id AND ativo = 1
            """),
            {"j2_id": jogador2_id, "j1_id": jogador1_id}
        ).scalar()

        assert amizades_forward == 1
        assert amizades_backward == 1

    def test_adicionar_amigo_ja_existe_http_400(self, client: TestClient, db_session: Session):
        """IT-UC24-002: Rejeitar adição de amigo que já existe"""
        # Criar 2 jogadores
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash"}
        )
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "Maria", "email": "maria@test.com", "senha": "hash"}
        )
        db_session.commit()

        jogador1_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'joao@test.com'")
        ).scalar()
        jogador2_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'maria@test.com'")
        ).scalar()

        # Criar amizade
        db_session.execute(
            text("""
                INSERT INTO amizade (jogador_id, amigo_id, ativo)
                VALUES (:jogador_id, :amigo_id, 1)
            """),
            {"jogador_id": jogador1_id, "amigo_id": jogador2_id}
        )
        db_session.commit()

        # Tentar adicionar novamente
        payload = {"amigo_id": jogador2_id}
        response = client.post(f"/amigos/adicionar/{jogador1_id}", json=payload)

        assert response.status_code == 400
        assert "ja e amigo" in response.json()["detail"].lower()

    def test_adicionar_jogador_inexistente_http_404(self, client: TestClient):
        """IT-UC24-003: Tentar adicionar jogador inexistente retorna 404"""
        payload = {"amigo_id": 99999}
        response = client.post("/amigos/adicionar/1", json=payload)
        assert response.status_code == 404


class TestObterAmigos:
    """IT-UC25-001, IT-UC25-002: Obter lista de amigos"""

    def test_obter_amigos_vazio_http_200(self, client: TestClient, db_session: Session):
        """IT-UC25-001: Obter amigos de jogador sem amigos retorna lista vazia"""
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

        response = client.get(f"/amigos/{jogador_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_obter_amigos_com_dados_http_200(self, client: TestClient, db_session: Session):
        """IT-UC25-002: Obter amigos com dados retorna lista com amigos"""
        # Criar 3 jogadores
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash"}
        )
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "Maria", "email": "maria@test.com", "senha": "hash"}
        )
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "Pedro", "email": "pedro@test.com", "senha": "hash"}
        )
        db_session.commit()

        j1 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'joao@test.com'")).scalar()
        j2 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'maria@test.com'")).scalar()
        j3 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'pedro@test.com'")).scalar()

        # Adicionar amizades
        db_session.execute(
            text("""
                INSERT INTO amizade (jogador_id, amigo_id, ativo)
                VALUES (:jogador_id, :amigo_id, 1)
            """),
            {"jogador_id": j1, "amigo_id": j2}
        )
        db_session.execute(
            text("""
                INSERT INTO amizade (jogador_id, amigo_id, ativo)
                VALUES (:jogador_id, :amigo_id, 1)
            """),
            {"jogador_id": j1, "amigo_id": j3}
        )
        db_session.commit()

        response = client.get(f"/amigos/{j1}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        nomes = [amigo["nome"] for amigo in data]
        assert "Maria" in nomes
        assert "Pedro" in nomes


class TestObterAmigosFavoritos:
    """IT-UC26-001, IT-UC26-002: Obter amigos favoritos"""

    def test_obter_amigos_favoritos_vazio_http_200(self, client: TestClient, db_session: Session):
        """IT-UC26-001: Obter favoritos vazio retorna lista vazia"""
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

        response = client.get(f"/amigos/{jogador_id}/favoritos")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_obter_amigos_favoritos_com_dados_http_200(self, client: TestClient, db_session: Session):
        """IT-UC26-002: Obter favoritos com dados"""
        # Setup
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash"}
        )
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "Maria", "email": "maria@test.com", "senha": "hash"}
        )
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "Pedro", "email": "pedro@test.com", "senha": "hash"}
        )
        db_session.commit()

        j1 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'joao@test.com'")).scalar()
        j2 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'maria@test.com'")).scalar()
        j3 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'pedro@test.com'")).scalar()

        # Adicionar amizades
        db_session.execute(
            text("""
                INSERT INTO amizade (jogador_id, amigo_id, ativo, favorito)
                VALUES (:jogador_id, :amigo_id, 1, :favorito)
            """),
            {"jogador_id": j1, "amigo_id": j2, "favorito": 1}
        )
        db_session.execute(
            text("""
                INSERT INTO amizade (jogador_id, amigo_id, ativo, favorito)
                VALUES (:jogador_id, :amigo_id, 1, :favorito)
            """),
            {"jogador_id": j1, "amigo_id": j3, "favorito": 0}
        )
        db_session.commit()

        response = client.get(f"/amigos/{j1}/favoritos")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["nome"] == "Maria"


class TestFavoritarAmigo:
    """IT-UC27-001, IT-UC27-002: Marcar amigo como favorito"""

    def test_favoritartar_amigo_sucesso_http_200(self, client: TestClient, db_session: Session):
        """IT-UC27-001: Marcar amigo como favorito com sucesso"""
        # Setup
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash"}
        )
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "Maria", "email": "maria@test.com", "senha": "hash"}
        )
        db_session.commit()

        j1 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'joao@test.com'")).scalar()
        j2 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'maria@test.com'")).scalar()

        # Criar amizade
        db_session.execute(
            text("""
                INSERT INTO amizade (jogador_id, amigo_id, ativo, favorito)
                VALUES (:jogador_id, :amigo_id, 1, 0)
            """),
            {"jogador_id": j1, "amigo_id": j2}
        )
        db_session.commit()

        amizade_id = db_session.execute(
            text("""
                SELECT id FROM amizade 
                WHERE jogador_id = :j1_id AND amigo_id = :j2_id
            """),
            {"j1_id": j1, "j2_id": j2}
        ).scalar()

        # Favoritartar
        response = client.put(f"/amigos/{amizade_id}/favoritartar")

        assert response.status_code == 200
        assert "favorito" in response.json()["mensagem"].lower()

    def test_favoritartar_amizade_inexistente_http_404(self, client: TestClient):
        """IT-UC27-002: Favoritartar amizade inexistente retorna 404"""
        response = client.put("/amigos/99999/favoritartar")
        assert response.status_code == 404


class TestDesfavoritarAmigo:
    """IT-UC28-001, IT-UC28-002: Remover de favoritos"""

    def test_desfavoritartar_amigo_sucesso_http_200(self, client: TestClient, db_session: Session):
        """IT-UC28-001: Remover de favoritos com sucesso"""
        # Setup
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash"}
        )
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "Maria", "email": "maria@test.com", "senha": "hash"}
        )
        db_session.commit()

        j1 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'joao@test.com'")).scalar()
        j2 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'maria@test.com'")).scalar()

        # Criar amizade favorita
        db_session.execute(
            text("""
                INSERT INTO amizade (jogador_id, amigo_id, ativo, favorito)
                VALUES (:jogador_id, :amigo_id, 1, 1)
            """),
            {"jogador_id": j1, "amigo_id": j2}
        )
        db_session.commit()

        amizade_id = db_session.execute(
            text("""
                SELECT id FROM amizade 
                WHERE jogador_id = :j1_id AND amigo_id = :j2_id
            """),
            {"j1_id": j1, "j2_id": j2}
        ).scalar()

        # Desfavoritartar
        response = client.put(f"/amigos/{amizade_id}/desfavoritartar")

        assert response.status_code == 200
        assert "removido" in response.json()["mensagem"].lower()

    def test_desfavoritartar_amizade_inexistente_http_404(self, client: TestClient):
        """IT-UC28-002: Desfavoritartar amizade inexistente retorna 404"""
        response = client.put("/amigos/99999/desfavoritartar")
        assert response.status_code == 404


class TestRemoverAmigo:
    """Bonus: Remover amigo (soft delete via ativo = 0)"""

    def test_remover_amigo_sucesso_http_200(self, client: TestClient, db_session: Session):
        """Remover amigo com sucesso (soft delete bilateral)"""
        # Setup
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash"}
        )
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash)
                VALUES (:nome, :email, :senha)
            """),
            {"nome": "Maria", "email": "maria@test.com", "senha": "hash"}
        )
        db_session.commit()

        j1 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'joao@test.com'")).scalar()
        j2 = db_session.execute(text("SELECT id FROM jogador WHERE email = 'maria@test.com'")).scalar()

        # Criar amizade bilateral
        db_session.execute(
            text("""
                INSERT INTO amizade (jogador_id, amigo_id, ativo)
                VALUES (:jogador_id, :amigo_id, 1)
            """),
            {"jogador_id": j1, "amigo_id": j2}
        )
        db_session.execute(
            text("""
                INSERT INTO amizade (jogador_id, amigo_id, ativo)
                VALUES (:jogador_id, :amigo_id, 1)
            """),
            {"jogador_id": j2, "amigo_id": j1}
        )
        db_session.commit()

        amizade_id = db_session.execute(
            text("""
                SELECT id FROM amizade 
                WHERE jogador_id = :j1_id AND amigo_id = :j2_id
            """),
            {"j1_id": j1, "j2_id": j2}
        ).scalar()

        # Remover
        response = client.delete(f"/amigos/{amizade_id}")

        assert response.status_code == 200
        assert "removido" in response.json()["mensagem"].lower()

        # Validar soft delete bilateral
        amizade_f = db_session.execute(
            text("""
                SELECT ativo FROM amizade 
                WHERE jogador_id = :j1_id AND amigo_id = :j2_id
            """),
            {"j1_id": j1, "j2_id": j2}
        ).scalar()
        
        amizade_b = db_session.execute(
            text("""
                SELECT ativo FROM amizade 
                WHERE jogador_id = :j2_id AND amigo_id = :j1_id
            """),
            {"j2_id": j2, "j1_id": j1}
        ).scalar()

        assert amizade_f == 0
        assert amizade_b == 0


class TestBuscarJogador:
    """Bonus: Buscar jogador para adicionar como amigo"""

    def test_buscar_jogador_por_nome_http_200(self, client: TestClient, db_session: Session):
        """Buscar jogador por nome de exibição"""
        # Setup
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, nome_exibicao)
                VALUES (:nome, :email, :senha, :exibicao)
            """),
            {"nome": "João Silva", "email": "joao@test.com", "senha": "hash", "exibicao": "Mestre João"}
        )
        db_session.commit()

        payload = {"termo_busca": "Mestre"}
        response = client.post("/amigos/buscar", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any("Mestre" in jogador["nome_exibicao"] for jogador in data)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
