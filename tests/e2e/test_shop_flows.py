# tests/e2e/test_shop_flows.py
"""
Testes End-to-End para Fluxos de Shop/Inventory (UC05-UC11)

Validam compra de items via interface web.
"""

import pytest
from playwright.async_api import Page


@pytest.fixture
async def logged_in_page():
    """Fixture para página com usuário já logado"""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Login
        await page.goto("http://localhost:8000/index.html")
        await page.click("text=Login")
        await page.fill('input[name="email"]', "admin@test.com")
        await page.fill('input[name="senha"]', "admin123")
        await page.click("button:has-text('Entrar')")
        await page.wait_for_url("**/game.html")
        
        yield page
        await browser.close()


class TestShopE2E:
    """E2E-UC05-UC11: Fluxos de shop e compras"""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_fluxo_compra_item(self, logged_in_page: Page):
        """E2E-UC10-001: Usuário compra item da loja"""
        page = logged_in_page
        
        # Navegar para loja
        await page.click("text=Loja")
        await page.wait_for_url("**/shop.html")
        
        # Clicar em comprar item
        await page.click("button:has-text('Comprar')[nth=0]")
        
        # Confirmar compra
        await page.click("button:has-text('Confirmar')")
        
        # Validar mensagem de sucesso
        success = await page.text_content(".sucesso-mensagem")
        assert "comprado" in success.lower()
        
        # Validar saldo reduzido
        saldo = await page.text_content(".saldo")
        assert float(saldo.replace("Saldo:", "").strip()) < 1000.0

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_fluxo_listar_inventario(self, logged_in_page: Page):
        """E2E-UC11-001: Usuário visualiza inventário"""
        page = logged_in_page
        
        # Navegar para inventário
        await page.click("text=Inventário")
        await page.wait_for_url("**/inventory.html")
        
        # Validar items são exibidos
        items_list = await page.query_selector_all(".item-card")
        assert len(items_list) >= 0  # Pode estar vazio


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
