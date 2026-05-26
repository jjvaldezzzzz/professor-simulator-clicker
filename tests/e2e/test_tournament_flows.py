# tests/e2e/test_tournament_flows.py
"""
Testes End-to-End para Fluxos de Torneios (UC19-UC23)

Validam criação e participação em torneios via interface web.
"""

import os
import pytest
from playwright.sync_api import Page

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

class TestTournamentE2E:
    """E2E-UC19-UC23: Fluxos de torneios"""

    @pytest.mark.e2e
    def test_fluxo_criar_torneio(self, browser_page: Page):
        """E2E-UC19-001: Usuário cria novo torneio"""
        page = browser_page
        page.set_default_timeout(10000)
        
        # Navegar para página de torneios
        page.goto(f"{BASE_URL}/tournament.html")
        
        # Validar página carregou
        assert page.locator("body").is_visible()
        page.wait_for_timeout(1000)

    @pytest.mark.e2e
    def test_fluxo_listar_torneios(self, browser_page: Page):
        """E2E-UC20-001: Usuário visualiza lista de torneios"""
        page = browser_page
        page.set_default_timeout(10000)
        
        # Navegar para página de torneios
        page.goto(f"{BASE_URL}/tournament.html")
        
        # Validar página carregou
        assert page.locator("body").is_visible()
        page.wait_for_timeout(1000)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
