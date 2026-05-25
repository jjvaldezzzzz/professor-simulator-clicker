# SonarQube & CI/CD Setup

## 1. Levantando SonarQube com Docker

### Opção A: Docker Compose (Recomendado)

```bash
# Iniciar SonarQube + PostgreSQL
docker-compose -f docker-compose.sonarqube.yml up -d

# Aguardar inicialização (2-3 minutos)
docker-compose -f docker-compose.sonarqube.yml logs -f sonarqube | grep "SonarQube is up"

# Acessar
# URL: http://localhost:9000
# Login: admin / admin
# Mudar senha na primeira vez
```

### Opção B: Docker Direto

```bash
# Sem banco de dados (desenvolvimento local)
docker run -d --name sonarqube -p 9000:9000 sonarqube:latest

# Com PostgreSQL
docker network create sonar-net
docker run -d --name postgres-sonar --network sonar-net \
  -e POSTGRES_USER=sonar \
  -e POSTGRES_PASSWORD=sonarpassword \
  -e POSTGRES_DB=sonarqube \
  postgres:15-alpine

docker run -d --name sonarqube --network sonar-net -p 9000:9000 \
  -e SONARQUBE_JDBC_URL=jdbc:postgresql://postgres-sonar:5432/sonarqube \
  -e SONARQUBE_JDBC_USERNAME=sonar \
  -e SONARQUBE_JDBC_PASSWORD=sonarpassword \
  sonarqube:latest
```

## 2. Configurar Primeiro Projeto no SonarQube

1. Abrir: http://localhost:9000
2. Login: admin / admin
3. Criar nova senha (obrigatório)
4. Criar novo projeto:
   - **Project key**: `professor-simulator-clicker`
   - **Display name**: `Professor Simulator Clicker`
   - **Main branch**: `main`
5. Escolher **Python** como linguagem
6. Gerar **token de autenticação**:
   - Menu → My Account → Security → Generate Tokens
   - Nome: `ci-token`
   - Expiration: 90 days
   - Copiar token (será necessário no CI/CD)

## 3. Executar SonarQube Scanner Localmente

### Instalar SonarQube Scanner

```bash
# macOS (Homebrew)
brew install sonar-scanner

# Ubuntu/Debian
sudo apt-get install sonar-scanner

# Windows (via chocolatey)
choco install sonar-scanner

# Ou baixar manualmente
# https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
```

### Executar Análise

```bash
# 1. Certificar que testes rodaram e geraram coverage.xml
pytest tests/ --cov=app --cov-report=xml --cov-report=term-missing

# 2. Executar SonarQube Scanner
sonar-scanner \
  -Dsonar.projectKey=professor-simulator-clicker \
  -Dsonar.sources=app \
  -Dsonar.tests=tests \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=seu_token_aqui

# 3. Acessar resultados
# URL: http://localhost:9000/dashboard?id=professor-simulator-clicker
```

### Executar via docker

```bash
# Se preferir não instalar localmente
docker run --rm \
  -v $(pwd):/usr/src \
  -e SONAR_HOST_URL=http://sonarqube:9000 \
  -e SONAR_LOGIN=seu_token_aqui \
  --network sonar-net \
  sonarsource/sonar-scanner-cli
```

## 4. Configurar CI/CD com GitHub Actions

### 4.1 Criar arquivo de workflow

Crie `.github/workflows/quality.yml`:

```yaml
name: Code Quality & Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test-and-analyze:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # SonarQube precisa do histórico completo
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run Pytest with Coverage
        run: |
          pytest tests/ \
            -v \
            --cov=app \
            --cov-report=xml \
            --cov-report=html \
            --cov-report=term-missing \
            --junit-xml=junit.xml
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: true
          verbose: true
      
      - name: Run pylint
        run: |
          pylint app --exit-zero --output-format=parseable > pylint-report.txt
      
      - name: Run flake8
        run: |
          flake8 app --format=json > flake8-report.json
      
      - name: Run bandit
        run: |
          bandit -r app -f json > bandit-report.json
      
      - name: SonarQube Scan
        uses: SonarSource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
        with:
          args: >
            -Dsonar.projectKey=professor-simulator-clicker
            -Dsonar.sources=app
            -Dsonar.tests=tests
            -Dsonar.python.coverage.reportPaths=coverage.xml
            -Dsonar.python.pylint.reportPaths=pylint-report.txt
            -Dsonar.python.flake8.reportPath=flake8-report.json
            -Dsonar.externalIssuesReportPaths=bandit-report.json
      
      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: |
            junit.xml
            htmlcov/
            pylint-report.txt
            flake8-report.json
            bandit-report.json
      
      - name: Comment PR with Results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const coverage = fs.readFileSync('htmlcov/status.json', 'utf8');
            const data = JSON.parse(coverage);
            
            const comment = `
            ## Test Results
            - **Coverage**: ${data.percent_covered}%
            - **Covered**: ${data.num_statements - data.num_missing} / ${data.num_statements}
            - **Missing**: ${data.num_missing}
            
            [View Full Report](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})
            `;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### 4.2 Configurar Secrets no GitHub

1. Repository → Settings → Secrets and variables → Actions
2. Adicione:
   - `SONAR_HOST_URL`: `https://seu-sonarqube.com` (ou `http://localhost:9000` para testes)
   - `SONAR_TOKEN`: Token gerado no passo 2.6

