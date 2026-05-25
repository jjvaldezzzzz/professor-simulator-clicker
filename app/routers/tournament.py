from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
import httpx
import random
from app.database import get_db
from app import schemas

router = APIRouter(prefix="/torneio", tags=["Torneio Pokemon"])

CUSTO_POR_TAMANHO = {
    2: 500.0,
    4: 700.0,
    8: 1000.0,
}
PREMIO_POR_TAMANHO = {
    2: 700.0,
    4: 1000.0,
    8: 2000.0,
}
RODADAS_POR_TAMANHO = {2: 1, 4: 2, 8: 3}


def _validar_nome_torneio(nome: str) -> str:
    nome_limpo = nome.strip() if nome else ""
    if not nome_limpo:
        raise HTTPException(status_code=400, detail="Nome do torneio e obrigatorio.")
    if len(nome_limpo) > 50:
        raise HTTPException(status_code=400, detail="Nome do torneio deve ter no maximo 50 caracteres.")
    return nome_limpo


async def _buscar_pokemon(client: httpx.AsyncClient, api_id: int) -> dict:
    response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{api_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=503, detail="Falha de comunicacao com a PokeAPI.")

    dados = response.json()
    bst = sum(stat["base_stat"] for stat in dados.get("stats", []))
    return {
        "pokemon_api_id": api_id,
        "nome_pokemon": dados["name"].capitalize(),
        "sprite_url": dados["sprites"]["front_default"],
        "bst": bst,
    }


def _inserir_participante(
    db: Session,
    torneio_id: int,
    nome_treinador: str,
    nome_time: str,
    total_bst: int,
    ordem: int,
    is_bot: bool,
    jogador_id: Optional[int] = None,
    time_id: Optional[int] = None,
):
    query = text("""
        INSERT INTO torneio_participante (
            torneio_id,
            nome_treinador,
            nome_time,
            total_bst,
            ordem,
            is_bot,
            jogador_id,
            time_id
        )
        VALUES (:torneio_id, :nome_treinador, :nome_time, :total_bst, :ordem, :is_bot, :jogador_id, :time_id)
        RETURNING id
    """)
    return db.execute(
        query,
        {
            "torneio_id": torneio_id,
            "nome_treinador": nome_treinador,
            "nome_time": nome_time,
            "total_bst": total_bst,
            "ordem": ordem,
            "is_bot": is_bot,
            "jogador_id": jogador_id,
            "time_id": time_id,
        },
    ).fetchone()


def _criar_partidas(db: Session, torneio_id: int, participantes_ordenados: list[dict], tamanho: int):
    total_rodadas = RODADAS_POR_TAMANHO[tamanho]
    partidas = []

    # Rodada 1
    partidas_rodada = tamanho // 2
    for match_index in range(partidas_rodada):
        participante_a = participantes_ordenados[match_index * 2]["id"]
        participante_b = participantes_ordenados[match_index * 2 + 1]["id"]
        partida_id = db.execute(
            text("""
                INSERT INTO torneio_partida (
                    torneio_id,
                    rodada,
                    match_index,
                    participante_a_id,
                    participante_b_id
                )
                VALUES (:torneio_id, 1, :match_index, :a_id, :b_id)
                RETURNING id
            """),
            {
                "torneio_id": torneio_id,
                "match_index": match_index,
                "a_id": participante_a,
                "b_id": participante_b,
            },
        ).fetchone().id
        partidas.append({
            "id": partida_id,
            "rodada": 1,
            "match_index": match_index,
            "participante_a_id": participante_a,
            "participante_b_id": participante_b,
            "vencedor_id": None,
        })

    # Rodadas seguintes
    for rodada in range(2, total_rodadas + 1):
        partidas_rodada = tamanho // (2 ** rodada)
        for match_index in range(partidas_rodada):
            partida_id = db.execute(
                text("""
                    INSERT INTO torneio_partida (torneio_id, rodada, match_index)
                    VALUES (:torneio_id, :rodada, :match_index)
                    RETURNING id
                """),
                {"torneio_id": torneio_id, "rodada": rodada, "match_index": match_index},
            ).fetchone().id
            partidas.append({
                "id": partida_id,
                "rodada": rodada,
                "match_index": match_index,
                "participante_a_id": None,
                "participante_b_id": None,
                "vencedor_id": None,
            })

    return partidas


