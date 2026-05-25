# tests/integration/test_tournament_integration.py
"""
Testes de Integração para Torneios (UC19-UC23)

Validam criação, listagem, obtenção e resolução de torneios.
Meta de cobertura: 75%+
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


class TestCriarTorneio:
    """IT-UC19-001, IT-UC19-002, IT-UC19-003: Criar novo torneio"""

    def test_criar_torneio_tamanho_2_sucesso_http_201(self, client: TestClient, db_session: Session):
        """IT-UC19-001: Criar torneio tamanho 2 (custo 500, prêmio 700)"""
        # Criar jogador com saldo
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, saldo)
                VALUES (:nome, :email, :senha, :saldo)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash", "saldo": 1000.0}
        )
        db_session.commit()
        jogador_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'joao@test.com'")
        ).scalar()

        # Criar time com pokémon
        db_session.execute(
            text("""
                INSERT INTO pokemon (jogador_id, nome, tipo, bst)
                VALUES (:jogador_id, :nome, :tipo, :bst)
            """),
            {"jogador_id": jogador_id, "nome": "Pikachu", "tipo": "elétrico", "bst": 320}
        )
        db_session.commit()

        db_session.execute(
            text("""
                INSERT INTO time_pokemon (jogador_id, nome)
                VALUES (:jogador_id, :nome)
            """),
            {"jogador_id": jogador_id, "nome": "Time Competição"}
        )
        db_session.commit()

        payload = {"tamanho": 2, "time_id": 1}
        response = client.post(f"/torneio/{jogador_id}", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["tamanho"] == 2
        assert "torneio_id" in data

    def test_criar_torneio_saldo_insuficiente_http_400(self, client: TestClient, db_session: Session):
        """IT-UC19-002: Rejeitar torneio com saldo insuficiente"""
        # Criar jogador com saldo baixo
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

        payload = {"tamanho": 2, "time_id": 1}
        response = client.post(f"/torneio/{jogador_id}", json=payload)

        assert response.status_code == 400
        assert "saldo insuficiente" in response.json()["detail"].lower()

    def test_criar_torneio_tamanho_invalido_http_400(self, client: TestClient, db_session: Session):
        """IT-UC19-003: Rejeitar tamanho de torneio inválido"""
        # Criar jogador
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, saldo)
                VALUES (:nome, :email, :senha, :saldo)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash", "saldo": 1000.0}
        )
        db_session.commit()
        jogador_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'joao@test.com'")
        ).scalar()

        payload = {"tamanho": 5, "time_id": 1}  # Válidos: 2, 4, 8
        response = client.post(f"/torneio/{jogador_id}", json=payload)

        assert response.status_code == 400
        assert "invalido" in response.json()["detail"].lower()


class TestListarTorneios:
    """IT-UC20-001, IT-UC20-002: Listar torneios do jogador"""

    def test_listar_torneios_vazio_http_200(self, client: TestClient, db_session: Session):
        """IT-UC20-001: Listar torneios vazios retorna lista vazia"""
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

        response = client.get(f"/torneio/{jogador_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_listar_torneios_com_dados_http_200(self, client: TestClient, db_session: Session):
        """IT-UC20-002: Listar torneios com dados"""
        # Setup
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, saldo)
                VALUES (:nome, :email, :senha, :saldo)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash", "saldo": 1000.0}
        )
        db_session.commit()
        jogador_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'joao@test.com'")
        ).scalar()

        # Criar torneio
        db_session.execute(
            text("""
                INSERT INTO torneio (jogador_id, tamanho, status, custo, premio)
                VALUES (:jogador_id, :tamanho, :status, :custo, :premio)
            """),
            {"jogador_id": jogador_id, "tamanho": 2, "status": "aberto", "custo": 500, "premio": 700}
        )
        db_session.commit()

        response = client.get(f"/torneio/{jogador_id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0


class TestObterTorneio:
    """IT-UC21-001, IT-UC21-002: Obter detalhes de um torneio"""

    def test_obter_torneio_sucesso_http_200(self, client: TestClient, db_session: Session):
        """IT-UC21-001: Obter torneio existente"""
        # Setup
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

        # Criar torneio
        db_session.execute(
            text("""
                INSERT INTO torneio (jogador_id, tamanho, status, custo, premio)
                VALUES (:jogador_id, :tamanho, :status, :custo, :premio)
            """),
            {"jogador_id": jogador_id, "tamanho": 2, "status": "aberto", "custo": 500, "premio": 700}
        )
        db_session.commit()
        torneio_id = db_session.execute(
            text("SELECT id FROM torneio WHERE jogador_id = :id"),
            {"id": jogador_id}
        ).scalar()

        response = client.get(f"/torneio/{jogador_id}/{torneio_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == torneio_id
        assert data["tamanho"] == 2

    def test_obter_torneio_inexistente_http_404(self, client: TestClient):
        """IT-UC21-002: Obter torneio inexistente retorna 404"""
        response = client.get("/torneio/1/99999")
        assert response.status_code == 404


class TestResolverPartida:
    """IT-UC22-001, IT-UC22-002: Resolver partida de torneio"""

    def test_resolver_partida_time_vencedor_http_200(self, client: TestClient, db_session: Session):
        """IT-UC22-001: Resolver partida com vencedor"""
        # Setup: Criar 2 jogadores, torneio, e partida
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, saldo)
                VALUES (:nome, :email, :senha, :saldo)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash", "saldo": 1000.0}
        )
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, saldo)
                VALUES (:nome, :email, :senha, :saldo)
            """),
            {"nome": "Maria", "email": "maria@test.com", "senha": "hash", "saldo": 1000.0}
        )
        db_session.commit()

        jogador1_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'joao@test.com'")
        ).scalar()
        jogador2_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'maria@test.com'")
        ).scalar()

        # Criar torneio
        db_session.execute(
            text("""
                INSERT INTO torneio (jogador_id, tamanho, status, custo, premio)
                VALUES (:jogador_id, :tamanho, :status, :custo, :premio)
            """),
            {"jogador_id": jogador1_id, "tamanho": 2, "status": "aberto", "custo": 500, "premio": 700}
        )
        db_session.commit()

        torneio_id = db_session.execute(
            text("SELECT id FROM torneio WHERE jogador_id = :id"),
            {"id": jogador1_id}
        ).scalar()

        # Criar partida
        db_session.execute(
            text("""
                INSERT INTO torneio_partida (torneio_id, jogador_1_id, jogador_2_id, vencedor_id, rodada)
                VALUES (:torneio_id, :j1_id, :j2_id, :vencedor_id, :rodada)
            """),
            {
                "torneio_id": torneio_id,
                "j1_id": jogador1_id,
                "j2_id": jogador2_id,
                "vencedor_id": None,
                "rodada": 1
            }
        )
        db_session.commit()

        partida_id = db_session.execute(
            text("SELECT id FROM torneio_partida WHERE torneio_id = :id"),
            {"id": torneio_id}
        ).scalar()

        # Resolver
        payload = {"vencedor_id": jogador1_id}
        response = client.put(f"/torneio/{torneio_id}/partida/{partida_id}", json=payload)

        assert response.status_code == 200
        assert "resolvida" in response.json()["mensagem"].lower()

    def test_resolver_partida_inexistente_http_404(self, client: TestClient):
        """IT-UC22-002: Resolver partida inexistente retorna 404"""
        payload = {"vencedor_id": 1}
        response = client.put("/torneio/1/partida/99999", json=payload)
        assert response.status_code == 404


class TestDeletarTorneio:
    """IT-UC23-001, IT-UC23-002: Deletar torneio"""

    def test_deletar_torneio_sucesso_http_200(self, client: TestClient, db_session: Session):
        """IT-UC23-001: Deletar torneio com sucesso"""
        # Setup
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

        # Criar torneio
        db_session.execute(
            text("""
                INSERT INTO torneio (jogador_id, tamanho, status, custo, premio)
                VALUES (:jogador_id, :tamanho, :status, :custo, :premio)
            """),
            {"jogador_id": jogador_id, "tamanho": 2, "status": "aberto", "custo": 500, "premio": 700}
        )
        db_session.commit()

        torneio_id = db_session.execute(
            text("SELECT id FROM torneio WHERE jogador_id = :id"),
            {"id": jogador_id}
        ).scalar()

        response = client.delete(f"/torneio/{torneio_id}")

        assert response.status_code == 200
        assert "deletado" in response.json()["mensagem"].lower()

    def test_deletar_torneio_inexistente_http_404(self, client: TestClient):
        """IT-UC23-002: Deletar torneio inexistente retorna 404"""
        response = client.delete("/torneio/99999")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
