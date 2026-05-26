from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas

router = APIRouter(prefix="/loja", tags=["Catálogo e Loja"])

@router.post("/itens", status_code=status.HTTP_201_CREATED)
def cadastrar_item(item: schemas.ItemCreate, jogador_id: int, db: Session = Depends(get_db)):
    """UC07: Cadastrar Novo Item na Loja (Apenas Admin)"""
    
    # 1. Verifica se quem está chamando a rota é realmente um admin
    jogador = db.execute(text("SELECT is_admin FROM jogador WHERE id = :id"), {"id": jogador_id}).fetchone()
    
    if not jogador or not jogador.is_admin:
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas o Professor/Admin pode criar itens.")
    
    # 2. Validações do item
    if item.preco <= 0:
        raise HTTPException(status_code=400, detail="Preco deve ser maior que zero.")
    if item.multiplicador <= 0:
        raise HTTPException(status_code=400, detail="Multiplicador deve ser maior que zero.")

    # 2. Se passou, cria o item normalmente
    query = text("""
        INSERT INTO item (nome, descricao, preco, multiplicador, tipo, raridade, vendivel) 
        VALUES (:nome, :descricao, :preco, :multiplicador, :tipo, :raridade, :vendivel)
        RETURNING id, nome, preco, multiplicador
    """)
    novo_item = db.execute(query, item.dict()).fetchone()
    db.execute(
        text("INSERT INTO transacao (jogador_id, tipo, valor, descricao) VALUES (:id, 'admin_criar_item', 0, :desc)"),
        {"id": jogador_id, "desc": f"Criou item {novo_item.nome}"}
    )
    db.commit()
    return dict(novo_item._mapping)

@router.get("/itens")
def listar_loja(db: Session = Depends(get_db)):
    """UC08: Visualizar Catálogo da Loja"""
    query = text("SELECT * FROM item WHERE ativo = TRUE ORDER BY preco ASC")
    itens = db.execute(query).fetchall()
    return [dict(i._mapping) for i in itens]

@router.put("/itens/{item_id}")
def atualizar_item(item_id: int, item: schemas.ItemUpdate, jogador_id: int, db: Session = Depends(get_db)):
    """Atualiza dados de um item (Apenas Admin)"""

    jogador = db.execute(text("SELECT is_admin FROM jogador WHERE id = :id"), {"id": jogador_id}).fetchone()
    if not jogador or not jogador.is_admin:
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas o Professor/Admin pode editar itens.")

    if item.nome is not None:
        item.nome = item.nome.strip()
        if not item.nome:
            raise HTTPException(status_code=400, detail="Nome do item nao pode ser vazio.")

    if item.descricao is not None:
        item.descricao = item.descricao.strip()

    if item.preco is not None and item.preco <= 0:
        raise HTTPException(status_code=400, detail="Preco deve ser maior que zero.")

    if item.multiplicador is not None and item.multiplicador <= 0:
        raise HTTPException(status_code=400, detail="Multiplicador deve ser maior que zero.")

    if item.tipo is not None:
        item.tipo = item.tipo.strip()
        if not item.tipo:
            raise HTTPException(status_code=400, detail="Tipo do item nao pode ser vazio.")

    if item.raridade is not None:
        item.raridade = item.raridade.strip()
        if not item.raridade:
            raise HTTPException(status_code=400, detail="Raridade do item nao pode ser vazia.")

    tem_alteracao = any(
        campo is not None
        for campo in [
            item.nome,
            item.descricao,
            item.preco,
            item.multiplicador,
            item.tipo,
            item.raridade,
            item.vendivel
        ]
    )
    if not tem_alteracao:
        raise HTTPException(status_code=400, detail="Nenhuma alteracao enviada.")

    query = text("""
        UPDATE item
        SET nome = COALESCE(:nome, nome),
            descricao = COALESCE(:descricao, descricao),
            preco = COALESCE(:preco, preco),
            multiplicador = COALESCE(:multiplicador, multiplicador),
            tipo = COALESCE(:tipo, tipo),
            raridade = COALESCE(:raridade, raridade),
            vendivel = COALESCE(:vendivel, vendivel)
        WHERE id = :id AND ativo = TRUE
        RETURNING id, nome, descricao, preco, multiplicador, tipo, raridade, vendivel
    """)

    resultado = db.execute(
        query,
        {
            "id": item_id,
            "nome": item.nome,
            "descricao": item.descricao,
            "preco": item.preco,
            "multiplicador": item.multiplicador,
            "tipo": item.tipo,
            "raridade": item.raridade,
            "vendivel": item.vendivel
        }
    ).fetchone()

    if not resultado:
        raise HTTPException(status_code=404, detail="Item nao encontrado.")

    db.execute(
        text("INSERT INTO transacao (jogador_id, tipo, valor, descricao) VALUES (:id, 'admin_editar_item', 0, :desc)"),
        {"id": jogador_id, "desc": f"Editou item {resultado.nome}"}
    )
    db.commit()
    return dict(resultado._mapping)

@router.put("/itens/{item_id}/preco")
def alterar_preco(item_id: int, novo_preco: float, jogador_id: int, db: Session = Depends(get_db)):
    """UC09: Alterar Preço de um Item (Apenas Admin)"""
    
    # 1. Verifica se quem está chamando a rota é realmente um admin
    jogador = db.execute(text("SELECT is_admin FROM jogador WHERE id = :id"), {"id": jogador_id}).fetchone()
    
    if not jogador or not jogador.is_admin:
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas o Professor/Admin pode alterar os preços da loja.")

    # 2. Valida o preço antes de ir para o banco
    if novo_preco <= 0:
        raise HTTPException(status_code=400, detail="Preço deve ser maior que zero.")
        
    # 3. Faz a atualização se todas as verificações passarem
    query = text("UPDATE item SET preco = :preco WHERE id = :id RETURNING id, nome, preco")
    resultado = db.execute(query, {"preco": novo_preco, "id": item_id}).fetchone()
    db.commit()
    
    if not resultado:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
        
    return dict(resultado._mapping)

@router.delete("/itens/{item_id}")
def deletar_item(item_id: int, jogador_id: int, db: Session = Depends(get_db)):
    """Remove item da loja (Apenas Admin)"""

    jogador = db.execute(text("SELECT is_admin FROM jogador WHERE id = :id"), {"id": jogador_id}).fetchone()
    if not jogador or not jogador.is_admin:
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas o Professor/Admin pode deletar itens.")

    db.execute(
        text("DELETE FROM inventario WHERE item_id = :id"),
        {"id": item_id}
    )

    resultado = db.execute(
        text("UPDATE item SET ativo = FALSE WHERE id = :id AND ativo = TRUE RETURNING id, nome"),
        {"id": item_id}
    ).fetchone()

    if not resultado:
        raise HTTPException(status_code=404, detail="Item nao encontrado.")

    db.execute(
        text("INSERT INTO transacao (jogador_id, tipo, valor, descricao) VALUES (:id, 'admin_deletar_item', 0, :desc)"),
        {"id": jogador_id, "desc": f"Deletou item {resultado.nome}"}
    )
    db.commit()

    return {"mensagem": f"Item {resultado.nome} deletado com sucesso!"}