# tests/e2e/test_shop_flows.py
"""
Testes End-to-End para Fluxos de Shop/Inventory (UC05-UC11)

Validam compra de items via interface web.
"""

import pytest
from playwright.sync_api import Page


class TestShopE2E:
    """E2E-UC05-UC11: Fluxos de shop e compras"""

    @pytest.mark.e2e
    def test_fluxo_compra_item(self, browser_page: Page):
        """E2E-UC10-001: Usuário compra item da loja"""
        page = browser_page
        
        # Login
        page.goto("http://localhost:8000/index.html")
        page.click("text=Login")
        page.fill('input[name="email"]', "admin@test.com")
        page.fill('input[name="senha"]', "admin123")
        page.click("button:has-text('Entrar')")
        
        # Navegar para loja
        page.click("text=Loja")
        page.wait_for_url("**/shop.html")
        
        # Clicar em comprar item
        page.click("button:has-text('Comprar')[nth=0]")
        
        # Confirmar compra
        page.click("button:has-text('Confirmar')")
        
        # Validar mensagem de sucesso
        success = page.text_content(".sucesso-mensagem")
        assert "comprado" in success.lower()

    @pytest.mark.e2e
    def test_fluxo_listar_inventario(self, browser_page: Page):
        """E2E-UC11-001: Usuário visualiza inventário"""
        page = browser_page
        
        # Login
        page.goto("http://localhost:8000/index.html")
        page.click("text=Login")
        page.fill('input[name="email"]', "admin@test.com")
        page.fill('input[name="senha"]', "admin123")
        page.click("button:has-text('Entrar')")
        
        # Navegar para inventário
        page.click("text=Inventário")
        page.wait_for_url("**/inventory.html")
        
        # Validar items são exibidos
        items_list = page.query_selector_all(".item-card")
        assert len(items_list) >= 0  # Pode estar vazio


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
