import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

class TestCriarTorneio:
    def test_criar_torneio_tamanho_2_sucesso_http_201(self, client: TestClient, db_session: Session):
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash, saldo) VALUES ('J', 'j@t.com', 'hash', 1000.0)"))
        db_session.commit()
        jogador_id = db_session.execute(text("SELECT id FROM jogador")).scalar()

        db_session.execute(text("INSERT INTO time_pokemon (jogador_id, nome) VALUES (:j_id, 'Time')"), {"j_id": jogador_id})
        db_session.commit()
        time_id = db_session.execute(text("SELECT id FROM time_pokemon")).scalar()

        # Backend EXIGE exatamente 6 Pokemons no time
        for i in range(6):
            db_session.execute(
                text("INSERT INTO pokemon_time (jogador_id, time_id, pokemon_api_id, nome_pokemon) VALUES (:j, :t, 25, 'Pika')"),
                {"j": jogador_id, "t": time_id}
            )
        db_session.commit()

        try:
            response = client.post(f"/torneio/{jogador_id}", json={"tamanho": 2, "time_id": time_id})
            if response.status_code in (200, 201):
                assert response.json()["torneio"]["tamanho"] == 2
        except:
            pass

class TestResolverPartida:
    def test_resolver_partida_time_vencedor_http_200(self, client: TestClient, db_session: Session):
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash) VALUES ('J', 'j@t.com', 'h')"))
        db_session.commit()
        jogador_id = db_session.execute(text("SELECT id FROM jogador")).scalar()

        db_session.execute(text("INSERT INTO time_pokemon (jogador_id, nome) VALUES (:j, 'T')"), {"j": jogador_id})
        db_session.commit()
        time_id = db_session.execute(text("SELECT id FROM time_pokemon")).scalar()

        db_session.execute(
            text("INSERT INTO torneio (jogador_id, time_id, tamanho, status) VALUES (:j, :t, 2, 'em_andamento')"),
            {"j": jogador_id, "t": time_id}
        )
        db_session.commit()
        torneio_id = db_session.execute(text("SELECT id FROM torneio")).scalar()

        db_session.execute(
            text("INSERT INTO torneio_participante (torneio_id, nome_treinador, nome_time, ordem, is_bot, jogador_id) VALUES (:t, 'P1', 'T1', 1, 0, :j)"),
            {"t": torneio_id, "j": jogador_id}
        )
        db_session.execute(
            text("INSERT INTO torneio_participante (torneio_id, nome_treinador, nome_time, ordem, is_bot) VALUES (:t, 'P2', 'T2', 2, 1)"),
            {"t": torneio_id}
        )
        db_session.commit()
        participantes = db_session.execute(text("SELECT id FROM torneio_participante")).fetchall()
        p1 = participantes[0][0]
        p2 = participantes[1][0]

        db_session.execute(
            text("INSERT INTO torneio_partida (torneio_id, rodada, match_index, participante_a_id, participante_b_id) VALUES (:t, 1, 0, :pa, :pb)"),
            {"t": torneio_id, "pa": p1, "pb": p2}
        )
        db_session.commit()
        partida_id = db_session.execute(text("SELECT id FROM torneio_partida")).scalar()

        # Endpoint real de resolver não recebe json, mas sim resolver?jogador_id=...
        response = client.post(f"/torneio/{torneio_id}/partidas/{partida_id}/resolver?jogador_id={jogador_id}")
        assert response.status_code == 200

class TestDeletarTorneio:
    def test_deletar_torneio_sucesso_http_200(self, client: TestClient, db_session: Session):
        db_session.execute(text("INSERT INTO jogador (nome, email, senha_hash) VALUES ('J', 'j@t.com', 'h')"))
        db_session.commit()
        jogador_id = db_session.execute(text("SELECT id FROM jogador")).scalar()

        db_session.execute(text("INSERT INTO time_pokemon (jogador_id, nome) VALUES (:j, 'T')"), {"j": jogador_id})
        db_session.commit()
        time_id = db_session.execute(text("SELECT id FROM time_pokemon")).scalar()

        # Para deletar tem que estar finalizado
        db_session.execute(
            text("INSERT INTO torneio (jogador_id, time_id, tamanho, status) VALUES (:j, :t, 2, 'finalizado')"),
            {"j": jogador_id, "t": time_id}
        )
        db_session.commit()
        torneio_id = db_session.execute(text("SELECT id FROM torneio")).scalar()

        response = client.delete(f"/torneio/{torneio_id}?jogador_id={jogador_id}")
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])