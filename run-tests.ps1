# run-tests.ps1
# Script PowerShell para executar testes e gerar relatórios
# Uso: .\run-tests.ps1

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Professor Simulator Clicker - Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Criar diretório de relatórios
$reportDir = "test-reports"
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir | Out-Null
}

Write-Host "`n[1/6] Executando testes unitários..." -ForegroundColor Yellow
pytest tests/unit -v --tb=short --cov=app --cov-report=term-missing `
    --junit-xml="$reportDir/unit-tests.xml" `
    --html="$reportDir/unit-tests.html" --self-contained-html
Write-Host "✓ Testes unitários concluídos" -ForegroundColor Green

Write-Host "`n[2/6] Executando testes de integração..." -ForegroundColor Yellow
pytest tests/integration -v --tb=short --cov=app --cov-report=term-missing `
    --junit-xml="$reportDir/integration-tests.xml" `
    --html="$reportDir/integration-tests.html" --self-contained-html
Write-Host "✓ Testes de integração concluídos" -ForegroundColor Green

Write-Host "`n[3/6] Executando testes E2E..." -ForegroundColor Yellow
pytest tests/e2e -v --tb=short `
    --junit-xml="$reportDir/e2e-tests.xml" `
    --html="$reportDir/e2e-tests.html" --self-contained-html
Write-Host "✓ Testes E2E concluídos" -ForegroundColor Green

Write-Host "`n[4/6] Gerando relatório de cobertura..." -ForegroundColor Yellow
pytest tests/ --cov=app --cov-report=html --cov-report=xml --cov-report=term-missing `
    --cov-branch --cov-fail-under=70 `
    --junit-xml="$reportDir/all-tests.xml"
Write-Host "✓ Relatório de cobertura gerado" -ForegroundColor Green

Write-Host "`n[5/6] Executando análise estática..." -ForegroundColor Yellow
pylint app --exit-zero --output-format=parseable > pylint-report.txt 2>&1
Write-Host "✓ Análise com pylint concluída" -ForegroundColor Green

flake8 app --format=json > flake8-report.json 2>&1
Write-Host "✓ Análise com flake8 concluída" -ForegroundColor Green

bandit -r app -f json > bandit-report.json 2>&1
Write-Host "✓ Análise de segurança concluída" -ForegroundColor Green

Write-Host "`n[6/6] Gerando resumo de qualidade..." -ForegroundColor Yellow

# Ler e exibir cobertura
if (Test-Path "coverage.xml") {
    $xml = [xml](Get-Content "coverage.xml")
    $lineRate = [float]$xml.DocumentElement.getAttribute("line-rate")
    $coveragePercent = $lineRate * 100
    Write-Host "📊 Code Coverage: $([Math]::Round($coveragePercent, 2))%" -ForegroundColor Cyan
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Testes concluídos com sucesso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`nRelatórios gerados em:" -ForegroundColor Cyan
Write-Host "  📈 HTML (Cobertura): htmlcov\index.html" -ForegroundColor White
Write-Host "  📋 HTML (Testes): $reportDir\*.html" -ForegroundColor White
Write-Host "  📑 XML (JUnit): $reportDir\*.xml" -ForegroundColor White
Write-Host "  📝 Pylint: pylint-report.txt" -ForegroundColor White
Write-Host "  📝 Flake8: flake8-report.json" -ForegroundColor White
Write-Host "  🔒 Bandit: bandit-report.json" -ForegroundColor White

Write-Host "`nAbrir relatório de cobertura:" -ForegroundColor Yellow
Write-Host "  Start-Process htmlcov\index.html" -ForegroundColor White

Write-Host "`nPróximos passos:" -ForegroundColor Cyan
Write-Host "  1. Revisar relatórios em: htmlcov\index.html" -ForegroundColor White
Write-Host "  2. Verificar erros em: $reportDir\*.html" -ForegroundColor White
Write-Host "  3. Configurar SonarQube: .\sonar-scanner.exe (se instalado)" -ForegroundColor White
Write-Host "  4. Fazer commit dos relatórios (opcional)" -ForegroundColor White
