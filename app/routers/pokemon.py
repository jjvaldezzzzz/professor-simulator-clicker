from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
import httpx
import random
from app.database import get_db
from app import schemas

router = APIRouter(prefix="/pokemon", tags=["Integração PokeAPI"])

CUSTO_GACHA = 100.00
LIMITE_POKEMON_TIME = 6

def _validar_nome_time(nome: str) -> str:
    nome_limpo = nome.strip() if nome else ""
    if not nome_limpo:
        raise HTTPException(status_code=400, detail="Nome do time e obrigatorio.")
    if len(nome_limpo) > 50:
        raise HTTPException(status_code=400, detail="Nome do time deve ter no maximo 50 caracteres.")
    return nome_limpo

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

    return {
        "mensagem": f"Voce capturou um {nome_poke}!",
        "pokemon": nome_poke,
        "imagem": sprite,
        "pokemon_id": novo_poke.id,
        "pokemon_api_id": pokemon_id
    }

@router.get("/times/{jogador_id}")
def listar_times(jogador_id: int, db: Session = Depends(get_db)):
    query = text("""
        SELECT t.id AS time_id, t.nome AS time_nome, t.data_criacao,
               p.id AS pokemon_id, p.pokemon_api_id, p.nome_pokemon, p.sprite_url, p.apelido
        FROM time_pokemon t
        LEFT JOIN pokemon_time p ON p.time_id = t.id AND p.ativo = TRUE
        WHERE t.jogador_id = :id AND t.ativo = TRUE
        ORDER BY t.id, p.id
    """)
    rows = db.execute(query, {"id": jogador_id}).fetchall()
    if not rows:
        return []

    times = []
    por_id = {}
    for row in rows:
        data = row._mapping
        time_id = data["time_id"]
        if time_id not in por_id:
            time = {
                "id": time_id,
                "nome": data["time_nome"],
                "pokemons": []
            }
            por_id[time_id] = time
            times.append(time)

        if data["pokemon_id"] is not None:
            por_id[time_id]["pokemons"].append({
                "id": data["pokemon_id"],
                "pokemon_api_id": data["pokemon_api_id"],
                "nome_pokemon": data["nome_pokemon"],
                "sprite_url": data["sprite_url"],
                "apelido": data["apelido"]
            })

    for time in times:
        time["quantidade"] = len(time["pokemons"])
    return times

@router.get("/{jogador_id}")
def visualizar_time(jogador_id: int, db: Session = Depends(get_db)):
    """UC13: Visualizar Pokemon do Jogador (Usar ANTES de /times para não conflitar)"""
    query = text("""
        SELECT id, pokemon_api_id, nome_pokemon, sprite_url, apelido, time_id, data_obtido
        FROM pokemon_time
        WHERE jogador_id = :id AND ativo = TRUE
        ORDER BY id
    """)
    time = db.execute(query, {"id": jogador_id}).fetchall()
    return [dict(p._mapping) for p in time]

@router.post("/times/{jogador_id}")
def criar_time(jogador_id: int, payload: schemas.TimePokemonCreate, db: Session = Depends(get_db)):
    nome_time = _validar_nome_time(payload.nome)
    jogador = db.execute(text("SELECT id FROM jogador WHERE id = :id AND ativo = TRUE"), {"id": jogador_id}).fetchone()
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador nao encontrado.")

    existente = db.execute(
        text("SELECT id FROM time_pokemon WHERE jogador_id = :id AND nome = :nome AND ativo = TRUE"),
        {"id": jogador_id, "nome": nome_time}
    ).fetchone()
    if existente:
        raise HTTPException(status_code=400, detail="Ja existe um time com esse nome.")

    novo_time = db.execute(
        text("""
            INSERT INTO time_pokemon (jogador_id, nome)
            VALUES (:id, :nome)
            RETURNING id, nome
        """),
        {"id": jogador_id, "nome": nome_time}
    ).fetchone()
    db.commit()
    return dict(novo_time._mapping)

