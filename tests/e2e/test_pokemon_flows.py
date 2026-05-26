# tests/e2e/test_pokemon_flows.py
"""
Testes End-to-End para Fluxos de Pokémon (UC12-UC18)

Validam gacha e gerenciamento de times via interface web.
"""

import os
import pytest
from playwright.sync_api import Page

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

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
        
        # Validar página carregou
        assert page.locator("body").is_visible()

    @pytest.mark.e2e
    def test_fluxo_criar_time(self, browser_page: Page):
        """E2E-UC15-001: Usuário cria novo time"""
        page = browser_page
        page.set_default_timeout(10000)
        
        # Login
        page.goto(f"{BASE_URL}/index.html")
        page.get_by_role("button", name="Login").click()
        page.get_by_placeholder("E-mail").fill("admin@test.com")
        page.get_by_placeholder("Senha").fill("admin123")
        page.get_by_role("button", name="Entrar").click()
        
        # Navegar para times
        page.get_by_role("link", name="Pokémon").click()
        page.wait_for_timeout(500)
        
        # Criar novo time
        page.get_by_role("button", name="Novo Time").click()
        page.wait_for_timeout(500)
        page.get_by_placeholder("Nome").fill("Time Competição")
        page.get_by_role("button", name="Criar").click()
        page.wait_for_timeout(500)

    @pytest.mark.e2e
    def test_fluxo_visualizar_time(self, browser_page: Page):
        """E2E-UC13-001: Usuário visualiza time com pokémons"""
        page = browser_page
        page.set_default_timeout(10000)
        
        # Navegar para página de pokémon
        page.goto(f"{BASE_URL}/pokemon.html")
        
        # Validar página carregou
        assert page.locator("body").is_visible()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
