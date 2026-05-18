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

    # 2. Se passou, cria o item normalmente
    query = text("""
        INSERT INTO item (nome, descricao, preco, multiplicador, tipo, raridade, vendivel) 
        VALUES (:nome, :descricao, :preco, :multiplicador, :tipo, :raridade, :vendivel)
        RETURNING id, nome, preco, multiplicador
    """)
    novo_item = db.execute(query, item.dict()).fetchone()
    db.commit()
    return dict(novo_item._mapping)

@router.get("/itens")
def listar_loja(db: Session = Depends(get_db)):
    """UC08: Visualizar Catálogo da Loja"""
    query = text("SELECT * FROM item WHERE ativo = TRUE ORDER BY preco ASC")
    itens = db.execute(query).fetchall()
    return [dict(i._mapping) for i in itens]

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