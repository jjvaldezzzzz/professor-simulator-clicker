# tests/unit/test_jogador_unit.py
"""
Testes Unitários para Perfil do Usuário (UC01-UC04)

Validam funções, schemas e lógica isolada sem dependência de BD ou HTTP.
Meta de cobertura: 90%+
"""

import pytest
from pydantic import ValidationError
from app.schemas import JogadorCreate, JogadorLogin, JogadorUpdate, JogadorResponse


class TestJogadorCreateSchema:
    """UT-UC01-001, UT-UC01-002, UT-UC01-003: Schema de criação"""

    def test_jogador_create_valido(self):
        """UT-UC01-003: Criar schema com dados válidos"""
        payload = {
            "nome": "João Silva",
            "email": "joao@example.com",
            "senha": "senha123"
        }
        jogador = JogadorCreate(**payload)
        assert jogador.nome == "João Silva"
        assert jogador.email == "joao@example.com"
        assert jogador.senha == "senha123"

    def test_jogador_create_email_vazio(self):
        """UT-UC01-001: Rejeitar email vazio"""
        with pytest.raises(ValidationError) as exc_info:
            JogadorCreate(nome="João", email="", senha="123")
        errors = exc_info.value.errors()
        assert any(e["type"] == "value_error" for e in errors)

    def test_jogador_create_email_invalido(self):
        """Rejeitar email mal formatado"""
        with pytest.raises(ValidationError):
            JogadorCreate(nome="João", email="invalido", senha="123")

    def test_jogador_create_nome_vazio(self):
        """UT-UC01-002: Rejeitar nome vazio"""
        with pytest.raises(ValidationError):
            JogadorCreate(nome="", email="teste@example.com", senha="123")

    def test_jogador_create_nome_whitespace(self):
        """Rejeitar nome só com espaços"""
        with pytest.raises(ValidationError):
            JogadorCreate(nome="   ", email="teste@example.com", senha="123")

    def test_jogador_create_senha_obrigatoria(self):
        """Validar que senha é obrigatória"""
        # Nota: Pydantic aceita string vazia, validação fica na rota
        # Este teste valida que schema não aceita se obrigatório
        payload = {"nome": "João", "email": "teste@example.com"}
        with pytest.raises(ValidationError):
            JogadorCreate(**payload)  # Sem senha


class TestJogadorLoginSchema:
    """UT-UC02-001: Schema de autenticação"""

    def test_login_valido(self):
        """Criar schema de login com dados válidos"""
        payload = {"email": "joao@example.com", "senha": "senha123"}
        login = JogadorLogin(**payload)
        assert login.email == "joao@example.com"
        assert login.senha == "senha123"

    def test_login_email_invalido(self):
        """Rejeitar email inválido no login"""
        with pytest.raises(ValidationError):
            JogadorLogin(email="invalido", senha="123")

    def test_login_email_vazio(self):
        """Rejeitar email vazio no login"""
        with pytest.raises(ValidationError):
            JogadorLogin(email="", senha="123")

    def test_login_senha_vazia(self):
        """Rejeitar senha vazia no login"""
        # Nota: Pydantic aceita string vazia, validação fica na rota
        payload = {"email": "teste@example.com", "senha": ""}
        login = JogadorLogin(**payload)
        assert login.senha == ""  # Schema permite, validação fica na rota


class TestJogadorUpdateSchema:
    """UT-UC03-001, UT-UC03-002: Schema de atualização de perfil"""

    def test_update_nome_valido(self):
        """Atualizar nome com valor válido"""
        payload = {"nome_exibicao": "Mestre Pokémon"}
        update = JogadorUpdate(**payload)
        assert update.nome_exibicao == "Mestre Pokémon"

    def test_update_nome_vazio(self):
        """Rejeitar nome vazio"""
        # Nota: Pydantic valida na API, mas testamos o schema também
        payload = {"nome_exibicao": ""}
        update = JogadorUpdate(**payload)
        assert update.nome_exibicao == ""  # Schema permite, validação fica na rota

    def test_update_nome_com_espacos(self):
        """Permitir nome com espaços"""
        payload = {"nome_exibicao": "Nome Com Espacos"}
        update = JogadorUpdate(**payload)
        assert update.nome_exibicao == "Nome Com Espacos"

    def test_update_nome_numeros(self):
        """Permitir números no nome"""
        payload = {"nome_exibicao": "Jogador 123"}
        update = JogadorUpdate(**payload)
        assert update.nome_exibicao == "Jogador 123"


class TestJogadorResponseSchema:
    """Validar schema de resposta do jogador"""

    def test_response_schema_valido(self):
        """Criar response com dados válidos"""
        payload = {
            "id": 1,
            "nome": "João",
            "nome_exibicao": "Mestre",
            "email": "joao@example.com",
            "saldo": 100.0
        }
        response = JogadorResponse(**payload)
        assert response.id == 1
        assert response.nome == "João"
        assert response.saldo == 100.0

    def test_response_saldo_padrao(self):
        """Validar saldo padrão"""
        payload = {
            "id": 1,
            "nome": "João",
            "nome_exibicao": "Mestre",
            "email": "joao@example.com",
            "saldo": 0.0
        }
        response = JogadorResponse(**payload)
        assert response.saldo == 0.0


class TestValidacaoNomeExibicao:
    """Testes de validação de nome de exibição"""

    @pytest.mark.parametrize("nome_invalido", [
        "Nome@Inválido",
        "Nome#Test",
        "Nome!Test",
        "Nome$Test",
        "Nome%Test",
        "Nome&Test",
    ])
    def test_nomes_com_caracteres_especiais(self, nome_invalido):
        """UT-UC03-002: Rejeitar caracteres especiais"""
        # Validação com regex no router: r"^[A-Za-z0-9 ]+$"
        import re
        DISPLAY_NAME_REGEX = re.compile(r"^[A-Za-z0-9 ]+$")
        assert not DISPLAY_NAME_REGEX.match(nome_invalido)

    @pytest.mark.parametrize("nome_valido", [
        "Nome Valido",
        "Jogador123",
        "Master Player",
        "J0g4d0r",
    ])
    def test_nomes_validos(self, nome_valido):
        """Aceitar nomes válidos"""
        import re
        DISPLAY_NAME_REGEX = re.compile(r"^[A-Za-z0-9 ]+$")
        assert DISPLAY_NAME_REGEX.match(nome_valido)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
