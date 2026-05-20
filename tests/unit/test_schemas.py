import pytest
from pydantic import ValidationError

from app.schemas import ItemCreate, JogadorCreate


def test_jogador_create_valido():
    jogador = JogadorCreate(nome="Ana", email="ana@example.com", senha="123")
    assert jogador.email == "ana@example.com"


def test_jogador_create_email_invalido():
    with pytest.raises(ValidationError):
        JogadorCreate(nome="Ana", email="ana", senha="123")


def test_jogador_create_nome_vazio():
    with pytest.raises(ValidationError):
        JogadorCreate(nome="   ", email="ana@example.com", senha="123")


def test_item_create_defaults():
    item = ItemCreate(
        nome="Caderno",
        descricao=None,
        preco=10.0,
        multiplicador=1.0,
        tipo="equipamento",
    )
    assert item.raridade == "comum"
    assert item.vendivel is True
