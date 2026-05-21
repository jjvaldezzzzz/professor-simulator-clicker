from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_fluxo_dar_aula_atualiza_saldo():
    # 1. Preparação (Cadastro e Login)
    client.post("/users/register", json={"email": "red@pallet.com", "senha": "123", "nome": "Red"})
    login_res = client.post("/users/login", data={"username": "red@pallet.com", "password": "123"})
    user_id = login_res.json().get("id") 
    
    saldo_inicial = client.get(f"/users/{user_id}").json()["saldo"]
    
    # 2. Ação
    client.post("/game/click", json={"jogador_id": user_id})
    
    # 3. Verificação
    saldo_final = client.get(f"/users/{user_id}").json()["saldo"]
    assert saldo_final == saldo_inicial + 10.0