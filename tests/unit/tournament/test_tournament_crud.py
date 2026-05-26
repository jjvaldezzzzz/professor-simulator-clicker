"""
Testes Unitários para Torneio Pokémon (UC19-UC23)
Focados em Schemas reais e lógicas de constantes.
"""

import pytest
from app.schemas import TorneioCreate, TorneioRename

class TestTorneioSchema:
    """Testes de inicialização de schemas para Torneio"""

    def test_torneio_create_tamanho_valido_2(self):
        """UT-UC19-001: Schema pode ser criado"""
        payload = {
            "time_id": 1,
            "tamanho": 2
        }
        torneio = TorneioCreate(**payload)
        assert torneio.tamanho == 2
        assert torneio.time_id == 1
        
    def test_torneio_rename(self):
        """Garante que a renomeação passa o nome corretamente"""
        payload = {
            "nome": "Torneio Mestre"
        }
        rename = TorneioRename(**payload)
        assert rename.nome == "Torneio Mestre"


class TestTorneioConstants:
    """Testes das regras de negócio atreladas as constantes em tournament.py"""

    def test_custo_por_tamanho(self):
        """UT-UC19-007: Validar tabela de custos por tamanho"""
        from app.routers.tournament import CUSTO_POR_TAMANHO
        assert CUSTO_POR_TAMANHO[2] == 500.0
        assert CUSTO_POR_TAMANHO[4] == 700.0
        assert CUSTO_POR_TAMANHO[8] == 1000.0

    def test_premio_por_tamanho(self):
        """UT-UC22-001: Validar tabela de prêmios por tamanho"""
        from app.routers.tournament import PREMIO_POR_TAMANHO
        assert PREMIO_POR_TAMANHO[2] == 700.0
        assert PREMIO_POR_TAMANHO[4] == 1000.0
        assert PREMIO_POR_TAMANHO[8] == 2000.0

    def test_rodadas_por_tamanho(self):
        """UT-UC19-008: Validar rodadas necessárias baseadas nos participantes"""
        from app.routers.tournament import RODADAS_POR_TAMANHO
        assert RODADAS_POR_TAMANHO[2] == 1
        assert RODADAS_POR_TAMANHO[4] == 2
        assert RODADAS_POR_TAMANHO[8] == 3

    def test_custo_maior_que_premio(self):
        """UT-UC22-002: O prêmio deve ser sempre maior que a inscrição"""
        from app.routers.tournament import CUSTO_POR_TAMANHO, PREMIO_POR_TAMANHO
        for tamanho in [2, 4, 8]:
            assert PREMIO_POR_TAMANHO[tamanho] > CUSTO_POR_TAMANHO[tamanho]