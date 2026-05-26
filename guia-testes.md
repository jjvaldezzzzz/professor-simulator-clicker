# 📋 Guia Completo - Como Rodar os Testes

Este projeto utiliza **pytest** com três níveis de testes: unitários, integração e E2E (end-to-end).

---

## 🔧 Pré-requisitos

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar o banco de dados (se não estiver rodando)
```bash
docker-compose up -d
```

### 3. Verificar variáveis de ambiente (se necessário)
O projeto usa PostgreSQL. Certifique-se de que as credenciais estão corretas em `app/database.py`

---

## 🎯 Rodar os Testes

### **Opção 1: Rodar TODOS os testes (Recomendado)**
```bash
pytest
```
Isso roda:
- ✅ Testes unitários
- ✅ Testes de integração  
- ✅ Testes E2E
- 📊 Gera relatório de cobertura

---

### **Opção 2: Rodar cada tipo de teste SEPARADAMENTE**

#### 🧪 Apenas Testes Unitários
```bash
pytest tests/unit -v
```

**O que testa:**
- Lógica individual das funções
- Validação de schemas
- CRUD de usuários, pokémon, amigos, etc.

**Pastas principais:**
- `tests/unit/users/` - Registro e cadastro
- `tests/unit/pokemon/` - CRUD de Pokémon
- `tests/unit/friends/` - Amigos
- `tests/unit/tournament/` - Torneios
- `tests/unit/game/` - Mecânica do jogo

---

#### 🔗 Testes de Integração
```bash
pytest tests/integration -v
```

**O que testa:**
- Fluxos entre múltiplos componentes
- Interação com banco de dados
- Endpoints da API funcionando em conjunto

**Pastas principais:**
- `tests/integration/test_users_integration.py`
- `tests/integration/test_pokemon_integration.py`
- `tests/integration/test_friends_integration.py`
- `tests/integration/test_shop_integration.py`
- `tests/integration/test_tournament_integration.py`

---

#### 🌐 Testes E2E (End-to-End)
```bash
pytest tests/e2e -v
```

**O que testa:**
- Cenários completos do usuário
- Interface web + API + Banco de dados
- Fluxos reais de gameplay

**Pastas principais:**
- `tests/e2e/test_user_flows.py` - Criar conta, login
- `tests/e2e/test_game.py` - Jogar o jogo
- `tests/e2e/test_pokemon_flows.py` - Capturar pokémon
- `tests/e2e/test_friends_flows.py` - Adicionar amigos
- `tests/e2e/test_shop_flows.py` - Comprar itens
- `tests/e2e/test_tournament_flows.py` - Participar de torneios

---

### **Opção 3: Usar o Script Automático** (Recomendado para CI/CD)
```bash
bash run-tests.sh
```

**Este script executa:**
1. ✅ Testes unitários
2. ✅ Testes de integração
3. ✅ Testes E2E
4. 📊 Gera cobertura de código
5. 🔍 Análise estática (pylint, flake8)
6. 🛡️ Verificação de segurança (bandit)

---

## 📊 Opções Úteis do pytest

### Com cobertura detalhada:
```bash
pytest --cov=app --cov-report=html
```
Abre o relatório em: `htmlcov/index.html`

### Com relatório HTML:
```bash
pytest --html=report.html --self-contained-html
```

### Apenas testes que passaram (sem os que falharam):
```bash
pytest --tb=short
```

### Rodar teste específico:
```bash
pytest tests/unit/users/test_cadastro.py -v
```

### Rodar função específica:
```bash
pytest tests/unit/users/test_cadastro.py::test_criar_usuario -v
```

### Rodar em paralelo (mais rápido):
```bash
pytest -n auto
```
*Requer: `pip install pytest-xdist`*

### Modo verbose (mais detalhes):
```bash
pytest -vv
```

### Parar no primeiro erro:
```bash
pytest -x
```

### Mostrar prints do teste:
```bash
pytest -s
```

---

## 📈 Interpretar os Resultados

### Exemplo de saída:
```
tests/unit/users/test_cadastro.py::test_criar_usuario PASSED      [15%]
tests/unit/pokemon/test_pokemon_crud.py::test_listar_pokemon PASSED [30%]
tests/integration/test_users_integration.py::test_fluxo_completo PASSED [60%]
tests/e2e/test_game.py::test_jogar_partida PASSED                 [100%]

============= 4 passed in 2.34s =============
```

**Legendas:**
- ✅ `PASSED` - Teste passou
- ❌ `FAILED` - Teste falhou
- ⊘ `SKIPPED` - Teste pulado
- ⚠️ `XFAIL` - Falha esperada
- 🔴 `ERROR` - Erro na execução

---

## 🐛 Troubleshooting

### ❌ Erro: "ModuleNotFoundError: No module named 'app'"
**Solução:**
```bash
# Certifique-se de estar na raiz do projeto
cd professor-simulator-clicker

# Reinstale as dependências
pip install -r requirements.txt

# Verifique se o pytest.ini está na raiz
ls pytest.ini
```

### ❌ Erro: "Falha ao conectar ao banco de dados"
**Solução:**
```bash
# Verifique se o container está rodando
docker ps

# Se não estiver, inicie:
docker-compose up -d

# Verifique os logs
docker-compose logs db
```

### ❌ Testes E2E muito lentos
**Solução:**
- Rode em paralelo: `pytest -n auto`
- Rode apenas unitários primeiro: `pytest tests/unit`

### ❌ Erro: "playwright not installed"
**Solução:**
```bash
pip install playwright
playwright install chromium
```

---

## ✅ Checklist - Rodar Testes Localmente

- [ ] Dependências instaladas: `pip install -r requirements.txt`
- [ ] PostgreSQL rodando: `docker-compose up -d`
- [ ] Testes unitários passando: `pytest tests/unit`
- [ ] Testes de integração passando: `pytest tests/integration`
- [ ] Testes E2E passando: `pytest tests/e2e`
- [ ] Cobertura acima de 70%: `pytest --cov=app`

---

## 📚 Referências

- 📖 [Documentação pytest](https://docs.pytest.org)
- 🎭 [Playwright para E2E](https://playwright.dev/python/)
- 📊 [Coverage.py](https://coverage.readthedocs.io)

---

**Dúvidas?** Verifique `TEST_CASES.md` para detalhes dos testes!
