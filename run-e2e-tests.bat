@REM Script batch para rodar testes E2E no Windows
@REM Uso: run-e2e-tests.bat

@echo off
setlocal enabledelayedexpansion

echo.
echo ==========================================
echo  Professor Simulator - Testes E2E
echo ==========================================
echo.

REM Verificar se o servidor está rodando
echo [1] Verificando se servidor FastAPI está rodando na porta 8000...
netstat -ano | findstr ":8000" >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo ✓ Servidor já está rodando
) else (
    echo ✗ Servidor NÃO está rodando
    echo.
    echo Para iniciar o servidor em outro terminal, execute:
    echo.
    echo   cd professor-simulator-clicker
    echo   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    echo.
    pause
)

echo.
echo [2] Rodando testes E2E...
echo.

REM Rodar testes E2E
pytest tests/e2e -v --tb=short

echo.
echo ==========================================
echo  Testes Concluídos!
echo ==========================================
echo.

pause
