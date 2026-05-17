from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/jogo", tags=["Economia e Regras de Negócio"])

@router.post("/{jogador_id}/dar-aula")
def dar_aula(jogador_id: int, db: Session = Depends(get_db)):
    """UC04: Clicar em 'Dar Aula' (Calcula ganho com base no inventário)"""
    
    # 1. Verifica se o jogador existe
    jogador = db.execute(text("SELECT id, saldo FROM jogador WHERE id = :id"), {"id": jogador_id}).fetchone()
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")

    # 2. Calcula o multiplicador total baseado nos itens ativos no inventário
    query_mult = text("""
        SELECT COALESCE(SUM(i.multiplicador), 0) AS total_mult
        FROM inventario inv
        JOIN item i ON inv.item_id = i.id
        WHERE inv.jogador_id = :id AND inv.ativo = TRUE
    """)
    multiplicador_itens = db.execute(query_mult, {"id": jogador_id}).scalar()
    
    # Ganho base é 10. Somamos o multiplicador dos itens.
    ganho_total = 10 + float(multiplicador_itens)

    # 3. Atualiza o saldo e insere a transação (usando a mesma transação do banco)
    db.execute(text("UPDATE jogador SET saldo = saldo + :ganho WHERE id = :id"), 
               {"ganho": ganho_total, "id": jogador_id})
               
    db.execute(text("""
        INSERT INTO transacao (jogador_id, tipo, valor, descricao) 
        VALUES (:id, 'ganho_aula', :ganho, 'Ganho por dar aula')
    """), {"id": jogador_id, "ganho": ganho_total})
    
    db.commit()
    return {"mensagem": "Aula dada com sucesso!", "ganho": ganho_total, "novo_saldo": float(jogador.saldo) + ganho_total}

@router.delete("/{jogador_id}/reset")
def resetar_progresso(jogador_id: int, db: Session = Depends(get_db)):
    """UC06: Resetar Progresso (Zero saldo e limpa inventário/time)"""
    # Como as tabelas inventario e pokemon_time tem ON DELETE CASCADE, 
    # deletaríamos o user, mas o escopo é só resetar o progresso.
    db.execute(text("UPDATE jogador SET saldo = 0 WHERE id = :id"), {"id": jogador_id})
    db.execute(text("DELETE FROM inventario WHERE jogador_id = :id"), {"id": jogador_id})
    db.execute(text("DELETE FROM pokemon_time WHERE jogador_id = :id"), {"id": jogador_id})
    db.execute(text("INSERT INTO transacao (jogador_id, tipo, valor, descricao) VALUES (:id, 'reset', 0, 'Progresso zerado')"), {"id": jogador_id})
    db.commit()
    return {"mensagem": "Progresso do jogo foi resetado."}