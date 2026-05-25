# Script PowerShell para executar análise com SonarQube
# Executar de: powershell -ExecutionPolicy Bypass -File .\analyze-sonarqube.ps1

Write-Host "🚀 Iniciando Análise SonarQube..." -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se SonarQube está rodando
Write-Host "⏳ Verificando status do SonarQube..." -ForegroundColor Yellow
$sonarqube_status = docker ps --filter "name=sonarqube" --format "{{.Status}}" 2>$null
if ($sonarqube_status -contains "Up") {
    Write-Host "✅ SonarQube está rodando" -ForegroundColor Green
} else {
    Write-Host "❌ SonarQube não está rodando!" -ForegroundColor Red
    Write-Host "Inicie com: docker-compose -f docker-compose.sonarqube.yml up -d"
    exit 1
}

# 2. Verificar dependências Python
Write-Host ""
Write-Host "📦 Verificando dependências..." -ForegroundColor Yellow
$deps = @("pytest", "pytest-cov", "coverage")
foreach ($dep in $deps) {
    python -m pip show $dep >$null 2>&1
    if ($?) {
        Write-Host "✅ $dep instalado" -ForegroundColor Green
    } else {
        Write-Host "⚠️  $dep não encontrado" -ForegroundColor Yellow
        Write-Host "Instalando $dep..."
        python -m pip install $dep -q
    }
}

# 3. Executar testes com cobertura
Write-Host ""
Write-Host "🧪 Executando testes com cobertura..." -ForegroundColor Cyan
python -m pytest tests/ `
    --cov=app `
    --cov-report=xml `
    --cov-report=html `
    --cov-report=term-missing `
    -v `
    --tb=short

# 4. Verificar se coverage.xml foi gerado
if (Test-Path "coverage.xml") {
    Write-Host "✅ Coverage.xml gerado com sucesso" -ForegroundColor Green
} else {
    Write-Host "❌ Erro: coverage.xml não foi gerado" -ForegroundColor Red
    exit 1
}

# 5. Buscar token SonarQube (prompt do usuário)
Write-Host ""
Write-Host "🔐 Token SonarQube:" -ForegroundColor Yellow
Write-Host "   1. Acesse http://localhost:9000"
Write-Host "   2. Menu → My Account → Security"
Write-Host "   3. Gere um novo token"
Write-Host ""
$token = Read-Host "Cole o token (ou deixe em branco para usar 'admin')"
if ([string]::IsNullOrWhiteSpace($token)) {
    $token = "admin"
    Write-Host "⚠️  Usando credentials padrão (admin/admin)" -ForegroundColor Yellow
}

# 6. Executar análise SonarQube
Write-Host ""
Write-Host "📊 Enviando análise para SonarQube..." -ForegroundColor Cyan

# Tentar com sonar-scanner CLI
$sonarscanner_exists = Get-Command sonar-scanner -ErrorAction SilentlyContinue
if ($sonarscanner_exists) {
    sonar-scanner `
        -Dsonar.projectKey=professor-simulator-clicker `
        -Dsonar.projectName="Professor Simulator Clicker" `
        -Dsonar.projectVersion=1.0.0 `
        -Dsonar.sources=app `
        -Dsonar.tests=tests `
        -Dsonar.python.version=3.10 `
        -Dsonar.python.coverage.reportPaths=coverage.xml `
        -Dsonar.host.url=http://localhost:9000 `
        -Dsonar.login=$token
    Write-Host "✅ Análise enviada para SonarQube" -ForegroundColor Green
} else {
    Write-Host "⚠️  sonar-scanner não encontrado" -ForegroundColor Yellow
    Write-Host "Instale com: pip install sonarqube-scanner" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Pulando etapa de envio para SonarQube" -ForegroundColor Yellow
}

# 7. Exibir resultados
Write-Host ""
Write-Host "✅ Análise concluída!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Próximos Passos:" -ForegroundColor Cyan
Write-Host "   📈 Dashboard SonarQube:"
Write-Host "      http://localhost:9000/dashboard?id=professor-simulator-clicker" -ForegroundColor Green
Write-Host ""
Write-Host "   📊 Relatório HTML de Cobertura:"
Write-Host "      ./htmlcov/index.html" -ForegroundColor Green
Write-Host ""
Write-Host "   📋 Arquivo de Cobertura XML:"
Write-Host "      ./coverage.xml" -ForegroundColor Green
Write-Host ""
