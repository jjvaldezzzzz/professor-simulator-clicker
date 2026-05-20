from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # ⬅️ Importação nova
from app.routers import users, shop, game, inventory, pokemon, tournament

app = FastAPI(title="API Isaac Clicker")

# ⬅️ Configuração do CORS (Libera o acesso do Front-end)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, colocaríamos a URL do front-end aqui
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(shop.router)
app.include_router(game.router)
app.include_router(inventory.router)
app.include_router(pokemon.router)
app.include_router(tournament.router)

@app.get("/")
def root():
    return {"mensagem": "Servidor do Isaac Clicker está online!"}