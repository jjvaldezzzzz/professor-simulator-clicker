from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ==========================================
# SCHEMAS PARA A TABELA 'jogador'
# ==========================================
class JogadorCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str # No futuro, o back-end vai transformar isso em senha_hash

class JogadorLogin(BaseModel):
    email: EmailStr
    senha: str

class JogadorUpdate(BaseModel):
    nome_exibicao: str

class JogadorResponse(BaseModel):
    id: int
    nome: str
    nome_exibicao: str
    email: str
    saldo: float

    class Config:
        from_attributes = True

# ==========================================
# SCHEMAS PARA A TABELA 'item' (Loja)
# ==========================================
class ItemCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: float
    multiplicador: float = 1.00
    tipo: str
    raridade: str = "comum"
    vendivel: bool = True

class ItemResponse(ItemCreate):
    id: int
    ativo: bool
    
    class Config:
        from_attributes = True

# ==========================================
# SCHEMAS PARA A TABELA 'pokemon_time'
# ==========================================
class PokemonResponse(BaseModel):
    id: int
    pokemon_api_id: int
    nome_pokemon: str
    sprite_url: str
    apelido: Optional[str] = None

    class Config:
        from_attributes = True

# ==========================================
# SCHEMAS PARA A TABELA 'inventario'
# ==========================================
class InventarioResponse(BaseModel):
    id: int
    jogador_id: int
    item_id: int
    data_compra: datetime
    ativo: bool

    class Config:
        from_attributes = True

class InventarioDetalhadoResponse(BaseModel):
    inventario_id: int
    nome_item: str
    multiplicador: float
    data_compra: datetime

# ==========================================
# SCHEMAS PARA A TABELA 'transacao'
# ==========================================
class TransacaoResponse(BaseModel):
    id: int
    jogador_id: int
    tipo: str
    valor: float
    descricao: Optional[str] = None
    data_transacao: datetime

    class Config:
        from_attributes = True

# ==========================================
# SCHEMAS PARA A TABELA 'config_game'
# ==========================================
class ConfigGameResponse(BaseModel):
    config_key: str
    config_value: str

    class Config:
        from_attributes = True