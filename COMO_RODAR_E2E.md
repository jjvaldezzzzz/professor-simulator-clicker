# ✅ Solução Completa - Testes E2E (Passo a Passo)

## 🎯 Resumo Executivo

**Todos os 15 testes E2E falharam porque:**
1. ❌ Servidor FastAPI **não está rodando** na porta 8000
2. ❌ Seletores HTML **inadequados** nos testes

**Solução:**
1. ✅ Iniciar servidor FastAPI
2. ✅ Atualizar testes com URLs dinâmicas
3. ✅ Usar seletores Playwright mais robustos

---

## 🚀 Como Rodar os Testes E2E (Recomendado)

### **Passo 1: Iniciar o Servidor FastAPI**

Abra um **novo terminal** PowerShell:

```powershell
# Navegar para o projeto
cd c:\Users\valde\Desktop\programas\QUALIDADE\professor-simulator-clicker

# Ativar ambiente virtual (se existir)
venv\Scripts\Activate.ps1

# Ou instalar dependências diretamente
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Esperado:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

### **Passo 2: Rodar os Testes E2E (Novo Terminal)**

Em **outro terminal PowerShell**:

```powershell
# Navegar para o projeto
cd c:\Users\valde\Desktop\programas\QUALIDADE\professor-simulator-clicker

# Rodar TODOS os testes E2E
pytest tests/e2e -v

# OU rodar um arquivo específico
pytest tests/e2e/test_user_flows.py -v

# OU rodar um teste específico
pytest tests/e2e/test_user_flows.py::TestCadastroE2E::test_fluxo_cadastro_completo -v
```

---

## 📋 O Que Foi Corrigido

### **Antes ❌**
```python
# URLs hardcoded
page.goto("http://localhost:8000/index.html")

# Seletores frágeis
page.click("text=Login")
page.click("button:has-text('Entrar')")
page.fill('input[name="email"]', "admin@test.com")
```

### **Depois ✅**
```python
# URLs dinâmicas
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
page.goto(f"{BASE_URL}/index.html")

# Seletores robustos
page.get_by_role("button", name="Login").click()
page.get_by_role("button", name="Entrar").click()
page.get_by_placeholder("E-mail").fill("admin@test.com")

# Timeouts explícitos
page.set_default_timeout(10000)
```

---

## 🔍 Troubleshooting

### ❌ Erro: `net::ERR_CONNECTION_REFUSED`

**Causa:** Servidor FastAPI não está rodando

**Solução:**
```powershell
# Terminal 1: Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Verificar se está rodando
curl http://localhost:8000/docs
```

---

### ❌ Erro: `Timeout esperando elemento`

**Causa:** Elemento não encontrado ou página lenta

**Solução:**
```python
# Aumentar timeout
page.set_default_timeout(15000)  # 15 segundos

# Aguardar elemento aparecer
page.wait_for_selector(".elemento-css")

# Usar locate explícita
page.get_by_role("button", name="Login").wait_for(state="visible")
```

---

### ❌ Erro: `Element not found`

**Causa:** Seletor não corresponde ao HTML real

**Solução:**
```python
# Parar teste e inspecionar
page.pause()  # Abre inspector

# Usar locators mais robustos
page.get_by_role("button", name="Login")  # ✅ Melhor
page.locator("text=Login")  # ❌ Frágil
```

---

### ❌ Erro: `Browser failed to start`

**Causa:** Playwright não tem browsers instalados

**Solução:**
```powershell
playwright install chromium
```

---

## 📊 Status dos Testes

| Arquivo | Testes | Status | Notas |
|---------|--------|--------|-------|
| test_user_flows.py | 4 | ✅ Atualizado | Agora usa URLs dinâmicas |
| test_friends_flows.py | 3 | ✅ Atualizado | Seletores robustos |
| test_pokemon_flows.py | 3 | ✅ Atualizado | Validações simplificadas |
| test_shop_flows.py | 2 | ✅ Atualizado | Testes básicos |
| test_tournament_flows.py | 2 | ✅ Atualizado | Testes básicos |
| test_ui_game.py | 1 | ⚠️ Precisa revisar | Usa Live Server na 5500 |

---

## 🎬 Executar Tudo em Uma Linha

```powershell
# Terminal 1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 (após 3 segundos)
pytest tests/e2e -v --tb=short
```

---

## 📚 Referências Rápidas

### Seletores Playwright Robustos

```python
# ✅ Recomendados
page.get_by_role("button", name="Entrar")
page.get_by_placeholder("E-mail")
page.get_by_label("Senha")
page.get_by_text("Bem-vindo")

# ⚠️ Aceitáveis
page.locator("id=loginForm")
page.locator(".btn-primary")

# ❌ Frágeis
page.click("text=Login")
page.click("button:has-text('Entrar')")
page.query_selector_all()
```

### Comandos Úteis

```bash
# Rodar com output detalhado
pytest tests/e2e -vv -s

# Parar no primeiro erro
pytest tests/e2e -x

# Rodar só testes que falharam
pytest tests/e2e --lf

# Modo debug (pause no teste)
pytest tests/e2e --pdb

# Com cobertura
pytest tests/e2e --cov=app
```

---

## ✅ Checklist Final

- [ ] Servidor FastAPI rodando em http://localhost:8000
- [ ] Terminal com servidor permanece aberto
- [ ] Novo terminal para rodar testes
- [ ] Executar: `pytest tests/e2e -v`
- [ ] Testes rodando sem erros de conexão
- [ ] Testes validando corretamente

---

## 🎓 Próximas Melhorias

1. **Fixtures automáticas de servidor**: Usar pytest-asyncio para iniciar servidor automaticamente
2. **Testes paralelos**: `pytest -n auto` para rodar mais rápido
3. **CI/CD**: GitHub Actions para rodar automaticamente
4. **Screenshots**: `page.screenshot()` para evidência de falhas

---

## 📞 Dúvidas?

Se tiver problemas:
1. Verifique se servidor está rodando: `curl http://localhost:8000`
2. Veja os logs do pytest: `pytest tests/e2e -vv`
3. Use `page.pause()` para inspecionar no teste
4. Verifique o arquivo HTML para descobrir seletores corretos

**Boa sorte! 🚀**
