from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# String de conexão com o PostgreSQL
# ATENÇÃO: Substitua "suasenha" pela senha do seu Postgres local e "isaac_db" pelo nome do seu banco.
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:suasenha@localhost:5433/isaac_db"

# O Engine é o motor que estabelece a conexão real
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# O SessionLocal cria sessões individuais para cada requisição, evitando travamentos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função geradora que o FastAPI usa para injetar o banco nas rotas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()