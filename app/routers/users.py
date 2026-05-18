from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas

router = APIRouter(prefix="/jogadores", tags=["Gestão de Jogadores"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def cadastrar_jogador(jogador: schemas.JogadorCreate, db: Session = Depends(get_db)):
    """UC01: Cadastrar Novo Jogador"""
    
    # 1. Verifica se o email já existe
    query_check = text("SELECT id FROM jogador WHERE email = :email")
    resultado = db.execute(query_check, {"email": jogador.email}).fetchone()
    
    if resultado:
        raise HTTPException(status_code=400, detail="Email já cadastrado.")

    # 2. Insere no banco (Nota: Em produção, usaríamos uma lib como bcrypt para a senha)
    query_insert = text("""
        INSERT INTO jogador (nome, email, senha_hash) 
        VALUES (:nome, :email, :senha) 
        RETURNING id, nome, nome_exibicao, email, saldo
    """)
    
    novo_jogador = db.execute(query_insert, {
        "nome": jogador.nome,
        "email": jogador.email,
        "senha": jogador.senha # Simulando o hash para o trabalho
    }).fetchone()
    
    db.commit()
    
    # Retorna os dados mapeados para um dicionário
    return dict(novo_jogador._mapping)

@router.post("/login")
def autenticar_jogador(credenciais: schemas.JogadorLogin, db: Session = Depends(get_db)):
    """UC02: Autenticar Jogador (Incluindo verificação de Admin)"""
    
    # 1. Adicionamos 'is_admin' no SELECT para capturar o privilégio do usuário
    query = text("SELECT id, senha_hash, is_admin FROM jogador WHERE email = :email AND ativo = TRUE")
    jogador = db.execute(query, {"email": credenciais.email}).fetchone()

    # Validação de credenciais
    if not jogador or jogador.senha_hash != credenciais.senha:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    # Atualiza o último login
    db.execute(text("UPDATE jogador SET ultimo_login = CURRENT_TIMESTAMP WHERE id = :id"), {"id": jogador.id})
    db.commit()

    # 2. Retornamos o 'is_admin' junto com os dados de sucesso do login
    return {
        "mensagem": "Login bem-sucedido", 
        "jogador_id": jogador.id, 
        "is_admin": jogador.is_admin,  # True para o admin, False para jogadores comuns
        "token": "token-simulado-123"
    }

@router.get("/{jogador_id}")
def obter_jogador(jogador_id: int, db: Session = Depends(get_db)):
    """Retorna dados basicos do jogador para o front-end"""

    query = text("""
        SELECT id, nome, nome_exibicao, email, saldo
        FROM jogador
        WHERE id = :id AND ativo = TRUE
    """)
    jogador = db.execute(query, {"id": jogador_id}).fetchone()

    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador nao encontrado.")

    return dict(jogador._mapping)

@router.put("/{jogador_id}/perfil")
def atualizar_perfil(jogador_id: int, perfil: schemas.JogadorUpdate, db: Session = Depends(get_db)):
    """UC03: Atualizar Perfil (Nome de Exibição)"""
    
    query = text("""
        UPDATE jogador 
        SET nome_exibicao = :nome_exibicao 
        WHERE id = :id AND ativo = TRUE
        RETURNING id, nome_exibicao
    """)
    
    resultado = db.execute(query, {"nome_exibicao": perfil.nome_exibicao, "id": jogador_id}).fetchone()
    db.commit()

    if not resultado:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")

    return {"mensagem": "Perfil atualizado com sucesso!", "novo_nome_exibicao": resultado.nome_exibicao}