import pytest
import re
import time
from playwright.sync_api import Page, expect

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

@pytest.fixture(autouse=True)
def screenshot_on_failure(page: Page, request):
    # Salva evidência visual automaticamente apenas se o teste falhar
    yield
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        page.screenshot(path=f"screenshots/{request.node.name}.png")

def test_fluxo_completo_cadastro_login_jogo(page: Page):
    page.goto("http://127.0.0.1:5500/professor-simulator-clicker/front-end/index.html")

    # E-mail único usando timestamp para evitar conflitos no banco ao rodar o teste várias vezes
    email_teste = f"treinador_{int(time.time())}@pokemon.com"

    page.get_by_placeholder("Nome (somente para cadastro)").fill("Ash Ketchum")
    page.get_by_placeholder("E-mail (ex: aluno@ufpa.br)").fill(email_teste)
    page.get_by_placeholder("Senha").fill("senha123")
    
    page.get_by_role("button", name="Criar Conta").click()

    mensagem_alerta = page.locator("#mensagem")
    expect(mensagem_alerta).to_have_text("Cadastro realizado! Agora voce pode entrar.")

    # Apenas a senha precisa ser redigitada, pois o e-mail não é limpo da tela após o cadastro
    page.get_by_placeholder("Senha").fill("senha123")
    page.get_by_role("button", name="Entrar").click()

    expect(page).to_have_url(re.compile(r".*/game\.html"))

    saldo_element = page.locator("#saldo-display")
    saldo_texto_antes = saldo_element.inner_text()
    
    page.get_by_role("button", name="DAR AULA!").click()

    # O Playwright faz auto-wait natural aguardando a alteração no DOM antes de afirmar o teste
    expect(saldo_element).not_to_have_text(saldo_texto_antes)