## 5. GitLab CI/CD (Alternativa)

Crie `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - analyze
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - venv/

test:unit:
  stage: test
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - pytest tests/unit --cov=app --cov-report=xml --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

test:integration:
  stage: test
  image: python:3.10
  services:
    - postgres:15-alpine
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
  script:
    - pip install -r requirements.txt
    - pytest tests/integration --cov=app --cov-report=xml
  artifacts:
    reports:
      junit: junit.xml

sonarqube:analyze:
  stage: analyze
  image: sonarsource/sonar-scanner-cli:latest
  variables:
    SONAR_HOST_URL: "$CI_SERVER_PROTOCOL://$CI_SERVER_HOST:$SONAR_PORT"
    SONAR_TOKEN: "$SONAR_TOKEN"
  script:
    - sonar-scanner
  only:
    - main
    - merge_requests
```

## 6. Verificar Configuração de Qualidade

```bash
# 1. Verificar se sonar-project.properties está correto
cat sonar-project.properties

# 2. Rodar testes
pytest tests/ --cov=app --cov-report=xml

# 3. Verificar coverage.xml foi gerado
ls -lah coverage.xml

# 4. Rodar scanner
sonar-scanner -Dsonar.login=seu_token

# 5. Acessar dashboard
echo "http://localhost:9000/dashboard?id=professor-simulator-clicker"
```

## 7. Métricas de Qualidade Esperadas

| Métrica | Mínimo | Alvo | Ideal |
|---------|--------|------|-------|
| Code Coverage | 70% | 80% | 90%+ |
| Code Smells | - | < 5 | 0 |
| Bugs | - | 0 | 0 |
| Vulnerabilities | - | 0 | 0 |
| Duplications | - | < 3% | < 1% |
| Complexity (avg) | - | < 5 | < 3 |
| Security Rating | - | A | A |
| Maintainability | - | A | A |

## 8. Troubleshooting SonarQube

### SonarQube não inicia

```bash
# Ver logs
docker-compose -f docker-compose.sonarqube.yml logs sonarqube

# Aumentar memória (SonarQube precisa de 2GB mínimo)
docker-compose -f docker-compose.sonarqube.yml down
# Adicionar em docker-compose.sonarqube.yml:
# environment:
#   - sonar.ce.javaAdditionalOpts=-Xmx2G
docker-compose -f docker-compose.sonarqube.yml up -d
```

### Coverage não aparece no SonarQube

```bash
# Certificar que coverage.xml foi gerado com o caminho correto
pytest tests/ --cov=app --cov-report=xml

# Verificar sonar-project.properties
grep "sonar.python.coverage" sonar-project.properties

# Re-rodar scanner com opção explícita
sonar-scanner -Dsonar.python.coverage.reportPaths=coverage.xml
```

### Erro de autenticação

```bash
# Gerar novo token no SonarQube
# Menu → My Account → Security → Generate Tokens

# Usar token na linha de comando
sonar-scanner -Dsonar.login=seu_novo_token
```

## 9. Próximos Passos

- [ ] Levantar SonarQube com Docker
- [ ] Configurar primeiro projeto
- [ ] Gerar token de autenticação
- [ ] Executar análise local
- [ ] Configurar GitHub Actions / GitLab CI
- [ ] Validar métricas de qualidade
- [ ] Configurar quality gates
- [ ] Implementar pre-commit hooks

## Referências

- [SonarQube Documentation](https://docs.sonarqube.org/)
- [SonarQube Python Plugin](https://docs.sonarqube.org/latest/analysis/languages/python/)
- [GitHub Actions & SonarQube](https://docs.sonarqube.org/latest/analysis/github-integration/)
- [GitLab CI & SonarQube](https://docs.sonarqube.org/latest/analysis/gitlab-integration/)
