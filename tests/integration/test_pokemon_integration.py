# tests/integration/test_pokemon_integration.py
"""
Testes de Integração para Pokémon/Teams (UC12-UC18)

Validam gacha, visualização de times e gerenciamento de pokémons.
Meta de cobertura: 75%+
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


class TestSorteioPokemon:
    """IT-UC12-001, IT-UC12-002, IT-UC12-003: Gacha/sorteiro de pokémon"""

    def test_jogador_sorteia_pokemon_saldo_suficiente_http_200(self, client: TestClient, db_session: Session):
        """IT-UC12-001: Sortear pokémon com saldo suficiente retorna HTTP 200"""
        # Criar jogador com saldo
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, saldo)
                VALUES (:nome, :email, :senha, :saldo)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash", "saldo": 500.0}
        )
        db_session.commit()
        jogador_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'joao@test.com'")
        ).scalar()

        # Sortear pokémon (custo padrão: 100)
        response = client.post(f"/pokemon/gacha/{jogador_id}")

        assert response.status_code == 200
        data = response.json()
        assert "pokemon" in data
        assert data["pokemon"]["nome"] is not None
        assert "saldo_restante" in data
        assert data["saldo_restante"] == 400.0  # 500 - 100

    def test_jogador_sorteia_pokemon_saldo_insuficiente_http_400(self, client: TestClient, db_session: Session):
        """IT-UC12-002: Rejeitar gacha com saldo insuficiente"""
        # Criar jogador com saldo baixo
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, saldo)
                VALUES (:nome, :email, :senha, :saldo)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash", "saldo": 50.0}
        )
        db_session.commit()
        jogador_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = 'joao@test.com'")
        ).scalar()

        # Tentar sortear
        response = client.post(f"/pokemon/gacha/{jogador_id}")

        assert response.status_code == 400
        assert "saldo insuficiente" in response.json()["detail"].lower()

    def test_sortear_pokemon_jogador_inexistente_http_404(self, client: TestClient):
        """IT-UC12-003: Tentar sortear para jogador inexistente retorna 404"""
        response = client.post("/pokemon/gacha/99999")
        assert response.status_code == 404


class TestVisualizarTime:
    """IT-UC13-001, IT-UC13-002: Visualizar time do jogador"""

    def test_visualizar_time_vazio_http_200(self, client: TestClient, db_session: Session):
        """IT-UC13-001: Visualizar time vazio retorna lista vazia"""
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

        # Visualizar time padrão
        response = client.get(f"/pokemon/times/{jogador_id}/1")

        assert response.status_code == 200
        data = response.json()
        assert "pokemons" in data
        assert len(data["pokemons"]) == 0

    def test_visualizar_time_com_pokemons_http_200(self, client: TestClient, db_session: Session):
        """IT-UC13-002: Visualizar time com pokémons"""
        # Criar jogador e time
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

        # Criar time
        db_session.execute(
            text("""
                INSERT INTO time_pokemon (jogador_id, nome)
                VALUES (:jogador_id, :nome)
            """),
            {"jogador_id": jogador_id, "nome": "Time 1"}
        )
        db_session.commit()

        response = client.get(f"/pokemon/times/{jogador_id}/1")
        assert response.status_code == 200


class TestListarTimes:
    """IT-UC14-001, IT-UC14-002: Listar todos os times do jogador"""

    def test_listar_times_vazio_http_200(self, client: TestClient, db_session: Session):
        """IT-UC14-001: Listar times vazio"""
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

        response = client.get(f"/pokemon/times/{jogador_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_listar_times_com_dados_http_200(self, client: TestClient, db_session: Session):
        """IT-UC14-002: Listar times com dados"""
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

        # Criar times
        db_session.execute(
            text("""
                INSERT INTO time_pokemon (jogador_id, nome)
                VALUES (:jogador_id, :nome)
            """),
            {"jogador_id": jogador_id, "nome": "Time 1"}
        )
        db_session.commit()

        response = client.get(f"/pokemon/times/{jogador_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0


class TestCriarTime:
    """IT-UC15-001, IT-UC15-002, IT-UC15-003: Criar novo time"""

    def test_criar_time_sucesso_http_201(self, client: TestClient, db_session: Session):
        """IT-UC15-001: Criar time com sucesso"""
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

        payload = {"nome": "Time Competitivo"}
        response = client.post(f"/pokemon/times/{jogador_id}", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == "Time Competitivo"

    def test_criar_time_nome_vazio_http_400(self, client: TestClient, db_session: Session):
        """IT-UC15-002: Rejeitar time com nome vazio"""
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

        payload = {"nome": ""}
        response = client.post(f"/pokemon/times/{jogador_id}", json=payload)

        assert response.status_code == 400

    def test_criar_time_jogador_inexistente_http_404(self, client: TestClient):
        """IT-UC15-003: Criar time para jogador inexistente retorna 404"""
        payload = {"nome": "Time"}
        response = client.post("/pokemon/times/99999", json=payload)
        assert response.status_code == 404


class TestRenomearTime:
    """IT-UC16-001, IT-UC16-002: Renomear time"""

    def test_renomear_time_sucesso_http_200(self, client: TestClient, db_session: Session):
        """IT-UC16-001: Renomear time com sucesso"""
        # Criar jogador e time
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

        db_session.execute(
            text("""
                INSERT INTO time_pokemon (jogador_id, nome)
                VALUES (:jogador_id, :nome)
            """),
            {"jogador_id": jogador_id, "nome": "Time Antigo"}
        )
        db_session.commit()
        time_id = db_session.execute(
            text("SELECT id FROM time_pokemon WHERE jogador_id = :id"),
            {"id": jogador_id}
        ).scalar()

        payload = {"novo_nome": "Time Novo"}
        response = client.put(f"/pokemon/times/{time_id}", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "Time Novo"

    def test_renomear_time_inexistente_http_404(self, client: TestClient):
        """IT-UC16-002: Renomear time inexistente retorna 404"""
        payload = {"novo_nome": "Novo Nome"}
        response = client.put("/pokemon/times/99999", json=payload)
        assert response.status_code == 404


class TestDeletarTime:
    """IT-UC17-001, IT-UC17-002: Deletar time"""

    def test_deletar_time_sucesso_http_200(self, client: TestClient, db_session: Session):
        """IT-UC17-001: Deletar time com sucesso"""
        # Criar jogador e time
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

        db_session.execute(
            text("""
                INSERT INTO time_pokemon (jogador_id, nome)
                VALUES (:jogador_id, :nome)
            """),
            {"jogador_id": jogador_id, "nome": "Time Deletavel"}
        )
        db_session.commit()
        time_id = db_session.execute(
            text("SELECT id FROM time_pokemon WHERE jogador_id = :id"),
            {"id": jogador_id}
        ).scalar()

        response = client.delete(f"/pokemon/times/{time_id}")

        assert response.status_code == 200
        assert "deletado" in response.json()["mensagem"].lower()

    def test_deletar_time_inexistente_http_404(self, client: TestClient):
        """IT-UC17-002: Deletar time inexistente retorna 404"""
        response = client.delete("/pokemon/times/99999")
        assert response.status_code == 404


class TestAdicionarPokemonTime:
    """IT-UC18-001, IT-UC18-002, IT-UC18-003: Adicionar pokémon ao time"""

    def test_adicionar_pokemon_time_sucesso_http_200(self, client: TestClient, db_session: Session):
        """IT-UC18-001: Adicionar pokémon ao time com sucesso"""
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

        db_session.execute(
            text("""
                INSERT INTO pokemon (jogador_id, nome, tipo, bst)
                VALUES (:jogador_id, :nome, :tipo, :bst)
            """),
            {"jogador_id": jogador_id, "nome": "Pikachu", "tipo": "elétrico", "bst": 320}
        )
        db_session.commit()
        pokemon_id = db_session.execute(
            text("SELECT id FROM pokemon WHERE nome = 'Pikachu'")
        ).scalar()

        db_session.execute(
            text("""
                INSERT INTO time_pokemon (jogador_id, nome)
                VALUES (:jogador_id, :nome)
            """),
            {"jogador_id": jogador_id, "nome": "Time 1"}
        )
        db_session.commit()
        time_id = db_session.execute(
            text("SELECT id FROM time_pokemon WHERE nome = 'Time 1'")
        ).scalar()

        payload = {"pokemon_id": pokemon_id}
        response = client.post(f"/pokemon/times/{time_id}/adicionar", json=payload)

        assert response.status_code == 200
        assert "adicionado" in response.json()["mensagem"].lower()

    def test_adicionar_pokemon_time_cheio_http_400(self, client: TestClient, db_session: Session):
        """IT-UC18-002: Rejeitar adição quando time está cheio (6 slots)"""
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

        # Criar 7 pokémons
        for i in range(7):
            db_session.execute(
                text("""
                    INSERT INTO pokemon (jogador_id, nome, tipo, bst)
                    VALUES (:jogador_id, :nome, :tipo, :bst)
                """),
                {"jogador_id": jogador_id, "nome": f"Pokemon{i}", "tipo": "normal", "bst": 300}
            )
        db_session.commit()

        # Criar time
        db_session.execute(
            text("""
                INSERT INTO time_pokemon (jogador_id, nome)
                VALUES (:jogador_id, :nome)
            """),
            {"jogador_id": jogador_id, "nome": "Time Cheio"}
        )
        db_session.commit()
        time_id = db_session.execute(
            text("SELECT id FROM time_pokemon WHERE nome = 'Time Cheio'")
        ).scalar()

        # Adicionar 6 pokémons
        pokemons = db_session.execute(
            text("SELECT id FROM pokemon WHERE jogador_id = :id ORDER BY id DESC LIMIT 6"),
            {"id": jogador_id}
        ).fetchall()

        for pokemon in pokemons:
            db_session.execute(
                text("""
                    INSERT INTO tempo_pokemon (time_id, pokemon_id)
                    VALUES (:time_id, :pokemon_id)
                """),
                {"time_id": time_id, "pokemon_id": pokemon[0]}
            )
        db_session.commit()

        # Tentar adicionar 7º
        ultimo_pokemon = db_session.execute(
            text("SELECT id FROM pokemon WHERE jogador_id = :id ORDER BY id ASC LIMIT 1"),
            {"id": jogador_id}
        ).scalar()

        payload = {"pokemon_id": ultimo_pokemon}
        response = client.post(f"/pokemon/times/{time_id}/adicionar", json=payload)

        assert response.status_code == 400
        assert "cheio" in response.json()["detail"].lower()

    def test_adicionar_pokemon_inexistente_http_404(self, client: TestClient, db_session: Session):
        """IT-UC18-003: Adicionar pokémon inexistente retorna 404"""
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

        db_session.execute(
            text("""
                INSERT INTO time_pokemon (jogador_id, nome)
                VALUES (:jogador_id, :nome)
            """),
            {"jogador_id": jogador_id, "nome": "Time 1"}
        )
        db_session.commit()
        time_id = db_session.execute(
            text("SELECT id FROM time_pokemon WHERE nome = 'Time 1'")
        ).scalar()

        payload = {"pokemon_id": 99999}
        response = client.post(f"/pokemon/times/{time_id}/adicionar", json=payload)

        assert response.status_code == 404


class TestLivertarPokemon:
    """IT-UC18-004: Liberar/deletar pokémon (bonus para UC18)"""

    def test_liberar_pokemon_sucesso_http_200(self, client: TestClient, db_session: Session):
        """Liberar pokémon do time com sucesso"""
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

        db_session.execute(
            text("""
                INSERT INTO pokemon (jogador_id, nome, tipo, bst)
                VALUES (:jogador_id, :nome, :tipo, :bst)
            """),
            {"jogador_id": jogador_id, "nome": "Pikachu", "tipo": "elétrico", "bst": 320}
        )
        db_session.commit()

        pokemon_id = db_session.execute(
            text("SELECT id FROM pokemon WHERE nome = 'Pikachu'")
        ).scalar()

        response = client.delete(f"/pokemon/{pokemon_id}")

        assert response.status_code == 200
        assert "liberado" in response.json()["mensagem"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