def _montar_detalhes_torneio(db: Session, torneio_id: int) -> dict:
    torneio = db.execute(
        text("""
            SELECT id, jogador_id, nome, tamanho, status, premio, custo, vencedor_participante_id, criado_em, finalizado_em
            FROM torneio
            WHERE id = :id
        """),
        {"id": torneio_id},
    ).fetchone()

    if not torneio:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado.")

    rows = db.execute(
        text("""
            SELECT tp.id AS participante_id,
                   tp.nome_treinador,
                   tp.nome_time,
                   tp.total_bst,
                   tp.is_bot,
                   pk.pokemon_api_id,
                   pk.nome_pokemon,
                   pk.sprite_url,
                   pk.bst
            FROM torneio_participante tp
            LEFT JOIN torneio_pokemon pk ON pk.torneio_participante_id = tp.id
            WHERE tp.torneio_id = :id
            ORDER BY tp.ordem, pk.id
        """),
        {"id": torneio_id},
    ).fetchall()

    participantes = []
    participantes_map: dict[int, dict] = {}

    for row in rows:
        data = row._mapping
        participante_id = data["participante_id"]
        if participante_id not in participantes_map:
            participante = {
                "id": participante_id,
                "nome_treinador": data["nome_treinador"],
                "nome_time": data["nome_time"],
                "is_bot": bool(data["is_bot"]),
                "total_bst": int(data["total_bst"]),
                "pokemons": [],
            }
            participantes_map[participante_id] = participante
            participantes.append(participante)

        if data["pokemon_api_id"] is not None:
            participantes_map[participante_id]["pokemons"].append({
                "pokemon_api_id": data["pokemon_api_id"],
                "nome_pokemon": data["nome_pokemon"],
                "sprite_url": data["sprite_url"],
                "bst": int(data["bst"]),
            })

    partidas_rows = db.execute(
        text("""
            SELECT id, rodada, match_index, participante_a_id, participante_b_id, vencedor_id
            FROM torneio_partida
            WHERE torneio_id = :id
            ORDER BY rodada, match_index
        """),
        {"id": torneio_id},
    ).fetchall()

    partidas = [dict(row._mapping) for row in partidas_rows]

    return {
        "torneio": {
            "id": torneio.id,
            "jogador_id": torneio.jogador_id,
            "nome": torneio.nome,
            "tamanho": torneio.tamanho,
            "status": torneio.status,
            "premio": float(torneio.premio),
            "custo": float(torneio.custo),
            "vencedor_id": torneio.vencedor_participante_id,
            "criado_em": torneio.criado_em,
            "finalizado_em": torneio.finalizado_em,
        },
        "participantes": participantes,
        "partidas": partidas,
    }


