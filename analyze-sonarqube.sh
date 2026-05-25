#!/bin/bash
# Script para executar análise com SonarQube
# Executar a partir da raiz do projeto

echo "🚀 Iniciando Análise SonarQube..."
echo ""

# 1. Aguardar SonarQube pronto
echo "⏳ Verificando se SonarQube está pronto..."
docker wait sonarqube 2>/dev/null || {
    echo "✅ SonarQube está rodando"
}

# 2. Executar testes com cobertura
echo ""
echo "🧪 Executando testes com cobertura..."
python -m pytest tests/ \
    --cov=app \
    --cov-report=xml \
    --cov-report=html \
    --cov-report=term-missing \
    -v \
    --tb=short

# 3. Verificar se coverage.xml foi gerado
if [ -f "coverage.xml" ]; then
    echo "✅ Coverage.xml gerado com sucesso"
else
    echo "❌ Erro: coverage.xml não foi gerado"
    exit 1
fi

# 4. Instalar SonarQube Scanner (se necessário)
echo ""
echo "📦 Verificando SonarQube Scanner..."
if ! command -v sonar-scanner &> /dev/null; then
    echo "⚠️  SonarQube Scanner não encontrado"
    echo "Instale com: pip install sonarqube-scanner"
    echo "Ou: brew install sonar-scanner (macOS)"
    exit 1
fi

# 5. Executar análise
echo ""
echo "📊 Enviando análise para SonarQube..."
sonar-scanner \
    -Dsonar.projectKey=professor-simulator-clicker \
    -Dsonar.projectName="Professor Simulator Clicker" \
    -Dsonar.projectVersion=1.0.0 \
    -Dsonar.sources=app \
    -Dsonar.tests=tests \
    -Dsonar.python.version=3.10 \
    -Dsonar.python.coverage.reportPaths=coverage.xml \
    -Dsonar.host.url=http://localhost:9000 \
    -Dsonar.login=admin \
    -Dsonar.password=admin

echo ""
echo "✅ Análise concluída!"
echo ""
echo "📈 Acessar Dashboard:"
echo "   http://localhost:9000/dashboard?id=professor-simulator-clicker"
echo ""
echo "📊 Relatório HTML de Cobertura:"
echo "   ./htmlcov/index.html"
