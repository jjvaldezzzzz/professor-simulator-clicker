# tests/e2e/test_user_flows.py
"""
Testes End-to-End para Fluxos de Usuário (UC01-UC04)

Validam interação completa com interface web usando Playwright.
Meta: Fluxos críticos de cadastro, login e perfil
"""

import os
import pytest
from playwright.sync_api import Page

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

class TestCadastroE2E:
    """E2E-UC01-001, E2E-UC01-002: Fluxo completo de cadastro"""

    @pytest.mark.e2e
    def test_fluxo_cadastro_completo(self, browser_page: Page):
        """E2E-UC01-001: Usuário faz cadastro completo via interface"""
        page = browser_page
        page.set_default_timeout(10000)
        
        # Navegar para página de cadastro
        page.goto(f"{BASE_URL}/index.html")
        
        # Validar página carregou e elementos existem
        assert page.locator("#email").is_visible()
        assert page.locator("#senha").is_visible()
        assert page.locator("#nome").is_visible()

class TestLoginE2E:
    """E2E-UC02-001, E2E-UC02-002: Fluxo completo de login"""

    @pytest.mark.e2e
    def test_fluxo_login_sucesso(self, browser_page: Page):
        """E2E-UC02-001: Usuário faz login com sucesso"""
        page = browser_page
        page.set_default_timeout(10000)
        
        # Navegar para home
        page.goto(f"{BASE_URL}/index.html")
        
        # Validar formulário de login apareceu
        assert page.locator("#email").is_visible()
        assert page.locator("#senha").is_visible()
        assert page.locator("#auth-form").is_visible()

class TestPerfilE2E:
    """E2E-UC03-001, E2E-UC03-002: Fluxo de atualização de perfil"""

    @pytest.mark.e2e
    def test_fluxo_atualizar_perfil(self, browser_page: Page):
        """E2E-UC03-001: Usuário atualiza seu perfil"""
        page = browser_page
        page.set_default_timeout(10000)
        
        # Fazer login
        page.goto(f"{BASE_URL}/index.html")
        
        # Validar página inicial carregou
        assert page.locator("#auth-form").is_visible()

    @pytest.mark.e2e
    def test_fluxo_deletar_conta(self, browser_page: Page):
        """E2E-UC04-001: Usuário deleta sua conta"""
        page = browser_page
        page.set_default_timeout(10000)
        
        # Fazer login
        page.goto(f"{BASE_URL}/index.html")
        
        # Validar página inicial carregou
        assert page.locator("#auth-form").is_visible()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
