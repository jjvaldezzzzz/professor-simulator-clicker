# tests/integration/test_users_integration.py
"""
Testes de Integração para Perfil do Usuário (UC01-UC04)

Validam HTTP, BD, e fluxos completos.
Meta de cobertura: 75%+
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

# Fixtures são importadas de conftest.py


class TestCadastroJogador:
    """IT-UC01-001, IT-UC01-002, IT-UC01-003: Endpoints de cadastro"""

    def test_cadastro_sucesso_http_201(self, client: TestClient, db_session: Session):
        """IT-UC01-001: Cadastro com sucesso retorna HTTP 201"""
        payload = {
            "nome": "Ana Silva",
            "email": "ana@test.com",
            "senha": "senha123"
        }
        response = client.post("/jogadores/", json=payload)

        # Validações
        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == "Ana Silva"
        assert data["email"] == "ana@test.com"
        assert data["nome_exibicao"] == "Treinador Iniciante"
        assert data["saldo"] == 0

        # Validar persistência no BD
        jogador = db_session.execute(
            text("SELECT * FROM jogador WHERE email = :email"),
            {"email": "ana@test.com"}
        ).fetchone()
        assert jogador is not None
        assert jogador.nome == "Ana Silva"
        assert jogador.ativo == 1

    def test_cadastro_email_duplicado_http_400(self, client: TestClient, db_session: Session):
        """IT-UC01-002: Rejeitar email duplicado com HTTP 400"""
        # Criar primeiro jogador
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, ativo)
                VALUES (:nome, :email, :senha, 1)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash123"}
        )
        db_session.commit()

        # Tentar criar com mesmo email
        payload = {
            "nome": "Outro João",
            "email": "joao@test.com",
            "senha": "outra_senha"
        }
        response = client.post("/jogadores/", json=payload)

        assert response.status_code == 400
        assert "Email já cadastrado" in response.json()["detail"]

    def test_cadastro_email_invalido_http_422(self, client: TestClient):
        """IT-UC01-003: Rejeitar email mal formatado com HTTP 422"""
        payload = {
            "nome": "João",
            "email": "invalido",  # Sem @
            "senha": "123"
        }
        response = client.post("/jogadores/", json=payload)
        assert response.status_code == 422

    def test_cadastro_nome_vazio_http_422(self, client: TestClient):
        """Rejeitar nome vazio"""
        payload = {
            "nome": "",
            "email": "teste@example.com",
            "senha": "123"
        }
        response = client.post("/jogadores/", json=payload)
        assert response.status_code == 422

    def test_cadastro_nome_whitespace_http_422(self, client: TestClient):
        """Rejeitar nome só com espaços"""
        payload = {
            "nome": "   ",
            "email": "teste@example.com",
            "senha": "123"
        }
        response = client.post("/jogadores/", json=payload)
        assert response.status_code == 422

    def test_consultar_jogador_criado_http_200(self, client: TestClient, db_session: Session):
        """Validar que jogador criado pode ser consultado"""
        # Criar jogador
        payload = {
            "nome": "Maria",
            "email": "maria@test.com",
            "senha": "senha123"
        }
        create_response = client.post("/jogadores/", json=payload)
        jogador_id = create_response.json()["id"]

        # Consultar jogador
        get_response = client.get(f"/jogadores/{jogador_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["nome"] == "Maria"
        assert data["email"] == "maria@test.com"


class TestAutenticacao:
    """IT-UC02-001, IT-UC02-002, IT-UC02-003: Endpoints de autenticação"""

    def test_login_valido_http_200(self, client: TestClient, db_session: Session):
        """IT-UC02-001: Login com credenciais válidas retorna HTTP 200 com token"""
        # Criar jogador
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, ativo, is_admin)
                VALUES (:nome, :email, :senha, 1, 0)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "senha123"}
        )
        db_session.commit()

        # Fazer login
        payload = {"email": "joao@test.com", "senha": "senha123"}
        response = client.post("/jogadores/login", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "jogador_id" in data
        assert "is_admin" in data
        assert data["is_admin"] == False

    def test_login_senha_incorreta_http_401(self, client: TestClient, db_session: Session):
        """IT-UC02-002: Rejeitar senha incorreta com HTTP 401"""
        # Criar jogador
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, ativo)
                VALUES (:nome, :email, :senha, 1)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "correta"}
        )
        db_session.commit()

        # Tentar login com senha errada
        payload = {"email": "joao@test.com", "senha": "incorreta"}
        response = client.post("/jogadores/login", json=payload)

        assert response.status_code == 401
        assert "Credenciais inválidas" in response.json()["detail"]

    def test_login_email_inexistente_http_401(self, client: TestClient):
        """IT-UC02-003: Rejeitar email inexistente com HTTP 401"""
        payload = {"email": "inexistente@test.com", "senha": "qualquer"}
        response = client.post("/jogadores/login", json=payload)

        assert response.status_code == 401
        assert "Credenciais inválidas" in response.json()["detail"]

    def test_login_admin_retorna_is_admin_true(self, client: TestClient, db_session: Session):
        """Validar que admin retorna is_admin=True"""
        # Criar admin
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, ativo, is_admin)
                VALUES (:nome, :email, :senha, 1, 1)
            """),
            {"nome": "Admin", "email": "admin@test.com", "senha": "admin123"}
        )
        db_session.commit()

        # Fazer login
        payload = {"email": "admin@test.com", "senha": "admin123"}
        response = client.post("/jogadores/login", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["is_admin"] == True


class TestAtualizacaoPerfil:
    """IT-UC03-001, IT-UC03-002, IT-UC03-003: Endpoints de atualização"""

    def test_atualizar_nome_sucesso_http_200(self, client: TestClient, db_session: Session):
        """IT-UC03-001: Atualizar nome com sucesso retorna HTTP 200"""
        # Criar jogador
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, nome_exibicao)
                VALUES (:nome, :email, :senha, :exibicao)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash", "exibicao": "Jogador"}
        )
        db_session.commit()
        jogador_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = :email"),
            {"email": "joao@test.com"}
        ).scalar()

        # Atualizar nome
        payload = {"nome_exibicao": "Mestre Pokémon"}
        response = client.put(f"/jogadores/{jogador_id}/perfil", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["novo_nome_exibicao"] == "Mestre Pokémon"

        # Validar persistência
        jogador = db_session.execute(
            text("SELECT nome_exibicao FROM jogador WHERE id = :id"),
            {"id": jogador_id}
        ).fetchone()
        assert jogador.nome_exibicao == "Mestre Pokémon"

    def test_atualizar_nome_invalido_http_400(self, client: TestClient, db_session: Session):
        """IT-UC03-002: Rejeitar nome com caracteres inválidos com HTTP 400"""
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
            text("SELECT id FROM jogador WHERE email = :email"),
            {"email": "joao@test.com"}
        ).scalar()

        # Tentar atualizar com caracteres inválidos
        payload = {"nome_exibicao": "Nome@Inválido"}
        response = client.put(f"/jogadores/{jogador_id}/perfil", json=payload)

        assert response.status_code == 400
        assert "caracteres invalidos" in response.json()["detail"]

    def test_atualizar_nome_vazio_http_400(self, client: TestClient, db_session: Session):
        """IT-UC03-003: Rejeitar nome vazio com HTTP 400"""
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
            text("SELECT id FROM jogador WHERE email = :email"),
            {"email": "joao@test.com"}
        ).scalar()

        # Tentar atualizar com nome vazio
        payload = {"nome_exibicao": ""}
        response = client.put(f"/jogadores/{jogador_id}/perfil", json=payload)

        assert response.status_code == 400
        assert "Nome de exibicao e obrigatorio" in response.json()["detail"]

    def test_atualizar_nome_muito_longo_http_400(self, client: TestClient, db_session: Session):
        """Rejeitar nome com mais de 50 caracteres"""
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
            text("SELECT id FROM jogador WHERE email = :email"),
            {"email": "joao@test.com"}
        ).scalar()

        # Nome com mais de 50 caracteres
        payload = {"nome_exibicao": "A" * 51}
        response = client.put(f"/jogadores/{jogador_id}/perfil", json=payload)

        assert response.status_code == 400
        assert "50 caracteres" in response.json()["detail"]

    def test_atualizar_perfil_jogador_inexistente_http_404(self, client: TestClient):
        """Rejeitar atualização de jogador inexistente"""
        payload = {"nome_exibicao": "Novo Nome"}
        response = client.put("/jogadores/99999/perfil", json=payload)

        assert response.status_code == 404
        assert "Jogador não encontrado" in response.json()["detail"]


