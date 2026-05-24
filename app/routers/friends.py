from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db

router = APIRouter(prefix="/amigos", tags=["Sistema de Amigos"])


# ==================== MODELOS PYDANTIC ====================
class AdicionarAmigoRequest(BaseModel):
    jogador_id: int
    amigo_id: int


class AtualizarFavoritoRequest(BaseModel):
    jogador_id: int


class RemoverAmigoRequest(BaseModel):
    jogador_id: int


# ==================== ENDPOINTS ====================
@router.post("/adicionar")
def adicionar_amigo(request: AdicionarAmigoRequest, db: Session = Depends(get_db)):
    """
    Adiciona um novo amigo à conta do jogador (bilateral).
    
    Se a amizade já existe, retorna erro 400.
    Caso contrário, insere duas linhas na tabela amizade (A->B e B->A).
    """
    jogador_id = request.jogador_id
    amigo_id = request.amigo_id
    
    # Validação: não pode adicionar a si mesmo
    if jogador_id == amigo_id:
        raise HTTPException(status_code=400, detail="Você não pode se adicionar como amigo.")
    
    # Validação: verifica se ambos os jogadores existem e estão ativos
    query_check = text("SELECT id FROM jogador WHERE id = :id AND ativo = TRUE")
    jogador = db.execute(query_check, {"id": jogador_id}).fetchone()
    amigo = db.execute(query_check, {"id": amigo_id}).fetchone()
    
    if not jogador or not amigo:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")
    
    # Verifica se já são amigos (em qualquer direção)
    query_existe = text("""
        SELECT id FROM amizade 
        WHERE (
            (jogador_id = :jogador_id AND amigo_id = :amigo_id) 
            OR (jogador_id = :amigo_id AND amigo_id = :jogador_id)
        )
        AND ativo = TRUE
    """)
    amizade_existente = db.execute(query_existe, {
        "jogador_id": jogador_id,
        "amigo_id": amigo_id
    }).fetchone()
    
    if amizade_existente:
        raise HTTPException(status_code=400, detail="Você já é amigo deste jogador.")
    
    # Insere a amizade BILATERAL (A -> B e B -> A)
    query_insert = text("""
        INSERT INTO amizade (jogador_id, amigo_id) 
        VALUES (:jogador_id, :amigo_id), (:amigo_id, :jogador_id)
        RETURNING id, jogador_id, amigo_id, data_amizade, favorito
    """)
    
    amizades = db.execute(query_insert, {
        "jogador_id": jogador_id,
        "amigo_id": amigo_id
    }).fetchall()
    
    db.commit()
    
    return {
        "mensagem": "Amigo adicionado com sucesso!",
        "amizades": [dict(a._mapping) for a in amizades]
    }


@router.get("/{jogador_id}")
def obter_amigos(jogador_id: int, db: Session = Depends(get_db)):
    """Retorna a lista de amigos do jogador (ordenada por favorito e data)"""
    
    # Verifica se o jogador existe
    query_check = text("SELECT id FROM jogador WHERE id = :id AND ativo = TRUE")
    jogador = db.execute(query_check, {"id": jogador_id}).fetchone()
    
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")
    
    # Busca todos os amigos do jogador
    query = text("""
        SELECT 
            a.id,
            j.id as amigo_id,
            j.nome,
            j.nome_exibicao,
            j.email,
            j.saldo,
            a.favorito,
            a.data_amizade
        FROM amizade a
        JOIN jogador j ON a.amigo_id = j.id
        WHERE a.jogador_id = :jogador_id AND a.ativo = TRUE
        ORDER BY a.favorito DESC, a.data_amizade DESC
    """)
    
    amigos = db.execute(query, {"jogador_id": jogador_id}).fetchall()
    
    return {
        "total": len(amigos),
        "amigos": [dict(amigo._mapping) for amigo in amigos]
    }


@router.get("/{jogador_id}/favoritos")
def obter_amigos_favoritos(jogador_id: int, db: Session = Depends(get_db)):
    """Retorna apenas os amigos marcados como favoritos"""
    
    # Verifica se o jogador existe
    query_check = text("SELECT id FROM jogador WHERE id = :id AND ativo = TRUE")
    jogador = db.execute(query_check, {"id": jogador_id}).fetchone()
    
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")
    
    # Busca apenas os amigos favoritos
    query = text("""
        SELECT 
            a.id,
            j.id as amigo_id,
            j.nome,
            j.nome_exibicao,
            j.email,
            j.saldo,
            a.data_amizade
        FROM amizade a
        JOIN jogador j ON a.amigo_id = j.id
        WHERE a.jogador_id = :jogador_id AND a.ativo = TRUE AND a.favorito = TRUE
        ORDER BY a.data_amizade DESC
    """)
    
    amigos_favoritos = db.execute(query, {"jogador_id": jogador_id}).fetchall()
    
    return {
        "total": len(amigos_favoritos),
        "amigos_favoritos": [dict(amigo._mapping) for amigo in amigos_favoritos]
    }