@router.put("/times/{jogador_id}/{time_id}")
def renomear_time(jogador_id: int, time_id: int, payload: schemas.TimePokemonRename, db: Session = Depends(get_db)):
    nome_time = _validar_nome_time(payload.nome)
    time_existente = db.execute(
        text("SELECT id FROM time_pokemon WHERE id = :time_id AND jogador_id = :jogador_id AND ativo = TRUE"),
        {"time_id": time_id, "jogador_id": jogador_id}
    ).fetchone()
    if not time_existente:
        raise HTTPException(status_code=404, detail="Time nao encontrado.")

    duplicado = db.execute(
        text("SELECT id FROM time_pokemon WHERE jogador_id = :jogador_id AND nome = :nome AND ativo = TRUE AND id <> :time_id"),
        {"jogador_id": jogador_id, "nome": nome_time, "time_id": time_id}
    ).fetchone()
    if duplicado:
        raise HTTPException(status_code=400, detail="Ja existe um time com esse nome.")

    atualizado = db.execute(
        text("UPDATE time_pokemon SET nome = :nome WHERE id = :time_id RETURNING id, nome"),
        {"nome": nome_time, "time_id": time_id}
    ).fetchone()
    db.commit()
    return dict(atualizado._mapping)

@router.delete("/times/{jogador_id}/{time_id}")
def deletar_time(jogador_id: int, time_id: int, db: Session = Depends(get_db)):
    time_existente = db.execute(
        text("SELECT id FROM time_pokemon WHERE id = :time_id AND jogador_id = :jogador_id AND ativo = TRUE"),
        {"time_id": time_id, "jogador_id": jogador_id}
    ).fetchone()
    if not time_existente:
        raise HTTPException(status_code=404, detail="Time nao encontrado.")

    db.execute(text("UPDATE pokemon_time SET time_id = NULL WHERE time_id = :time_id"), {"time_id": time_id})
    db.execute(text("DELETE FROM time_pokemon WHERE id = :time_id"), {"time_id": time_id})
    db.commit()
    return {"mensagem": "Time deletado com sucesso!"}

@router.post("/times/{jogador_id}/{time_id}/adicionar")
def adicionar_pokemon_ao_time(
    jogador_id: int,
    time_id: int,
    payload: schemas.TimePokemonAdicionar,
    db: Session = Depends(get_db)
):
    time_existente = db.execute(
        text("SELECT id FROM time_pokemon WHERE id = :time_id AND jogador_id = :jogador_id AND ativo = TRUE"),
        {"time_id": time_id, "jogador_id": jogador_id}
    ).fetchone()
    if not time_existente:
        raise HTTPException(status_code=404, detail="Time nao encontrado.")

    pokemon = db.execute(
        text("""
            SELECT id, time_id
            FROM pokemon_time
            WHERE id = :pokemon_id AND jogador_id = :jogador_id AND ativo = TRUE
        """),
        {"pokemon_id": payload.pokemon_id, "jogador_id": jogador_id}
    ).fetchone()
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokemon nao encontrado.")

    if pokemon.time_id == time_id:
        return {"mensagem": "Pokemon ja esta nesse time."}

    quantidade = db.execute(
        text("SELECT COUNT(*) FROM pokemon_time WHERE time_id = :time_id AND ativo = TRUE"),
        {"time_id": time_id}
    ).scalar()
    if quantidade >= LIMITE_POKEMON_TIME:
        raise HTTPException(status_code=400, detail="Time cheio. Maximo de 6 Pokemon.")

    db.execute(
        text("UPDATE pokemon_time SET time_id = :time_id WHERE id = :pokemon_id"),
        {"time_id": time_id, "pokemon_id": payload.pokemon_id}
    )
    db.commit()
    return {"mensagem": "Pokemon adicionado ao time!"}

@router.delete("/libertar/{jogador_id}/{pokemon_id}")
def libertar_pokemon(jogador_id: int, pokemon_id: int, db: Session = Depends(get_db)):
    pokemon = db.execute(
        text("""
            SELECT id
            FROM pokemon_time
            WHERE id = :pokemon_id AND jogador_id = :jogador_id AND ativo = TRUE
        """),
        {"pokemon_id": pokemon_id, "jogador_id": jogador_id}
    ).fetchone()

    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokemon nao encontrado.")

    db.execute(
        text("DELETE FROM pokemon_time WHERE id = :pokemon_id"),
        {"pokemon_id": pokemon_id}
    )
    db.commit()
    return {"mensagem": "Pokemon liberado com sucesso!"}