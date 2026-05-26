"""
Testes Unitários para Times Pokémon (UC12-UC18)
Ajustados para refletir a modelagem real dos schemas em app/schemas.py
"""

import pytest
from pydantic import ValidationError
from app.schemas import (
    TimePokemonCreate,
    TimePokemonRename,
    TimePokemonAdicionar
)

class TestTimeSchema:
    """Testes de validação de schemas para Times"""

    def test_time_create_valido(self):
        """UT-UC14-001: Schema de criação com dados válidos"""
        payload = {
            "nome": "Time Inicial"
        }
        time = TimePokemonCreate(**payload)
        assert time.nome == "Time Inicial"

    def test_time_create_nome_vazio(self):
        """Testar inicialização com nome vazio (validação de obrigatoriedade ocorre na rota)"""
        time = TimePokemonCreate(nome="")
        assert time.nome == ""

    def test_time_update_valido(self):
        """UT-UC15-001: Schema de atualização com dados válidos"""
        payload = {
            "nome": "Novo Nome do Time"
        }
        time_update = TimePokemonRename(**payload)
        assert time_update.nome == "Novo Nome do Time"

    def test_time_adicionar_valido(self):
        """Schema para adicionar Pokemon ao time"""
        payload = {
            "pokemon_id": 25
        }
        add_pokemon = TimePokemonAdicionar(**payload)
        assert add_pokemon.pokemon_id == 25

class TestPokemonValidations:
    """Testes de lógica de validação isoladas para Pokémon"""

    def test_custo_gacha_constante(self):
        """UT-UC12-005: Validar constante CUSTO_GACHA"""
        from app.routers.pokemon import CUSTO_GACHA
        assert CUSTO_GACHA == 100.0

    def test_limite_pokemon_time(self):
        """UT-UC17-001: Validar limite de 6 pokémons por time"""
        from app.routers.pokemon import LIMITE_POKEMON_TIME
        assert LIMITE_POKEMON_TIME == 6

    def test_validar_nome_time_com_espaços(self):
        """UT-UC14-005: Nome com espaços deve ser aceito após strip"""
        from app.routers.pokemon import _validar_nome_time
        nome_com_espacos = "  Time Teste  "
        resultado = _validar_nome_time(nome_com_espacos)
        assert resultado == "Time Teste"

    def test_validar_nome_time_vazio_raise_exception(self):
        """UT-UC14-006: Nome vazio na validação da rota deve levantar exceção"""
        from app.routers.pokemon import _validar_nome_time
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            _validar_nome_time("")
        
        assert exc_info.value.status_code == 400
        assert "obrigatorio" in exc_info.value.detail.lower()

    def test_validar_nome_time_muito_longo_raise_exception(self):
        """UT-UC14-007: Nome > 50 caracteres na validação da rota deve levantar exceção"""
        from app.routers.pokemon import _validar_nome_time
        from fastapi import HTTPException
        
        nome_longo = "A" * 51
        with pytest.raises(HTTPException) as exc_info:
            _validar_nome_time(nome_longo)
        
        assert exc_info.value.status_code == 400
        assert "50 caracteres" in exc_info.value.detail