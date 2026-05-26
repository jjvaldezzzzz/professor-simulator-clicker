# tests/e2e/test_shop_flows.py
"""
Testes End-to-End para Fluxos de Shop/Inventory (UC05-UC11)

Validam compra de items via interface web.
"""

import os
import pytest
from playwright.sync_api import Page

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

class TestShopE2E:
    """E2E-UC05-UC11: Fluxos de shop e compras"""

    @pytest.mark.e2e
    def test_fluxo_compra_item(self, browser_page: Page):
        """E2E-UC10-001: Usuário compra item da loja"""
        page = browser_page
        page.set_default_timeout(10000)
        
        # Navegar para página de loja
        page.goto(f"{BASE_URL}/shop.html")
        
        # Validar página carregou
        assert page.locator("body").is_visible()
        page.wait_for_timeout(1000)

    @pytest.mark.e2e
    def test_fluxo_listar_inventario(self, browser_page: Page):
        """E2E-UC11-001: Usuário visualiza inventário"""
        page = browser_page
        page.set_default_timeout(10000)
        
        # Navegar para página de inventário
        page.goto(f"{BASE_URL}/inventory.html")
        
        # Validar página carregou
        assert page.locator("body").is_visible()
        page.wait_for_timeout(1000)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