@router.post("/{jogador_id}")
async def criar_torneio(jogador_id: int, payload: schemas.TorneioCreate, db: Session = Depends(get_db)):
    if payload.tamanho not in RODADAS_POR_TAMANHO:
        raise HTTPException(status_code=400, detail="Tamanho do torneio invalido.")

    custo = CUSTO_POR_TAMANHO[payload.tamanho]
    premio = PREMIO_POR_TAMANHO[payload.tamanho]

    jogador = db.execute(
        text("SELECT id, saldo, nome_exibicao, nome FROM jogador WHERE id = :id AND ativo = TRUE"),
        {"id": jogador_id},
    ).fetchone()
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador nao encontrado.")

    if float(jogador.saldo) < custo:
        raise HTTPException(status_code=400, detail="Saldo insuficiente para entrar no torneio.")

    time = db.execute(
        text("""
            SELECT id, nome
            FROM time_pokemon
            WHERE id = :time_id AND jogador_id = :jogador_id AND ativo = TRUE
        """),
        {"time_id": payload.time_id, "jogador_id": jogador_id},
    ).fetchone()
    if not time:
        raise HTTPException(status_code=404, detail="Time nao encontrado.")

    pokemons_time = db.execute(
        text("""
            SELECT pokemon_api_id
            FROM pokemon_time
            WHERE time_id = :time_id AND ativo = TRUE
            ORDER BY id
        """),
        {"time_id": payload.time_id},
    ).fetchall()

    if len(pokemons_time) != 6:
        raise HTTPException(status_code=400, detail="O time precisa ter exatamente 6 Pokemon.")

    try:
        db.execute(
            text("UPDATE jogador SET saldo = saldo - :custo WHERE id = :id"),
            {"custo": custo, "id": jogador_id},
        )
        db.execute(
            text("INSERT INTO transacao (jogador_id, tipo, valor, descricao) VALUES (:id, 'torneio_inscricao', :valor, :desc)"),
            {"id": jogador_id, "valor": -custo, "desc": "Inscricao em torneio"},
        )

        torneio_id = db.execute(
            text("""
                INSERT INTO torneio (jogador_id, time_id, tamanho, custo, premio, status)
                VALUES (:jogador_id, :time_id, :tamanho, :custo, :premio, 'em_andamento')
                RETURNING id
            """),
            {
                "jogador_id": jogador_id,
                "time_id": payload.time_id,
                "tamanho": payload.tamanho,
                "custo": custo,
                "premio": premio,
            },
        ).fetchone().id

        participantes = []

        nome_treinador = jogador.nome_exibicao or jogador.nome or "Treinador"
        async with httpx.AsyncClient() as client:
            total_bst = 0
            participante_row = _inserir_participante(
                db,
                torneio_id,
                nome_treinador,
                time.nome,
                0,
                1,
                False,
                jogador_id=jogador_id,
                time_id=payload.time_id,
            )
            participante_id = participante_row.id
            for poke in pokemons_time:
                pokemon_info = await _buscar_pokemon(client, poke.pokemon_api_id)
                total_bst += pokemon_info["bst"]
                db.execute(
                    text("""
                        INSERT INTO torneio_pokemon (
                            torneio_participante_id,
                            pokemon_api_id,
                            nome_pokemon,
                            sprite_url,
                            bst
                        )
                        VALUES (:participante_id, :api_id, :nome, :sprite, :bst)
                    """),
                    {
                        "participante_id": participante_id,
                        "api_id": pokemon_info["pokemon_api_id"],
                        "nome": pokemon_info["nome_pokemon"],
                        "sprite": pokemon_info["sprite_url"],
                        "bst": pokemon_info["bst"],
                    },
                )

            db.execute(
                text("UPDATE torneio_participante SET total_bst = :total WHERE id = :id"),
                {"total": total_bst, "id": participante_id},
            )

            participantes.append({"id": participante_id, "total_bst": total_bst, "ordem": 1})

            bots = payload.tamanho - 1
            for i in range(bots):
                bot_nome = f"Bot {i + 1}"
                bot_time_nome = f"Time {bot_nome}"
                bot_row = _inserir_participante(db, torneio_id, bot_nome, bot_time_nome, 0, i + 2, True)
                bot_id = bot_row.id
                bot_total = 0
                for _ in range(6):
                    api_id = random.randint(1, 1025)
                    pokemon_info = await _buscar_pokemon(client, api_id)
                    bot_total += pokemon_info["bst"]
                    db.execute(
                        text("""
                            INSERT INTO torneio_pokemon (
                                torneio_participante_id,
                                pokemon_api_id,
                                nome_pokemon,
                                sprite_url,
                                bst
                            )
                            VALUES (:participante_id, :api_id, :nome, :sprite, :bst)
                        """),
                        {
                            "participante_id": bot_id,
                            "api_id": pokemon_info["pokemon_api_id"],
                            "nome": pokemon_info["nome_pokemon"],
                            "sprite": pokemon_info["sprite_url"],
                            "bst": pokemon_info["bst"],
                        },
                    )

                db.execute(
                    text("UPDATE torneio_participante SET total_bst = :total WHERE id = :id"),
                    {"total": bot_total, "id": bot_id},
                )
                participantes.append({"id": bot_id, "total_bst": bot_total, "ordem": i + 2})

        participantes_ordenados = sorted(participantes, key=lambda item: item["ordem"])
        _criar_partidas(db, torneio_id, participantes_ordenados, payload.tamanho)

        db.commit()

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao criar torneio.")

    return _montar_detalhes_torneio(db, torneio_id)


