from fastapi import FastAPI
from app.routers import users, shop, game, inventory, pokemon

app = FastAPI(title="API Isaac Clicker")

app.include_router(users.router)
app.include_router(shop.router)
app.include_router(game.router)
app.include_router(inventory.router)
app.include_router(pokemon.router)

@app.get("/")
def root():
    return {"mensagem": "Servidor do Isaac Clicker está online!"}