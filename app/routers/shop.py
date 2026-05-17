from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas

router = APIRouter(prefix="/loja", tags=["Catálogo e Loja"])

@router.post("/itens", status_code=status.HTTP_201_CREATED)
def cadastrar_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """UC07: Cadastrar Novo Item na Loja (Admin)"""
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
def alterar_preco(item_id: int, novo_preco: float, db: Session = Depends(get_db)):
    """UC09: Alterar Preço de um Item"""
    if novo_preco <= 0:
        raise HTTPException(status_code=400, detail="Preço deve ser maior que zero.")
        
    query = text("UPDATE item SET preco = :preco WHERE id = :id RETURNING id, nome, preco")
    resultado = db.execute(query, {"preco": novo_preco, "id": item_id}).fetchone()
    db.commit()
    
    if not resultado:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    return dict(resultado._mapping)