@router.get("/{jogador_id}")
def listar_torneios(jogador_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        text("""
            SELECT t.id, t.nome, t.tamanho, t.status, t.criado_em, t.finalizado_em, t.vencedor_participante_id,
                   tp.nome_treinador AS vencedor_nome
            FROM torneio t
            LEFT JOIN torneio_participante tp ON tp.id = t.vencedor_participante_id
            WHERE t.jogador_id = :id
            ORDER BY t.id DESC
        """),
        {"id": jogador_id},
    ).fetchall()

    return [dict(row._mapping) for row in rows]


@router.get("/{jogador_id}/{torneio_id}")
def obter_torneio(jogador_id: int, torneio_id: int, db: Session = Depends(get_db)):
    torneio = db.execute(
        text("SELECT id FROM torneio WHERE id = :id AND jogador_id = :jogador_id"),
        {"id": torneio_id, "jogador_id": jogador_id},
    ).fetchone()

    if not torneio:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado.")

    return _montar_detalhes_torneio(db, torneio_id)


@router.post("/{torneio_id}/partidas/{partida_id}/resolver")
def resolver_partida(torneio_id: int, partida_id: int, jogador_id: int, db: Session = Depends(get_db)):
    torneio = db.execute(
        text("""
            SELECT id, jogador_id, nome, tamanho, status, premio
            FROM torneio
            WHERE id = :id AND jogador_id = :jogador_id
        """),
        {"id": torneio_id, "jogador_id": jogador_id},
    ).fetchone()

    if not torneio:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado.")

    if torneio.status == "finalizado":
        raise HTTPException(status_code=400, detail="Torneio ja foi finalizado.")

    partida = db.execute(
        text("""
            SELECT id, rodada, match_index, participante_a_id, participante_b_id, vencedor_id
            FROM torneio_partida
            WHERE id = :id AND torneio_id = :torneio_id
        """),
        {"id": partida_id, "torneio_id": torneio_id},
    ).fetchone()

    if not partida:
        raise HTTPException(status_code=404, detail="Partida nao encontrada.")

    if partida.vencedor_id is not None:
        raise HTTPException(status_code=400, detail="Partida ja foi resolvida.")

    if partida.participante_a_id is None or partida.participante_b_id is None:
        raise HTTPException(status_code=400, detail="Partida ainda nao esta pronta.")

    participantes = db.execute(
        text("""
            SELECT id, total_bst, jogador_id
            FROM torneio_participante
            WHERE id = :a_id OR id = :b_id
        """),
        {"a_id": partida.participante_a_id, "b_id": partida.participante_b_id},
    ).fetchall()

    if len(participantes) != 2:
        raise HTTPException(status_code=404, detail="Participantes invalidos.")

    participante_a = next(p for p in participantes if p.id == partida.participante_a_id)
    participante_b = next(p for p in participantes if p.id == partida.participante_b_id)

    if participante_a.total_bst > participante_b.total_bst:
        vencedor = participante_a
    elif participante_b.total_bst > participante_a.total_bst:
        vencedor = participante_b
    else:
        vencedor = random.choice([participante_a, participante_b])

    rounds_total = RODADAS_POR_TAMANHO.get(int(torneio.tamanho))
    if not rounds_total:
        raise HTTPException(status_code=400, detail="Tamanho do torneio invalido.")

    db.execute(
        text("UPDATE torneio_partida SET vencedor_id = :vencedor_id, resolvido_em = CURRENT_TIMESTAMP WHERE id = :id"),
        {"vencedor_id": vencedor.id, "id": partida.id},
    )

    venceu = False
    novo_saldo = None

    if partida.rodada < rounds_total:
        proxima_rodada = partida.rodada + 1
        proximo_index = partida.match_index // 2
        if partida.match_index % 2 == 0:
            db.execute(
                text("""
                    UPDATE torneio_partida
                    SET participante_a_id = :vencedor_id
                    WHERE torneio_id = :torneio_id AND rodada = :rodada AND match_index = :match_index
                """),
                {
                    "vencedor_id": vencedor.id,
                    "torneio_id": torneio_id,
                    "rodada": proxima_rodada,
                    "match_index": proximo_index,
                },
            )
        else:
            db.execute(
                text("""
                    UPDATE torneio_partida
                    SET participante_b_id = :vencedor_id
                    WHERE torneio_id = :torneio_id AND rodada = :rodada AND match_index = :match_index
                """),
                {
                    "vencedor_id": vencedor.id,
                    "torneio_id": torneio_id,
                    "rodada": proxima_rodada,
                    "match_index": proximo_index,
                },
            )
    else:
        db.execute(
            text("""
                UPDATE torneio
                SET status = 'finalizado',
                    vencedor_participante_id = :vencedor_id,
                    finalizado_em = CURRENT_TIMESTAMP
                WHERE id = :id
            """),
            {"vencedor_id": vencedor.id, "id": torneio_id},
        )

        venceu = vencedor.jogador_id == jogador_id
        if venceu:
            novo_saldo = db.execute(
                text("UPDATE jogador SET saldo = saldo + :premio WHERE id = :id RETURNING saldo"),
                {"premio": torneio.premio, "id": jogador_id},
            ).scalar()
            db.execute(
                text("INSERT INTO transacao (jogador_id, tipo, valor, descricao) VALUES (:id, 'torneio_premio', :valor, :desc)"),
                {"id": jogador_id, "valor": torneio.premio, "desc": "Premio do torneio"},
            )
        else:
            novo_saldo = db.execute(
                text("SELECT saldo FROM jogador WHERE id = :id"),
                {"id": jogador_id},
            ).scalar()

    db.commit()

    return {
        "vencedor_id": vencedor.id,
        "torneio_status": "finalizado" if partida.rodada == rounds_total else "em_andamento",
        "venceu": venceu,
        "novo_saldo": float(novo_saldo) if novo_saldo is not None else None,
    }


