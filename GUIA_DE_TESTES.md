# Guia de Testes — Professor Simulator Clicker

Este guia explica como executar, documentar e gerar relatórios de testes e cobertura de código.

## Estrutura de Testes (3 Níveis)

```
tests/
├── unit/                       # Testes Unitários (UT)
│   ├── test_jogador_unit.py    # UT-UC01 a UT-UC04
│   ├── test_schemas.py         # Validação de schemas Pydantic
│   ├── game/
│   │   └── test_dar_aula.py
│   └── users/
│       └── test_cadastro.py
├── integration/                # Testes de Integração (IT)
│   ├── test_users_integration.py # IT-UC01 a IT-UC04
│   ├── test_shop.py            # IT-UC05 a IT-UC09
│   ├── test_pokemon.py         # IT-UC12 a IT-UC18
│   ├── test_tournament.py       # IT-UC19 a IT-UC23
│   ├── test_friends.py         # IT-UC24 a IT-UC28
│   └── flows/
│       ├── test_cadastro_flow.py
│       ├── test_dar_aula_flow.py
│       └── test_game_flow.py
└── e2e/                        # Testes End-to-End (E2E)
    ├── test_user_flows.py      # E2E-UC01 a E2E-UC04
    ├── test_shop_flows.py      # E2E-UC05 a E2E-UC11
    ├── test_pokemon_flows.py   # E2E-UC12 a E2E-UC18
    ├── test_tournament_flows.py # E2E-UC19 a E2E-UC23
    └── test_friends_flows.py   # E2E-UC24 a E2E-UC28
```

## Instalação de Dependências

```bash
# Instalar todas as dependências de teste
pip install -r requirements.txt

# Ou instalar apenas as de teste
pip install pytest pytest-cov pytest-mock pytest-playwright playwright \
            pylint flake8 bandit black isort sonar-scanner
```

## Executar Testes

### 1. Testes Unitários

```bash
# Executar todos os testes unitários
pytest tests/unit -v

# Executar testes unitários com cobertura
pytest tests/unit -v --cov=app --cov-report=html --cov-report=term-missing

# Executar teste específico
pytest tests/unit/test_jogador_unit.py::TestJogadorCreateSchema::test_jogador_create_valido -v
```

### 2. Testes de Integração

```bash
# Executar todos os testes de integração
pytest tests/integration -v

# Executar com cobertura
pytest tests/integration -v --cov=app --cov-report=html --cov-report=term-missing

# Executar teste específico
pytest tests/integration/test_users_integration.py::TestCadastroJogador::test_cadastro_sucesso_http_201 -v
```

### 3. Testes End-to-End

```bash
# Executar todos os testes E2E
pytest tests/e2e -v

# Executar com Playwright
pytest tests/e2e -v --headed  # Com navegador visível

# Executar teste específico
pytest tests/e2e/test_user_flows.py::test_fluxo_cadastro_completo -v
```

### 4. Executar Todos os Testes com Relatórios

```bash
# Opção 1: Usar script automatizado (recomendado)
bash run-tests.sh

# Opção 2: Manual com pytest
pytest tests/ \
    -v \
    --cov=app \
    --cov-report=html \
    --cov-report=xml \
    --cov-report=term-missing \
    --cov-branch \
    --cov-fail-under=70 \
    --junit-xml=test-reports/all-tests.xml \
    --html=test-reports/all-tests.html --self-contained-html
```

## Gerar Relatórios

### 1. Relatório de Cobertura

```bash
# Gerar relatório HTML de cobertura
pytest tests/ --cov=app --cov-report=html

# Abrir relatório no navegador
open htmlcov/index.html  # macOS
# ou
xdg-open htmlcov/index.html  # Linux
# ou
start htmlcov/index.html  # Windows
```

### 2. Análise Estática com SonarQube

```bash
# 1. Executar análise com pylint, flake8 e bandit
pylint app --exit-zero > pylint-report.txt 2>&1
flake8 app --format=json > flake8-report.json 2>&1
bandit -r app -f json > bandit-report.json 2>&1

# 2. Executar SonarQube Scanner
sonar-scanner

# 3. Acessar dashboard do SonarQube
# Padrão: http://localhost:9000
# Login: admin/admin
```