class TestDeletarConta:
    """IT-UC04-001, IT-UC04-002: Endpoints de deleção"""

    def test_deletar_conta_nao_admin_http_200(self, client: TestClient, db_session: Session):
        """IT-UC04-001: Deletar conta não-admin com sucesso retorna HTTP 200"""
        # Criar jogador não-admin
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, is_admin)
                VALUES (:nome, :email, :senha, 0)
            """),
            {"nome": "João", "email": "joao@test.com", "senha": "hash"}
        )
        db_session.commit()
        jogador_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = :email"),
            {"email": "joao@test.com"}
        ).scalar()

        # Deletar
        response = client.delete(f"/jogadores/{jogador_id}")

        assert response.status_code == 200
        assert "deletada com sucesso" in response.json()["mensagem"]

        # Validar que foi deletado do BD
        jogador = db_session.execute(
            text("SELECT id FROM jogador WHERE id = :id"),
            {"id": jogador_id}
        ).fetchone()
        assert jogador is None

    def test_deletar_conta_admin_http_403(self, client: TestClient, db_session: Session):
        """IT-UC04-002: Rejeitar deleção de admin com HTTP 403"""
        # Criar admin
        db_session.execute(
            text("""
                INSERT INTO jogador (nome, email, senha_hash, is_admin)
                VALUES (:nome, :email, :senha, 1)
            """),
            {"nome": "Admin", "email": "admin@test.com", "senha": "hash"}
        )
        db_session.commit()
        admin_id = db_session.execute(
            text("SELECT id FROM jogador WHERE email = :email"),
            {"email": "admin@test.com"}
        ).scalar()

        # Tentar deletar admin
        response = client.delete(f"/jogadores/{admin_id}")

        assert response.status_code == 403
        assert "admin nao pode ser deletada" in response.json()["detail"]

        # Validar que admin ainda existe
        admin = db_session.execute(
            text("SELECT id FROM jogador WHERE id = :id"),
            {"id": admin_id}
        ).fetchone()
        assert admin is not None

    def test_deletar_jogador_inexistente_http_404(self, client: TestClient):
        """Rejeitar deleção de jogador inexistente"""
        response = client.delete("/jogadores/99999")

        assert response.status_code == 404
        assert "Jogador nao encontrado" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
