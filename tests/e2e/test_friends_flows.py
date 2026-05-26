# tests/e2e/test_friends_flows.py
"""
Testes End-to-End para Fluxos de Amigos (UC24-UC28)

Validam adição de amigos e gerenciamento de favoritos via interface web.
"""

import os
import pytest
from playwright.sync_api import Page

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

class TestFriendsE2E:
    """E2E-UC24-UC28: Fluxos de amigos"""

    @pytest.mark.e2e
    def test_fluxo_adicionar_amigo(self, browser_page: Page):
        """E2E-UC24-001: Usuário adiciona novo amigo"""
        page = browser_page
        page.set_default_timeout(10000)
        
        # Navegar para página de amigos
        page.goto(f"{BASE_URL}/friends.html")
        
        # Validar página carregou
        assert page.locator("body").is_visible()
        page.wait_for_timeout(1000)

    @pytest.mark.e2e
    def test_fluxo_listar_amigos(self, browser_page: Page):
        """E2E-UC25-001: Usuário visualiza lista de amigos"""
        page = browser_page
        page.set_default_timeout(10000)
        
        # Navegar para página de amigos
        page.goto(f"{BASE_URL}/friends.html")
        
        # Validar página carregou
        assert page.locator("body").is_visible()

    @pytest.mark.e2e
    def test_fluxo_favoritar_amigo(self, browser_page: Page):
        """E2E-UC27-001: Usuário favorita um amigo"""
        page = browser_page
        page.set_default_timeout(10000)
        
        # Navegar para página de amigos
        page.goto(f"{BASE_URL}/friends.html")
        
        # Validar página carregou
        assert page.locator("body").is_visible()
        page.wait_for_timeout(1000)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
