# 🎯 Guia Prático: Verificação de Cobertura com SonarQube

**Data**: 25 de maio de 2026  
**Objetivo**: Executar análise de cobertura de testes usando SonarQube localmente

---

## 📋 Status Atual

✅ **SonarQube está rodando** em `http://localhost:9000`

```
Serviço         Status        URL
─────────────────────────────────────────
SonarQube       ✅ Ativo      http://localhost:9000
PostgreSQL      ✅ Ativo      localhost:5433
```

---

## 🚀 Passos para Executar Análise

### Opção 1: PowerShell (Windows) - ⭐ Recomendado

```powershell
# 1. Abrir PowerShell na pasta do projeto
cd "c:\Users\jorge\OneDrive\Área de Trabalho\clicker\professor-simulator-clicker"

# 2. Executar script de análise
powershell -ExecutionPolicy Bypass -File .\analyze-sonarqube.ps1

# 3. Seguir instruções interativas
```

### Opção 2: Bash/Shell Script

```bash
# 1. Dar permissão de execução
chmod +x analyze-sonarqube.sh

# 2. Executar script
./analyze-sonarqube.sh
```

### Opção 3: Manual Passo-a-Passo

#### 3.1 Instalar Dependências
```powershell
python -m pip install pytest pytest-cov coverage
```

#### 3.2 Executar Testes com Cobertura
```powershell
cd "c:\Users\jorge\OneDrive\Área de Trabalho\clicker\professor-simulator-clicker"

python -m pytest tests/ `
    --cov=app `
    --cov-report=xml `
    --cov-report=html `
    --cov-report=term-missing `
    -v
```

Isso gerará:
- 📄 `coverage.xml` - Relatório em XML
- 📁 `htmlcov/` - Relatório HTML interativo
- 📊 Saída no terminal

#### 3.3 Acessar Relatório HTML Localmente
```powershell
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

---

## 🔐 Acessar SonarQube Dashboard

### URL de Acesso
```
http://localhost:9000
```

### Credenciais Padrão
```
Usuário:  admin
Senha:    admin
```

⚠️ **Importante**: Altere a senha na primeira vez que acessar!

### Navegação

1. **Criar Novo Projeto**
   - Menu → Projects → Create Project
   - Project key: `professor-simulator-clicker`
   - Main branch: `main`

2. **Gerar Token de Autenticação**
   - Menu (canto superior direito) → My Account
   - Aba: Security
   - Seção: Generate Tokens
   - Criar token com nome `ci-token`
   - ⏱️ Validade: 90 dias

3. **Ver Resultados da Análise**
   - Projects → professor-simulator-clicker
   - Dashboard mostra:
     - Cobertura geral
     - Bugs encontrados
     - Code smells
     - Security vulnerabilities
     - Duplicação de código

---

## 📊 Interpretar Resultados

### Métricas Principales

| Métrica | O Que Significa | Meta |
|---------|-----------------|------|
| **Coverage** | % de código executado por testes | 70%+ |
| **Line Coverage** | Linhas cobertas | 85%+ |
| **Branch Coverage** | Condições cobertas | 80%+ |
| **Bugs** | Potenciais erros | 0 |
| **Code Smells** | Problemas de qualidade | < 10 |
| **Security** | Vulnerabilidades | 0 |
| **Duplications** | Código duplicado | < 5% |

### Cores e Status

| Cor | Significado | Ação |
|-----|-------------|------|
| 🟢 Verde | Bom (> 80%) | Continue assim |
| 🟡 Amarelo | Aceitável (70-80%) | Melhorar |
| 🔴 Vermelho | Crítico (< 70%) | Prioridade! |

---

## 🔍 Exemplos de Visualização

### 1. Dashboard Principal
```
┌─────────────────────────────────────────────────────┐
│ Professor Simulator Clicker                         │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Coverage: 87% ✅                    (Excelente)   │
│  Lines: 1,153 / 1,330                              │
│  Bugs: 2 🐛                          (Aceitável)   │
│  Code Smells: 8 💨                   (Aceitável)   │
│  Security: 0 🔒                      (Seguro)      │
│  Duplications: 2.1% 📋               (Bom)        │
│  Complexity: 5.8 ⚙️                  (Normal)     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 2. Cobertura por Arquivo
```
app/routers/users.py        ████████░ 95%  ✅ Excelente
app/routers/game.py         ████████░ 90%  ✅ Excelente
app/schemas.py              ████████░ 95%  ✅ Excelente
app/routers/pokemon.py      ███████░░ 88%  ✅ Muito Bom
app/routers/shop.py         ████████░ 85%  ✅ Muito Bom
app/models.py               ███████░░ 82%  ✅ Bom
```

### 3. Tendência Histórica
```
Cobertura Over Time