@router.put("/{jogador_id}/{torneio_id}")
def renomear_torneio(jogador_id: int, torneio_id: int, payload: schemas.TorneioRename, db: Session = Depends(get_db)):
    """UC19.2: Renomear Torneio"""
    nome_torneio = _validar_nome_torneio(payload.nome)
    
    torneio_existente = db.execute(
        text("SELECT id FROM torneio WHERE id = :torneio_id AND jogador_id = :jogador_id"),
        {"torneio_id": torneio_id, "jogador_id": jogador_id}
    ).fetchone()
    
    if not torneio_existente:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado.")
    
    # Verifica se já existe outro torneio com o mesmo nome (do mesmo jogador)
    duplicado = db.execute(
        text("SELECT id FROM torneio WHERE jogador_id = :jogador_id AND nome = :nome AND id <> :torneio_id"),
        {"jogador_id": jogador_id, "nome": nome_torneio, "torneio_id": torneio_id}
    ).fetchone()
    
    if duplicado:
        raise HTTPException(status_code=400, detail="Ja existe outro torneio com esse nome.")
    
    atualizado = db.execute(
        text("UPDATE torneio SET nome = :nome WHERE id = :torneio_id RETURNING id, nome"),
        {"nome": nome_torneio, "torneio_id": torneio_id}
    ).fetchone()
    
    db.commit()
    return dict(atualizado._mapping)


@router.delete("/{torneio_id}")
def deletar_torneio(torneio_id: int, jogador_id: int, db: Session = Depends(get_db)):
    torneio = db.execute(
        text("SELECT id, jogador_id, status FROM torneio WHERE id = :id AND jogador_id = :jogador_id"),
        {"id": torneio_id, "jogador_id": jogador_id},
    ).fetchone()

    if not torneio:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado.")

    if torneio.status != "finalizado":
        raise HTTPException(status_code=400, detail="Finalize o torneio antes de deletar.")

    db.execute(text("DELETE FROM torneio WHERE id = :id"), {"id": torneio_id})
    db.commit()

    return {"mensagem": "Torneio deletado com sucesso."}