@router.put("/{amizade_id}/favoritar")
def favoritar_amigo(amizade_id: int, request: AtualizarFavoritoRequest, db: Session = Depends(get_db)):
    """Marca um amigo como favorito"""
    jogador_id = request.jogador_id
    
    # Verifica se a amizade existe e pertence ao jogador
    query_check = text("""
        SELECT id, jogador_id FROM amizade 
        WHERE id = :id AND jogador_id = :jogador_id AND ativo = TRUE
    """)
    amizade = db.execute(query_check, {
        "id": amizade_id,
        "jogador_id": jogador_id
    }).fetchone()
    
    if not amizade:
        raise HTTPException(status_code=404, detail="Amizade não encontrada.")
    
    # Atualiza para favorito = TRUE
    query_update = text("""
        UPDATE amizade 
        SET favorito = TRUE 
        WHERE id = :id 
        RETURNING id, favorito
    """)
    
    amizade_atualizada = db.execute(query_update, {"id": amizade_id}).fetchone()
    db.commit()
    
    return {
        "mensagem": "Amigo marcado como favorito!",
        "amizade": dict(amizade_atualizada._mapping)
    }


@router.put("/{amizade_id}/desfavoritar")
def desfavoritar_amigo(amizade_id: int, request: AtualizarFavoritoRequest, db: Session = Depends(get_db)):
    """Remove um amigo da lista de favoritos"""
    jogador_id = request.jogador_id
    
    # Verifica se a amizade existe e pertence ao jogador
    query_check = text("""
        SELECT id, jogador_id FROM amizade 
        WHERE id = :id AND jogador_id = :jogador_id AND ativo = TRUE
    """)
    amizade = db.execute(query_check, {
        "id": amizade_id,
        "jogador_id": jogador_id
    }).fetchone()
    
    if not amizade:
        raise HTTPException(status_code=404, detail="Amizade não encontrada.")
    
    # Atualiza para favorito = FALSE
    query_update = text("""
        UPDATE amizade 
        SET favorito = FALSE 
        WHERE id = :id 
        RETURNING id, favorito
    """)
    
    amizade_atualizada = db.execute(query_update, {"id": amizade_id}).fetchone()
    db.commit()
    
    return {
        "mensagem": "Amigo removido dos favoritos!",
        "amizade": dict(amizade_atualizada._mapping)
    }


@router.delete("/{amizade_id}")
def remover_amigo(amizade_id: int, request: RemoverAmigoRequest, db: Session = Depends(get_db)):
    """Remove um amigo da lista do jogador (soft delete)"""
    jogador_id = request.jogador_id
    
    # Verifica se a amizade existe e pertence ao jogador
    query_check = text("""
        SELECT id, jogador_id, amigo_id FROM amizade 
        WHERE id = :id AND jogador_id = :jogador_id AND ativo = TRUE
    """)
    amizade = db.execute(query_check, {
        "id": amizade_id,
        "jogador_id": jogador_id
    }).fetchone()
    
    if not amizade:
        raise HTTPException(status_code=404, detail="Amizade não encontrada.")
    
    # Marca como inativo (soft delete)
    query_delete = text("""
        UPDATE amizade 
        SET ativo = FALSE 
        WHERE id = :id
    """)
    
    db.execute(query_delete, {"id": amizade_id})
    db.commit()
    
    return {"mensagem": "Amigo removido com sucesso!"}


@router.post("/buscar")
def buscar_jogador_para_amizade(email: str = Query(..., min_length=5), db: Session = Depends(get_db)):
    """Busca jogadores pelo e-mail no banco de dados"""
    
    # Valida o formato do email
    if "@" not in email or "." not in email:
        raise HTTPException(status_code=400, detail="Digite um e-mail válido.")
    
    # Busca todos os jogadores com o email fornecido
    query = text("""
        SELECT 
            j.id,
            j.nome,
            j.nome_exibicao,
            j.email,
            j.saldo
        FROM jogador j
        WHERE j.email = :email
        AND j.ativo = TRUE
    """)
    
    resultados = db.execute(query, {
        "email": email.strip().lower()
    }).fetchall()
    
    if not resultados:
        raise HTTPException(status_code=404, detail="Nenhum jogador encontrado com esse e-mail.")
    
    return {
        "resultados": [dict(resultado._mapping) for resultado in resultados]
    }
