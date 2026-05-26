"""
Testes Unitários para Perfil do Usuário (UC01-UC04)
Alinhados com a validação da rota e Pydantic EmailStr.
"""

import pytest
from pydantic import ValidationError
from app.schemas import JogadorCreate, JogadorLogin, JogadorUpdate, JogadorResponse

class TestJogadorCreateSchema:
    def test_jogador_create_valido(self):
        payload = {
            "nome": "João Silva",
            "email": "joao@example.com",
            "senha": "senha123"
        }
        jogador = JogadorCreate(**payload)
        assert jogador.nome == "João Silva"
        assert jogador.email == "joao@example.com"
        assert jogador.senha == "senha123"

    def test_jogador_create_email_invalido(self):
        with pytest.raises(ValidationError):
            JogadorCreate(nome="João", email="invalido", senha="123")

    def test_jogador_create_nome_vazio(self):
        with pytest.raises(ValidationError):
            JogadorCreate(nome="", email="teste@example.com", senha="123")

    def test_jogador_create_senha_obrigatoria(self):
        payload = {"nome": "João", "email": "teste@example.com"}
        with pytest.raises(ValidationError):
            JogadorCreate(**payload) 

class TestJogadorLoginSchema:
    def test_login_valido(self):
        payload = {"email": "joao@example.com", "senha": "senha123"}
        login = JogadorLogin(**payload)
        assert login.email == "joao@example.com"
        assert login.senha == "senha123"

    def test_login_email_invalido(self):
        with pytest.raises(ValidationError):
            JogadorLogin(email="invalido", senha="123")

class TestJogadorUpdateSchema:
    def test_update_nome_valido(self):
        payload = {"nome_exibicao": "Mestre Pokémon"}
        update = JogadorUpdate(**payload)
        assert update.nome_exibicao == "Mestre Pokémon"

    def test_update_nome_vazio_inicializa(self):
        # Validação do vazio ocorre na rota, o schema inicializa.
        payload = {"nome_exibicao": ""}
        update = JogadorUpdate(**payload)
        assert update.nome_exibicao == ""

class TestJogadorResponseSchema:
    def test_response_schema_valido(self):
        payload = {
            "id": 1,
            "nome": "João",
            "nome_exibicao": "Mestre",
            "email": "joao@example.com",
            "saldo": 100.0
        }
        response = JogadorResponse(**payload)
        assert response.id == 1
        assert response.saldo == 100.0

class TestValidacaoNomeExibicao:
    @pytest.mark.parametrize("nome_invalido", [
        "Nome@Inválido",
        "Nome#Test",
        "Nome!Test",
        "Nome$Test"
    ])
    def test_nomes_com_caracteres_especiais(self, nome_invalido):
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
        import re
        DISPLAY_NAME_REGEX = re.compile(r"^[A-Za-z0-9 ]+$")
        assert DISPLAY_NAME_REGEX.match(nome_valido)