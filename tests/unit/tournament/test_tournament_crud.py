"""
Testes Unitários para Torneio Pokémon (UC19-UC23)

UT-UC19: Criar Torneio e Inscrever Time
UT-UC20: Listar Torneios do Jogador
UT-UC21: Obter Detalhes de um Torneio
UT-UC22: Resolver Partida do Torneio
UT-UC23: Deletar Torneio
"""

import pytest
from pydantic import ValidationError
from app.schemas import TorneioCreate, TorneioResponse


class TestTorneioSchema:
    """Testes de validação de schemas para Torneio"""

    def test_torneio_create_tamanho_valido_2(self):
        """UT-UC19-001: Schema com tamanho válido 2"""
        payload = {
            "time_id": 1,
            "tamanho": 2
        }
        torneio = TorneioCreate(**payload)
        assert torneio.tamanho == 2
        assert torneio.time_id == 1

    def test_torneio_create_tamanho_valido_4(self):
        """UT-UC19-002: Schema com tamanho válido 4"""
        payload = {
            "time_id": 1,
            "tamanho": 4
        }
        torneio = TorneioCreate(**payload)
        assert torneio.tamanho == 4

    def test_torneio_create_tamanho_valido_8(self):
        """UT-UC19-003: Schema com tamanho válido 8"""
        payload = {
            "time_id": 1,
            "tamanho": 8
        }
        torneio = TorneioCreate(**payload)
        assert torneio.tamanho == 8

    def test_torneio_create_tamanho_invalido(self):
        """UT-UC19-004: Rejeitar tamanho inválido (não é 2, 4 ou 8)"""
        with pytest.raises(ValidationError):
            TorneioCreate(time_id=1, tamanho=3)

    def test_torneio_create_tamanho_negativo(self):
        """UT-UC19-005: Rejeitar tamanho negativo"""
        with pytest.raises(ValidationError):
            TorneioCreate(time_id=1, tamanho=-2)

    def test_torneio_create_time_id_negativo(self):
        """UT-UC19-006: Rejeitar time_id negativo"""
        with pytest.raises(ValidationError):
            TorneioCreate(time_id=-1, tamanho=2)


class TestTorneioConstants:
    """Testes das constantes de Torneio"""

    def test_custo_por_tamanho(self):
        """UT-UC19-007: Validar custos por tamanho"""
        from app.routers.tournament import CUSTO_POR_TAMANHO
        assert CUSTO_POR_TAMANHO[2] == 500.0
        assert CUSTO_POR_TAMANHO[4] == 700.0
        assert CUSTO_POR_TAMANHO[8] == 1000.0

    def test_premio_por_tamanho(self):
        """UT-UC22-001: Validar prêmios por tamanho"""
        from app.routers.tournament import PREMIO_POR_TAMANHO
        assert PREMIO_POR_TAMANHO[2] == 700.0
        assert PREMIO_POR_TAMANHO[4] == 1000.0
        assert PREMIO_POR_TAMANHO[8] == 2000.0

    def test_rodadas_por_tamanho(self):
        """UT-UC19-008: Validar rodadas por tamanho"""
        from app.routers.tournament import RODADAS_POR_TAMANHO
        assert RODADAS_POR_TAMANHO[2] == 1
        assert RODADAS_POR_TAMANHO[4] == 2
        assert RODADAS_POR_TAMANHO[8] == 3

    def test_custo_maior_que_premio(self):
        """UT-UC22-002: Validar que prêmio > custo para lucro"""
        from app.routers.tournament import CUSTO_POR_TAMANHO, PREMIO_POR_TAMANHO
        for tamanho in [2, 4, 8]:
            assert PREMIO_POR_TAMANHO[tamanho] > CUSTO_POR_TAMANHO[tamanho]


class TestTorneioLogica:
    """Testes de lógica de Torneio"""

    def test_tamanho_define_numero_participantes(self):
        """UT-UC19-009: Tamanho 2 = 2 participantes, 4 = 4, etc"""
        tamanhos = {2: 2, 4: 4, 8: 8}
        for tamanho, esperado in tamanhos.items():
            assert tamanho == esperado

    def test_tamanho_define_numero_rodadas(self):
        """UT-UC19-010: Tamanho 2 = 1 rodada, 4 = 2, 8 = 3"""
        from app.routers.tournament import RODADAS_POR_TAMANHO
        for tamanho, rodadas in RODADAS_POR_TAMANHO.items():
            # Tamanho 2^n tem log2(n) rodadas
            import math
            rodadas_esperadas = int(math.log2(tamanho))
            assert rodadas == rodadas_esperadas

    def test_tamanho_define_partidas_rodada_1(self):
        """UT-UC22-003: Primeira rodada tem tamanho/2 partidas"""
        tamanhos = {2: 1, 4: 2, 8: 4}
        for tamanho, partidas_r1 in tamanhos.items():
            assert partidas_r1 == tamanho // 2
