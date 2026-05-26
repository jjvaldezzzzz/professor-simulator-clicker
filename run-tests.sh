#!/bin/bash
# run-tests.sh - Script para executar testes e gerar relatórios

set -e

echo "=========================================="
echo "Professor Simulator Clicker - Test Suite"
echo "=========================================="

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Diretórios
REPORT_DIR="test-reports"
COVERAGE_DIR="htmlcov"

# Criar diretório de relatórios
mkdir -p $REPORT_DIR

echo -e "\n${YELLOW}1. Executando testes unitários...${NC}"
pytest tests/unit -v --tb=short --cov=app --cov-report=term-missing \
    --junit-xml=$REPORT_DIR/unit-tests.xml \
    --html=$REPORT_DIR/unit-tests.html --self-contained-html \
    || true

echo -e "\n${YELLOW}2. Executando testes de integração...${NC}"
pytest tests/integration -v --tb=short --cov=app --cov-report=term-missing \
    --junit-xml=$REPORT_DIR/integration-tests.xml \
    --html=$REPORT_DIR/integration-tests.html --self-contained-html \
    || true

echo -e "\n${YELLOW}3. Executando testes E2E...${NC}"
pytest tests/e2e -v --tb=short \
    --junit-xml=$REPORT_DIR/e2e-tests.xml \
    --html=$REPORT_DIR/e2e-tests.html --self-contained-html \
    || true

echo -e "\n${YELLOW}4. Gerando relatório de cobertura...${NC}"
pytest tests/ --cov=app --cov-report=html --cov-report=xml --cov-report=term-missing \
    --cov-branch --cov-fail-under=70 \
    --junit-xml=$REPORT_DIR/all-tests.xml \
    || true

echo -e "\n${YELLOW}5. Executando análise estática com pylint...${NC}"
pylint app --exit-zero --output-format=parseable > pylint-report.txt 2>&1 || true

echo -e "\n${YELLOW}6. Executando análise com flake8...${NC}"
flake8 app --format=default > flake8-report.txt 2>&1 || true

echo -e "\n${YELLOW}7. Executando verificação de segurança com bandit...${NC}"
bandit -r app -f json > bandit-report.json 2>&1 || true

echo -e "\n${GREEN}=========================================="
echo "Testes concluídos!"
echo "=========================================="
echo -e "\nRelatórios gerados em:"
echo "  - HTML (Cobertura): $COVERAGE_DIR/index.html"
echo "  - HTML (Testes): $REPORT_DIR/*.html"
echo "  - XML (JUnit): $REPORT_DIR/*.xml"
echo "  - Pylint: pylint-report.txt"
echo "  - Flake8: flake8-report.txt"
echo "  - Bandit: bandit-report.json"
echo ""
