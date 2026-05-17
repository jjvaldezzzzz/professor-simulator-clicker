from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
import httpx
import random
from app.database import get_db

router = APIRouter(prefix="/pokemon", tags=["Integração PokeAPI"])

CUSTO_GACHA = 100.00

@router.post("/gacha/{jogador_id}")
async def sortear_pokemon(jogador_id: int, db: Session = Depends(get_db)):
    """UC13: Sortear Pokémon (Integração API Externa)"""
    
    jogador = db.execute(text("SELECT saldo FROM jogador WHERE id = :id"), {"id": jogador_id}).fetchone()
    if not jogador or jogador.saldo < CUSTO_GACHA:
        raise HTTPException(status_code=400, detail=f"Saldo insuficiente. Custa {CUSTO_GACHA} moedas.")

    pokemon_id = random.randint(1, 1025)
    
    # Chamada na API externa
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=503, detail="Falha de comunicação com a PokeAPI.")
        
        dados = response.json()
        nome_poke = dados["name"].capitalize()
        sprite = dados["sprites"]["front_default"]

    # Desconta saldo e salva no banco
    db.execute(text("UPDATE jogador SET saldo = saldo - :custo WHERE id = :id"), {"custo": CUSTO_GACHA, "id": jogador_id})
    query_insert = text("""
        INSERT INTO pokemon_time (jogador_id, pokemon_api_id, nome_pokemon, sprite_url)
        VALUES (:j_id, :api_id, :nome, :sprite) RETURNING id
    """)
    novo_poke = db.execute(query_insert, {"j_id": jogador_id, "api_id": pokemon_id, "nome": nome_poke, "sprite": sprite}).fetchone()
    
    db.execute(text("INSERT INTO transacao (jogador_id, tipo, valor, descricao) VALUES (:id, 'sorteio_pokemon', :valor, :desc)"), 
               {"id": jogador_id, "valor": -CUSTO_GACHA, "desc": f"Sorteou {nome_poke}"})
    db.commit()

    return {"mensagem": f"Você capturou um {nome_poke}!", "pokemon": nome_poke, "imagem": sprite}

@router.get("/{jogador_id}")
def visualizar_time(jogador_id: int, db: Session = Depends(get_db)):
    """UC14: Visualizar Time Pokémon"""
    query = text("SELECT id, pokemon_api_id, nome_pokemon, sprite_url, data_obtido FROM pokemon_time WHERE jogador_id = :id AND ativo = TRUE")
    time = db.execute(query, {"id": jogador_id}).fetchall()
    return [dict(p._mapping) for p in time]