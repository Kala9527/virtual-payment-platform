@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"
set "FRONTEND_PORT=%~1"

if "%FRONTEND_PORT%"=="" set "FRONTEND_PORT=5176"

echo Checking port %FRONTEND_PORT%...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$connections = Get-NetTCPConnection -LocalPort %FRONTEND_PORT% -State Listen -ErrorAction SilentlyContinue; if ($connections) { $connections | Select-Object -ExpandProperty OwningProcess -Unique | Where-Object { $_ -and (Get-Process -Id $_ -ErrorAction SilentlyContinue) } | ForEach-Object { Write-Host ('Stopping process ' + $_ + ' on port %FRONTEND_PORT%'); Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue } }"

cd /d "%FRONTEND_DIR%"
echo Frontend starting at http://127.0.0.1:%FRONTEND_PORT%
npm run dev -- --host 127.0.0.1 --port %FRONTEND_PORT%

endlocal
