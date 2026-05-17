from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/inventario", tags=["Inventário do Jogador"])

@router.post("/comprar/{jogador_id}/{item_id}")
def comprar_item(jogador_id: int, item_id: int, db: Session = Depends(get_db)):
    """UC10: Comprar Item da Loja"""
    
    jogador = db.execute(text("SELECT saldo FROM jogador WHERE id = :id"), {"id": jogador_id}).fetchone()
    item = db.execute(text("SELECT preco, nome FROM item WHERE id = :id AND ativo = TRUE"), {"id": item_id}).fetchone()

    if not jogador or not item:
        raise HTTPException(status_code=404, detail="Jogador ou Item não encontrado.")
    if jogador.saldo < item.preco:
        raise HTTPException(status_code=400, detail="Saldo insuficiente.")

    # Deduz saldo, insere no inventário e loga transação
    try:
        db.execute(text("UPDATE jogador SET saldo = saldo - :preco WHERE id = :id"), {"preco": item.preco, "id": jogador_id})
        db.execute(text("INSERT INTO inventario (jogador_id, item_id) VALUES (:j_id, :i_id)"), {"j_id": jogador_id, "i_id": item_id})
        db.execute(text("INSERT INTO transacao (jogador_id, tipo, valor, descricao) VALUES (:id, 'compra_item', :valor, :desc)"), 
                   {"id": jogador_id, "valor": -item.preco, "desc": f"Comprou {item.nome}"})
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Você já possui este item ou ocorreu um erro.")

    return {"mensagem": f"{item.nome} comprado com sucesso!"}

@router.get("/{jogador_id}")
def listar_inventario(jogador_id: int, db: Session = Depends(get_db)):
    """UC11: Listar Itens Adquiridos"""
    query = text("""
        SELECT inv.id as inventario_id, i.nome, i.multiplicador, inv.data_compra 
        FROM inventario inv
        JOIN item i ON inv.item_id = i.id
        WHERE inv.jogador_id = :id AND inv.ativo = TRUE
    """)
    itens = db.execute(query, {"id": jogador_id}).fetchall()
    return [dict(i._mapping) for i in itens]