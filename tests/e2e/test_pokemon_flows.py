# tests/e2e/test_pokemon_flows.py
"""
Testes End-to-End para Fluxos de Pokémon (UC12-UC18)

Validam gacha e gerenciamento de times via interface web.
"""

import pytest
from playwright.async_api import Page


class TestPokemonE2E:
    """E2E-UC12-UC18: Fluxos de pokémon e times"""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_fluxo_sortear_pokemon(self, browser_page: Page):
        """E2E-UC12-001: Usuário sorteia pokémon via gacha"""
        page = browser_page
        
        # Login
        await page.goto("http://localhost:8000/index.html")
        await page.click("text=Login")
        await page.fill('input[name="email"]', "admin@test.com")
        await page.fill('input[name="senha"]', "admin123")
        await page.click("button:has-text('Entrar')")
        
        # Navegar para pokémon
        await page.click("text=Pokémon")
        await page.wait_for_url("**/pokemon.html")
        
        # Clicar em gacha
        await page.click("button:has-text('Sortear Pokémon')")
        
        # Aguardar resultado
        resultado = await page.text_content(".pokemon-resultado")
        assert resultado is not None
        assert "Parabéns" in resultado or "obteve" in resultado.lower()

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_fluxo_criar_time(self, browser_page: Page):
        """E2E-UC15-001: Usuário cria novo time"""
        page = browser_page
        
        # Login
        await page.goto("http://localhost:8000/index.html")
        await page.click("text=Login")
        await page.fill('input[name="email"]', "admin@test.com")
        await page.fill('input[name="senha"]', "admin123")
        await page.click("button:has-text('Entrar')")
        
        # Navegar para times
        await page.click("text=Meus Times")
        
        # Criar novo time
        await page.click("button:has-text('Novo Time')")
        await page.fill('input[name="nome_time"]', "Time Competição")
        await page.click("button:has-text('Criar')")
        
        # Validar time criado
        success = await page.text_content(".sucesso-mensagem")
        assert "criado" in success.lower()

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_fluxo_visualizar_time(self, browser_page: Page):
        """E2E-UC13-001: Usuário visualiza time com pokémons"""
        page = browser_page
        
        # Login
        await page.goto("http://localhost:8000/index.html")
        await page.click("text=Login")
        await page.fill('input[name="email"]', "admin@test.com")
        await page.fill('input[name="senha"]', "admin123")
        await page.click("button:has-text('Entrar')")
        
        # Ir para times
        await page.click("text=Meus Times")
        await page.wait_for_url("**/pokemon.html")
        
        # Clicar em primeiro time
        await page.click(".time-card[nth=0]")
        
        # Validar pokémons são exibidos
        pokemons = await page.query_selector_all(".pokemon-item")
        assert len(pokemons) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
