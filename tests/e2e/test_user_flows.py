# tests/e2e/test_user_flows.py
"""
Testes End-to-End para Fluxos de Usuário (UC01-UC04)

Validam interação completa com interface web usando Playwright.
Meta: Fluxos críticos de cadastro, login e perfil
"""

import pytest
from playwright.async_api import async_playwright, Page


@pytest.fixture
async def browser_page():
    """Fixture para instância do Playwright"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        yield page
        await browser.close()


class TestCadastroE2E:
    """E2E-UC01-001, E2E-UC01-002: Fluxo completo de cadastro"""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_fluxo_cadastro_completo(self, browser_page: Page):
        """E2E-UC01-001: Usuário faz cadastro completo via interface"""
        page = browser_page
        
        # Navegar para página de cadastro
        await page.goto("http://localhost:8000/index.html")
        
        # Clicar em botão de cadastro
        await page.click("text=Cadastro")
        
        # Preencher formulário
        await page.fill('input[name="nome"]', "João Silva")
        await page.fill('input[name="email"]', "joao.silva@test.com")
        await page.fill('input[name="senha"]', "senha123")
        await page.fill('input[name="confirmar_senha"]', "senha123")
        
        # Submeter
        await page.click("button:has-text('Cadastrar')")
        
        # Validar redirecionamento
        await page.wait_for_url("**/profile.html")
        assert page.url.endswith("profile.html")
        
        # Validar dados exibidos
        nome_exibido = await page.text_content(".nome-jogador")
        assert "João Silva" in nome_exibido

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_fluxo_cadastro_email_duplicado(self, browser_page: Page):
        """E2E-UC01-002: Sistema rejeita email duplicado"""
        page = browser_page
        
        # Navegar para cadastro
        await page.goto("http://localhost:8000/index.html")
        await page.click("text=Cadastro")
        
        # Tentar cadastrar com email já existente
        await page.fill('input[name="nome"]', "Outro Jogador")
        await page.fill('input[name="email"]', "admin@test.com")  # Email já registrado
        await page.fill('input[name="senha"]', "senha123")
        await page.fill('input[name="confirmar_senha"]', "senha123")
        
        await page.click("button:has-text('Cadastrar')")
        
        # Validar mensagem de erro
        error_msg = await page.text_content(".erro-mensagem")
        assert "Email já cadastrado" in error_msg or "duplicado" in error_msg


class TestLoginE2E:
    """E2E-UC02-001, E2E-UC02-002: Fluxo completo de login"""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_fluxo_login_sucesso(self, browser_page: Page):
        """E2E-UC02-001: Usuário faz login com sucesso"""
        page = browser_page
        
        # Navegar para home
        await page.goto("http://localhost:8000/index.html")
        
        # Clicar em login
        await page.click("text=Login")
        
        # Preencher credenciais
        await page.fill('input[name="email"]', "admin@test.com")
        await page.fill('input[name="senha"]', "admin123")
        
        # Submeter
        await page.click("button:has-text('Entrar')")
        
        # Validar redirecionamento para dashboard
        await page.wait_for_url("**/game.html")
        assert page.url.endswith("game.html")
        
        # Validar token salvo no localStorage
        token = await page.evaluate("() => localStorage.getItem('token')")
        assert token is not None

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_fluxo_login_credenciais_invalidas(self, browser_page: Page):
        """E2E-UC02-002: Sistema rejeita credenciais inválidas"""
        page = browser_page
        
        # Navegar para login
        await page.goto("http://localhost:8000/index.html")
        await page.click("text=Login")
        
        # Tentar login com senha errada
        await page.fill('input[name="email"]', "admin@test.com")
        await page.fill('input[name="senha"]', "senhaerrada")
        
        await page.click("button:has-text('Entrar')")
        
        # Validar erro
        error = await page.text_content(".erro-mensagem")
        assert "Credenciais inválidas" in error or "incorretas" in error


class TestPerfilE2E:
    """E2E-UC03-001, E2E-UC03-002: Fluxo de atualização de perfil"""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_fluxo_atualizar_perfil(self, browser_page: Page):
        """E2E-UC03-001: Usuário atualiza seu perfil"""
        page = browser_page
        
        # Fazer login
        await page.goto("http://localhost:8000/index.html")
        await page.click("text=Login")
        await page.fill('input[name="email"]', "admin@test.com")
        await page.fill('input[name="senha"]', "admin123")
        await page.click("button:has-text('Entrar')")
        
        # Navegar para perfil
        await page.click("text=Perfil")
        
        # Atualizar nome de exibição
        await page.fill('input[name="nome_exibicao"]', "Mestre Pokémon")
        await page.click("button:has-text('Salvar')")
        
        # Validar confirmação
        success_msg = await page.text_content(".sucesso-mensagem")
        assert "atualizado" in success_msg.lower()
        
        # Validar novo nome exibido
        nome_exibido = await page.text_content(".nome-jogador")
        assert "Mestre Pokémon" in nome_exibido

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_fluxo_deletar_conta(self, browser_page: Page):
        """E2E-UC04-001: Usuário deleta sua conta"""
        page = browser_page
        
        # Fazer login
        await page.goto("http://localhost:8000/index.html")
        await page.click("text=Login")
        await page.fill('input[name="email"]', "teste_delete@test.com")
        await page.fill('input[name="senha"]', "senha123")
        await page.click("button:has-text('Entrar')")
        
        # Ir para configurações
        await page.click("text=Configurações")
        
        # Clicar em deletar conta
        await page.click("button:has-text('Deletar Conta')")
        
        # Confirmar deleção
        await page.click("button:has-text('Confirmar Deleção')")
        
        # Validar redirecionamento para login
        await page.wait_for_url("**/index.html")
        
        # Validar token removido
        token = await page.evaluate("() => localStorage.getItem('token')")
        assert token is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
