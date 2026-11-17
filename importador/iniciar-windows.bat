@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1 || (echo Instale Python 3.11+ primeiro. && pause && exit /b 1)
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv || (echo Erro criando ambiente virtual. && pause && exit /b 1)
)
.venv\Scripts\python.exe -m pip install -r requirements.txt || (echo Erro instalando bibliotecas. && pause && exit /b 1)
.venv\Scripts\python.exe wmk_architecture_studio.py
if errorlevel 1 (echo O programa terminou com erro. && pause)
endlocal
