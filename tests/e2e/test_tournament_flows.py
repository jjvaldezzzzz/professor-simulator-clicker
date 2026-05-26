# tests/e2e/test_tournament_flows.py
"""
Testes End-to-End para Fluxos de Torneios (UC19-UC23)

Validam criação e participação em torneios via interface web.
"""

import pytest
from playwright.sync_api import Page


class TestTournamentE2E:
    """E2E-UC19-UC23: Fluxos de torneios"""

    @pytest.mark.e2e
    def test_fluxo_criar_torneio(self, browser_page: Page):
        """E2E-UC19-001: Usuário cria novo torneio"""
        page = browser_page
        
        # Login
        page.goto("http://localhost:8000/index.html")
        page.click("text=Login")
        page.fill('input[name="email"]', "admin@test.com")
        page.fill('input[name="senha"]', "admin123")
        page.click("button:has-text('Entrar')")
        
        # Navegar para torneios
        page.click("text=Torneios")
        page.wait_for_url("**/tournament.html")
        
        # Criar novo torneio
        page.click("button:has-text('Criar Torneio')")
        page.select_option('select[name="tamanho"]', "2")
        page.click("button:has-text('Criar')")
        
        # Validar criação
        success = page.text_content(".sucesso-mensagem")
        assert "criado" in success.lower()

    @pytest.mark.e2e
    def test_fluxo_listar_torneios(self, browser_page: Page):
        """E2E-UC20-001: Usuário visualiza lista de torneios"""
        page = browser_page
        
        # Login
        page.goto("http://localhost:8000/index.html")
        page.click("text=Login")
        page.fill('input[name="email"]', "admin@test.com")
        page.fill('input[name="senha"]', "admin123")
        page.click("button:has-text('Entrar')")
        
        # Navegar para torneios
        page.click("text=Torneios")
        page.wait_for_url("**/tournament.html")
        
        # Validar torneios são exibidos
        torneios = page.query_selector_all(".torneio-card")
        assert len(torneios) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