### 3. Relatórios JUnit XML

```bash
# Gerar relatório JUnit para integração com CI/CD
pytest tests/ --junit-xml=test-reports/junit.xml
```

## Filtrar Testes por Marker

```bash
# Executar apenas testes unitários
pytest -m unit -v

# Executar apenas testes de integração
pytest -m integration -v

# Executar apenas testes E2E
pytest -m e2e -v

# Executar todos exceto E2E
pytest -m "not e2e" -v

# Executar apenas testes de API
pytest -m api -v

# Executar testes rápidos (sem slow)
pytest -m "not slow" -v
```

## Documentação de Testes

Cada caso de teste segue o padrão:

```python
def test_exemplo_case(client, db_session):
    """
    IT-UC01-001: Descrição do teste (formato: TIPO-UCXX-NNN)
    
    Objetivo: O que será testado
    Pré-condições: Estado inicial do sistema
    Dados de entrada: Inputs do teste
    Resultado esperado: Output desejado
    """
    # Arrange
    ... setup ...
    
    # Act
    response = client.post("/endpoint", json=payload)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["expected_field"] == "expected_value"
```

### Padrão de ID de Teste

- **UT-UC01-001**: Unitário, Caso de Uso 01, Teste 001
- **IT-UC02-002**: Integração, Caso de Uso 02, Teste 002
- **E2E-UC03-001**: End-to-End, Caso de Uso 03, Teste 001

## Metas de Cobertura

| Nível | Meta | Ferramenta |
|-------|------|-----------|
| Unitário | 85–100% | pytest-cov |
| Integração | 70–85% | pytest-cov |
| E2E | Fluxos críticos | Playwright |
| **Geral** | **70–100%** | pytest-cov + SonarQube |

## SonarQube Dashboard

Após executar `sonar-scanner`, acesse:

```
http://localhost:9000
```

Métricas monitoradas:
- **Code Coverage**: % de código coberto por testes
- **Code Smells**: Problemas de qualidade (recomendado: < 5)
- **Bugs**: Problemas detectados (recomendado: 0)
- **Vulnerabilities**: Problemas de segurança (recomendado: 0)
- **Duplications**: % de código duplicado (recomendado: < 3%)
- **Complexity**: Complexidade ciclomática (recomendado: média < 5)

## Troubleshooting

### Erro: "No module named 'app'"

```bash
# Adicione o diretório ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

### Erro: "Database locked"

```bash
# Use SQLite em memória (padrão em conftest.py)
# Ou aguarde a liberação:
sleep 1 && pytest tests/
```

### Erro: "Playwright browsers not installed"

```bash
# Instalar browsers do Playwright
playwright install
```

### Erro: "SonarQube server not running"

```bash
# Iniciar Docker com SonarQube
docker run -d --name sonarqube -p 9000:9000 sonarqube:latest

# Aguardar inicialização (2-3 minutos)
sleep 180

# Acessar: http://localhost:9000 (admin/admin)
```

## Integração com CI/CD

### GitHub Actions Example

```yaml
name: Tests & Quality

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: 3.10
      
      - run: pip install -r requirements.txt
      
      - run: pytest tests/ --cov=app --cov-report=xml
      
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

## Checklist de Qualidade

- [ ] Todos os testes passam localmente
- [ ] Cobertura de código >= 70%
- [ ] SonarQube: Sem bloqueadores
- [ ] SonarQube: < 10 code smells
- [ ] SonarQube: 0 bugs críticos
- [ ] Relatórios HTML gerados
- [ ] Documentação atualizada

## Próximos Passos

1. ✅ Implementar testes unitários para UC01-UC04
2. ✅ Implementar testes de integração para UC01-UC04
3. ⏳ Implementar testes unitários para UC05-UC28
4. ⏳ Implementar testes de integração para UC05-UC28
5. ⏳ Implementar testes E2E para UC01-UC28
6. ⏳ Configurar SonarQube pipeline
7. ⏳ Gerar relatórios finais de cobertura

## Contato & Dúvidas

Para dúvidas sobre testes, consulte:
- `PLANO_DE_TESTES.md` - Estratégia completa
- `CASOS_DE_USO.md` - Mapeamento UC/testes
- Código dos testes comentado em cada arquivo