95% │                          ╱─
    │                    ╱───╱
85% │          ╱───────╱
    │    ╱───╱
75% │╱╱╱
65% ┼────────────────────────────
    │ Sprint 1  2   3  4 
```

---

## 🛠️ Troubleshooting

### ❌ SonarQube não está respondendo

**Solução:**
```powershell
# Verificar status
docker ps --filter "name=sonarqube"

# Reiniciar se necessário
docker restart sonarqube

# Ver logs
docker logs sonarqube --tail 20
```

### ❌ Erro ao conectar ao banco de dados

**Solução:**
```powershell
# Verificar conexão PostgreSQL
docker logs sonarqube-db

# Reiniciar serviços
docker-compose -f docker-compose.sonarqube.yml restart
```

### ❌ Coverage.xml não foi gerado

**Causas possíveis:**
1. Pytest não instalado
2. Módulos do projeto não encontrados
3. Erros em conftest.py

**Solução:**
```powershell
# Verificar instalaçõ
pip list | findstr pytest

# Reinstalar se necessário
pip install --upgrade pytest pytest-cov

# Executar com debug
python -m pytest tests/ -v --tb=long
```

### ❌ Permissão negada ao executar script PS1

**Solução:**
```powershell
# Alterar política de execução (apenas para esta sessão)
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Depois execute o script
.\analyze-sonarqube.ps1
```

---

## 📈 Integração com CI/CD (GitHub Actions)

Para automatizar análise a cada commit:

**Arquivo: `.github/workflows/sonarqube.yml`**

```yaml
name: SonarQube Analysis

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  sonarqube:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest-cov coverage
    
    - name: Run tests with coverage
      run: |
        pytest tests/ \
          --cov=app \
          --cov-report=xml \
          --cov-report=term-missing
    
    - name: SonarQube Scan
      uses: SonarSource/sonarqube-scan-action@master
      env:
        SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    
    - name: SonarQube Quality Gate
      uses: SonarSource/sonarqube-quality-gate-action@master
      timeout-minutes: 5
      env:
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

---

## 📊 Exemplos de Relatórios

### Relatório de Cobertura HTML

Após executar testes, abra:
```
htmlcov/index.html
```

Mostra:
- ✅ Linhas cobertas em verde
- ❌ Linhas não cobertas em vermelho
- 🟡 Linhas parcialmente cobertas em amarelo
- 📊 Gráficos de tendência

### Relatório SonarQube Dashboard

Acesse:
```
http://localhost:9000/dashboard?id=professor-simulator-clicker
```

Mostra:
- 📈 Todas as métricas
- 🐛 Lista de bugs
- 💨 Code smells
- 🔒 Vulnerabilidades
- 📋 Duplicações
- 📊 Histórico de análises

---

## ✅ Checklist de Validação

- [ ] Docker está rodando
- [ ] SonarQube está acessível em `http://localhost:9000`
- [ ] Projeto criado em SonarQube
- [ ] Token de autenticação gerado
- [ ] Dependências Python instaladas
- [ ] Testes executam com cobertura
- [ ] `coverage.xml` foi gerado
- [ ] Análise enviada para SonarQube
- [ ] Dashboard mostra métricas
- [ ] Relatório HTML acessível

---

## 📞 Próximas Ações Recomendadas

1. **Hoje**
   - [ ] Executar análise local
   - [ ] Revisar dashboard
   - [ ] Documentar insights

2. **Esta Semana**
   - [ ] Configurar CI/CD
   - [ ] Definir quality gates
   - [ ] Alertas automáticos

3. **Este Mês**
   - [ ] Treinar time em SonarQube
   - [ ] Estabelecer métricas por sprint
   - [ ] Integrar com pull requests

---

## 🎓 Recursos Úteis

- **SonarQube Docs**: https://docs.sonarqube.org/
- **Coverage.py Docs**: https://coverage.readthedocs.io/
- **Pytest Docs**: https://docs.pytest.org/
- **FastAPI Testing**: https://fastapi.tiangolo.com/advanced/testing-deps/

---

## 📝 Notas

- 💾 **Dados persistem**: Volumes Docker mantêm análises históricas
- 🔄 **Análises incrementais**: SonarQube detecta mudanças desde última análise
- 📊 **Webhooks**: Configure para alertas automáticos
- 🚀 **Performance**: Primeira análise pode demorar 5-10 minutos

---

✨ **Sua estrutura de testes está pronta para análise contínua!**

Qualquer dúvida, consulte os recursos ou execute os scripts interativos.

