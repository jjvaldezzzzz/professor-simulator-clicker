from sqlalchemy import text


def test_fluxo_cadastro_e_consulta(client):
    response = client.post(
        "/jogadores/",
        json={"nome": "Ana", "email": "ana@example.com", "senha": "123"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "ana@example.com"
    assert data["nome_exibicao"] == "Treinador Iniciante"

    jogador_id = data["id"]
    resposta_get = client.get(f"/jogadores/{jogador_id}")

    assert resposta_get.status_code == 200
    jogador = resposta_get.json()
    assert jogador["nome"] == "Ana"
    assert jogador["email"] == "ana@example.com"
    assert jogador["nome_exibicao"] == "Treinador Iniciante"
