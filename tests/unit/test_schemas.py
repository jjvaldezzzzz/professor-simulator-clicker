import pytest
from pydantic import ValidationError
from app.schemas import JogadorCreate, ItemCreate

def test_jogador_create_aceita_dados_validos():
    # Envia apenas os campos mapeados no modelo JogadorCreate (cadastro inicial)
    dados_validos = {"email": "treinador@pokemon.com", "senha": "senha123", "nome": "Ash Ketchum"}
    jogador = JogadorCreate(**dados_validos)
    
    assert jogador.email == "treinador@pokemon.com"
    assert jogador.nome == "Ash Ketchum"

def test_jogador_create_rejeita_email_invalido():
    # Valida se o Pydantic bloqueia e-mails mal formatados
    dados_invalidos = {"email": "email-invalido", "senha": "123", "nome": "Equipe Rocket"}
    with pytest.raises(ValidationError):
        JogadorCreate(**dados_invalidos)

def test_jogador_create_rejeita_nome_vazio():
    # Valida a regra de negócio do @field_validator("nome") que impede nomes vazios
    dados_invalidos = {"email": "treinador@pokemon.com", "senha": "123", "nome": "   "}
    with pytest.raises(ValidationError, match="Nome e obrigatorio"):
        JogadorCreate(**dados_invalidos)

def test_item_create_aplica_valores_padrao():
    item = ItemCreate(nome="Pocao", preco=100.0, tipo="consumivel")
    assert item.raridade == "comum"
    assert item.vendivel is True