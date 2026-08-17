@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "CONDA_ENV=virtual_pay_platform_env"
set "CONDA_ACTIVATE=D:\Miniconda3\Scripts\activate.bat"
set "BACKEND_PORT=%~1"
set "BACKEND_HOST=%~2"

if "%BACKEND_PORT%"=="" set "BACKEND_PORT=8006"
if "%BACKEND_HOST%"=="" set "BACKEND_HOST=0.0.0.0"

echo Checking port %BACKEND_PORT%...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$connections = Get-NetTCPConnection -LocalPort %BACKEND_PORT% -State Listen -ErrorAction SilentlyContinue; if ($connections) { $connections | Select-Object -ExpandProperty OwningProcess -Unique | Where-Object { $_ -and (Get-Process -Id $_ -ErrorAction SilentlyContinue) } | ForEach-Object { Write-Host ('Stopping process ' + $_ + ' on port %BACKEND_PORT%'); Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue } }"

cd /d "%BACKEND_DIR%"
call "%CONDA_ACTIVATE%" "%CONDA_ENV%"
if errorlevel 1 (
  echo Failed to activate conda environment: %CONDA_ENV%
  pause
  exit /b 1
)

echo Project starting at http://127.0.0.1:%BACKEND_PORT%
echo Public access listens on %BACKEND_HOST%:%BACKEND_PORT%
uvicorn app.main:app --host %BACKEND_HOST% --port %BACKEND_PORT%

endlocal
