@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found.
    echo Create it with: python -m venv .venv
    echo Then install dependencies with: .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist ".env" goto missing_env
for %%A in (".env") do if %%~zA==0 goto missing_env

".venv\Scripts\python.exe" manage.py chat %*
set "exit_code=%errorlevel%"

if not "%exit_code%"=="0" (
    echo.
    echo O chat foi encerrado devido a um problema.
)

echo.
echo Pressione qualquer tecla para fechar esta janela.
pause >nul
exit /b %exit_code%

:missing_env
echo .env file is missing or empty.
echo Copy .env.example to .env, then configure DJANGO_SECRET_KEY and GEMINI_API_KEY.
echo.
echo PowerShell command: Copy-Item .env.example .env
pause
exit /b 1
