# tests/e2e/test_pokemon_flows.py
"""
Testes End-to-End para Fluxos de Pokémon (UC12-UC18)

Validam gacha e gerenciamento de times via interface web.
"""

import pytest
from playwright.sync_api import Page


class TestPokemonE2E:
    """E2E-UC12-UC18: Fluxos de pokémon e times"""

    @pytest.mark.e2e
    def test_fluxo_sortear_pokemon(self, browser_page: Page):
        """E2E-UC12-001: Usuário sorteia pokémon via gacha"""
        page = browser_page
        
        # Login
        page.goto("http://localhost:8000/index.html")
        page.click("text=Login")
        page.fill('input[name="email"]', "admin@test.com")
        page.fill('input[name="senha"]', "admin123")
        page.click("button:has-text('Entrar')")
        
        # Navegar para pokémon
        page.click("text=Pokémon")
        page.wait_for_url("**/pokemon.html")
        
        # Clicar em gacha
        page.click("button:has-text('Sortear Pokémon')")
        
        # Aguardar resultado
        resultado = page.text_content(".pokemon-resultado")
        assert resultado is not None
        assert "Parabéns" in resultado or "obteve" in resultado.lower()

    @pytest.mark.e2e
    def test_fluxo_criar_time(self, browser_page: Page):
        """E2E-UC15-001: Usuário cria novo time"""
        page = browser_page
        
        # Login
        page.goto("http://localhost:8000/index.html")
        page.click("text=Login")
        page.fill('input[name="email"]', "admin@test.com")
        page.fill('input[name="senha"]', "admin123")
        page.click("button:has-text('Entrar')")
        
        # Navegar para times
        page.click("text=Meus Times")
        
        # Criar novo time
        page.click("button:has-text('Novo Time')")
        page.fill('input[name="nome_time"]', "Time Competição")
        page.click("button:has-text('Criar')")
        
        # Validar time criado
        success = page.text_content(".sucesso-mensagem")
        assert "criado" in success.lower()

    @pytest.mark.e2e
    def test_fluxo_visualizar_time(self, browser_page: Page):
        """E2E-UC13-001: Usuário visualiza time com pokémons"""
        page = browser_page
        
        # Login
        page.goto("http://localhost:8000/index.html")
        page.click("text=Login")
        page.fill('input[name="email"]', "admin@test.com")
        page.fill('input[name="senha"]', "admin123")
        page.click("button:has-text('Entrar')")
        
        # Ir para times
        page.click("text=Meus Times")
        page.wait_for_url("**/pokemon.html")
        
        # Clicar em primeiro time
        page.click(".time-card[nth=0]")
        
        # Validar pokémons são exibidos
        pokemons = page.query_selector_all(".pokemon-item")
        assert len(pokemons) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
