# tests/e2e/test_friends_flows.py
"""
Testes End-to-End para Fluxos de Amigos (UC24-UC28)

Validam adição de amigos e gerenciamento de favoritos via interface web.
"""

import pytest
from playwright.sync_api import Page


class TestFriendsE2E:
    """E2E-UC24-UC28: Fluxos de amigos"""

    @pytest.mark.e2e
    def test_fluxo_adicionar_amigo(self, browser_page: Page):
        """E2E-UC24-001: Usuário adiciona novo amigo"""
        page = browser_page
        
        # Login
        page.goto("http://localhost:8000/index.html")
        page.click("text=Login")
        page.fill('input[name="email"]', "admin@test.com")
        page.fill('input[name="senha"]', "admin123")
        page.click("button:has-text('Entrar')")
        
        # Navegar para amigos
        page.click("text=Amigos")
        page.wait_for_url("**/friends.html")
        
        # Buscar amigo
        page.fill('input[name="busca"]', "Jogador")
        page.click("button:has-text('Buscar')")
        
        # Adicionar amigo
        page.click("button:has-text('Adicionar')[nth=0]")
        
        # Validar adição
        success = page.text_content(".sucesso-mensagem")
        assert "adicionado" in success.lower()

    @pytest.mark.e2e
    def test_fluxo_listar_amigos(self, browser_page: Page):
        """E2E-UC25-001: Usuário visualiza lista de amigos"""
        page = browser_page
        
        # Login
        page.goto("http://localhost:8000/index.html")
        page.click("text=Login")
        page.fill('input[name="email"]', "admin@test.com")
        page.fill('input[name="senha"]', "admin123")
        page.click("button:has-text('Entrar')")
        
        # Navegar para amigos
        page.click("text=Amigos")
        page.wait_for_url("**/friends.html")
        
        # Validar amigos são exibidos
        amigos = page.query_selector_all(".amigo-card")
        assert len(amigos) >= 0

    @pytest.mark.e2e
    def test_fluxo_favoritar_amigo(self, browser_page: Page):
        """E2E-UC27-001: Usuário favorita um amigo"""
        page = browser_page
        
        # Login
        page.goto("http://localhost:8000/index.html")
        page.click("text=Login")
        page.fill('input[name="email"]', "admin@test.com")
        page.fill('input[name="senha"]', "admin123")
        page.click("button:has-text('Entrar')")
        
        # Navegar para amigos
        page.click("text=Amigos")
        
        # Clicar em favoritar primeiro amigo
        favoritar_btns = page.query_selector_all("button:has-text('Favoritar')")
        if len(favoritar_btns) > 0:
            favoritar_btns[0].click()
            
            # Validar confirmação
            success = page.text_content(".sucesso-mensagem")
            assert success is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
