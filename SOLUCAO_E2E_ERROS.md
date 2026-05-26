# 🔧 Guia de Solução - Testes E2E com Erros

## 📊 Análise dos Problemas

Todos os 15 testes E2E falharam com **3 problemas principais**:

### ❌ Problema 1: `net::ERR_CONNECTION_REFUSED` 
**Erro:** O servidor FastAPI não está rodando na porta 8000
```
playwright._impl._errors.Error: Page.goto: net::ERR_CONNECTION_REFUSED 
at http://localhost:8000/index.html
```

### ❌ Problema 2: Falta fixture `browser_page`
**Erro:** Os testes usam `browser_page` mas não há fixture configurada
```python
def test_fluxo_adicionar_amigo(self, browser_page: Page):  # ← Fixture não existe!
    page = browser_page
```

### ❌ Problema 3: URLs inconsistentes
- Maioria dos testes: `http://localhost:8000/`
- test_ui_game.py: `http://127.0.0.1:5500/` (Live Server)

---

## ✅ Solução Passo a Passo

### **PASSO 1: Criar fixture browser_page no conftest.py**

O arquivo `tests/conftest.py` NÃO tem a fixture para Playwright. Precisamos adicionar:

```python
@pytest.fixture
def browser_page():
    """Fixture que fornece uma página Playwright para testes E2E"""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        yield page
        page.close()
        browser.close()
```

---

### **PASSO 2: Iniciar o servidor FastAPI antes dos testes**

**Opção A - Iniciar manualmente em outro terminal:**
```bash
# Terminal 1: Iniciar servidor
cd professor-simulator-clicker
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Opção B - Fixture que inicia servidor automaticamente:**
```python
@pytest.fixture(scope="session")
def fastapi_server():
    """Inicia o servidor FastAPI antes de rodar os testes E2E"""
    import subprocess
    import time
    
    # Inicia o servidor em background
    process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(3)  # Aguarda servidor iniciar
    yield
    process.terminate()
```

---

### **PASSO 3: Verificar e corrigir seletores HTML**

Os testes usam seletores como:
```python
page.click("text=Login")  # ← Pode não existir no HTML
```

**Verifique o HTML real:**
```bash
# Ver o arquivo HTML
cat front-end/index.html
```

**Seletores mais seguros:**
```python
# Em vez de:
page.click("text=Login")

# Use:
page.get_by_role("button", name="Entrar")  # Mais robusto
page.locator("button:has-text('Entrar')")   # Alternativa
page.get_by_placeholder("E-mail")  # Para inputs
```

---

### **PASSO 4: Adaptar URLs para ambiente de teste**

Os testes usam URLs hardcoded. Melhor usar variáveis:

```python
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def test_fluxo_login(browser_page):
    page = browser_page
    page.goto(f"{BASE_URL}/index.html")
```

---

## 🚀 Implementação Rápida (Recomendado)

### **1. Atualizar conftest.py:**
Adicione ao final do arquivo `tests/conftest.py`:

```python
# ============ FIXTURES PARA TESTES E2E ============

@pytest.fixture
def browser_page():
    """Fixture Playwright para testes E2E"""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        yield page
        
        page.close()
        context.close()
        browser.close()
```

### **2. Atualizar todas os testes E2E:**

Substituir URLs hardcoded por variável de ambiente:

```python
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

class TestFriendsE2E:
    @pytest.mark.e2e
    def test_fluxo_adicionar_amigo(self, browser_page):
        page = browser_page
        page.goto(f"{BASE_URL}/index.html")  # ← URL dinâmica
        # ... resto do teste
```

### **3. Iniciar servidor:**

```bash
# Terminal 1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 (após 3 segundos)
pytest tests/e2e -v
```

---

## ✨ Verificação de Seletores

**Para descobrir os seletores corretos:**

1. Abra o navegador manualmente:
```bash
# Terminal
cd front-end
python -m http.server 8000
```

2. Acesse: `http://localhost:8000/index.html`

3. Inspecione o HTML (F12) e identifique:
   - Nomes dos botões
   - IDs dos inputs
   - Classes CSS

4. Exemplo de seletores robustos:
```python
# Ruim ❌
page.click("text=Login")

# Bom ✅
page.get_by_role("button", name="Entrar")
page.get_by_placeholder("E-mail")
page.locator("#loginForm button")
page.get_by_label("Senha")
```

---

## 📋 Checklist de Correção

- [ ] Adicionar fixture `browser_page` ao `conftest.py`
- [ ] Iniciar servidor FastAPI em porta 8000
- [ ] Substituir URLs hardcoded por variável de ambiente
- [ ] Inspecionar HTML e corrigir seletores
- [ ] Rodar: `pytest tests/e2e -v`
- [ ] Verificar se testes passam

---

## 🎯 Próximos Passos

Após aplicar essas mudanças, os erros devem desaparecer. Se ainda tiver problemas:

1. **Erro de autenticação?** → Verify usuário/senha nos testes
2. **Seletor não encontrado?** → Use `page.pause()` para inspecionar
3. **Timeout?** → Aumentar timeout: `page.set_default_timeout(10000)`

---

## 📚 Referências

- [Playwright Python Docs](https://playwright.dev/python/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Playwright Locators](https://playwright.dev/python/docs/locators)
