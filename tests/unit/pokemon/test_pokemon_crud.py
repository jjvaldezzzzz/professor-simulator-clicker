"""
Testes Unitários para Times Pokémon (UC12-UC18)

UT-UC12: Sortear Pokémon (Gacha)
UT-UC13: Visualizar Pokémons do Jogador  
UT-UC14: Criar Time Pokémon
UT-UC15: Renomear Time
UT-UC16: Deletar Time
UT-UC17: Adicionar Pokémon ao Time
UT-UC18: Libertar Pokémon
"""

import pytest
from pydantic import ValidationError
from app.schemas import (
    PokemonTimeCreate, 
    PokemonGachaResponse,
    TimeCreate,
    TimeUpdate,
)


class TestPokemonSchema:
    """Testes de validação de schemas para Pokémon"""

    def test_pokemon_time_create_valido(self):
        """UT-UC12-001: Schema com dados válidos"""
        payload = {
            "jogador_id": 1,
            "pokemon_api_id": 1,
            "nome_pokemon": "Bulbasaur",
            "sprite_url": "https://example.com/bulbasaur.png"
        }
        pokemon = PokemonTimeCreate(**payload)
        assert pokemon.jogador_id == 1
        assert pokemon.nome_pokemon == "Bulbasaur"

    def test_pokemon_time_nome_vazio(self):
        """UT-UC12-002: Rejeitar nome vazio"""
        with pytest.raises(ValidationError):
            PokemonTimeCreate(
                jogador_id=1,
                pokemon_api_id=1,
                nome_pokemon="",
                sprite_url="https://example.com/bulbasaur.png"
            )

    def test_pokemon_time_api_id_negativo(self):
        """UT-UC12-003: Rejeitar api_id negativo"""
        with pytest.raises(ValidationError):
            PokemonTimeCreate(
                jogador_id=1,
                pokemon_api_id=-1,
                nome_pokemon="Bulbasaur",
                sprite_url="https://example.com/bulbasaur.png"
            )


class TestTimeSchema:
    """Testes de validação de schemas para Times"""

    def test_time_create_valido(self):
        """UT-UC14-001: Schema de criação com dados válidos"""
        payload = {
            "nome": "Time Inicial"
        }
        time = TimeCreate(**payload)
        assert time.nome == "Time Inicial"

    def test_time_create_nome_vazio(self):
        """UT-UC14-002: Rejeitar nome vazio"""
        with pytest.raises(ValidationError):
            TimeCreate(nome="")

    def test_time_create_nome_whitespace(self):
        """UT-UC14-003: Rejeitar nome só com espaços"""
        with pytest.raises(ValidationError):
            TimeCreate(nome="   ")

    def test_time_create_nome_muito_longo(self):
        """UT-UC14-004: Rejeitar nome com mais de 50 caracteres"""
        nome_longo = "A" * 51
        with pytest.raises(ValidationError):
            TimeCreate(nome=nome_longo)

    def test_time_update_valido(self):
        """UT-UC15-001: Schema de atualização com dados válidos"""
        payload = {
            "nome": "Novo Nome do Time"
        }
        time_update = TimeUpdate(**payload)
        assert time_update.nome == "Novo Nome do Time"

    def test_time_update_nome_vazio(self):
        """UT-UC15-002: Rejeitar atualização com nome vazio"""
        with pytest.raises(ValidationError):
            TimeUpdate(nome="")

    def test_time_update_nome_muito_longo(self):
        """UT-UC15-003: Rejeitar atualização com nome > 50 caracteres"""
        nome_longo = "B" * 51
        with pytest.raises(ValidationError):
            TimeUpdate(nome=nome_longo)


class TestPokemonValidations:
    """Testes de lógica de validação para Pokémon"""

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
        nome_com_espaços = "  Time Teste  "
        resultado = _validar_nome_time(nome_com_espaços)
        assert resultado == "Time Teste"

    def test_validar_nome_time_vazio_raise_exception(self):
        """UT-UC14-006: Nome vazio deve levantar exceção"""
        from app.routers.pokemon import _validar_nome_time
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            _validar_nome_time("")
        
        assert exc_info.value.status_code == 400
        assert "obrigatorio" in exc_info.value.detail.lower()

    def test_validar_nome_time_muito_longo_raise_exception(self):
        """UT-UC14-007: Nome > 50 caracteres deve levantar exceção"""
        from app.routers.pokemon import _validar_nome_time
        from fastapi import HTTPException
        
        nome_longo = "A" * 51
        with pytest.raises(HTTPException) as exc_info:
            _validar_nome_time(nome_longo)
        
        assert exc_info.value.status_code == 400
        assert "50 caracteres" in exc_info.value.detail
