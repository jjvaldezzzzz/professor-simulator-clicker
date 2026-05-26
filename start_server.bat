@echo off
REM Script para iniciar o servidor FastAPI para testes E2E

echo ========================================
echo Professor Simulator - Servidor FastAPI
echo ========================================

cd /d "%~dp0"

echo.
echo [1/3] Ativando ambiente virtual...
if exist venv (
    call venv\Scripts\activate.bat
    echo ✓ Ambiente ativado
) else (
    echo ⚠ Ambiente virtual não encontrado. Instalando dependências...
    pip install -r requirements.txt
)

echo.
echo [2/3] Aguardando 2 segundos...
timeout /t 2 /nobreak

echo.
echo [3/3] Iniciando servidor FastAPI na porta 8000...
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
