@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo.
echo ============================================
echo     Career Planning Agent - Restart
echo ============================================
echo.

cd /d "%~dp0.."
set ROOT_DIR=%CD%
set FRONTEND_DIR=%ROOT_DIR%\app\frontend_optimized2
set BACKEND_SCRIPT=%ROOT_DIR%\app\backend\api_server.py
set LOGS_DIR=%ROOT_DIR%\logs

echo [1/4] Stopping existing services...

REM Stop processes on ports
for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo   Stopping backend (PID: %%i)
    taskkill /F /PID %%i 2>nul
)
for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
    echo   Stopping frontend (PID: %%i)
    taskkill /F /PID %%i 2>nul
)

timeout /t 3 >nul

echo.
echo [2/4] Cleaning log files...
del /q "%LOGS_DIR%\api_server.log" 2>nul

echo.
echo [3/4] Checking frontend dependencies...
cd /d "%FRONTEND_DIR%"
if not exist "node_modules" (
    echo   Installing npm dependencies...
    call npm install
)

echo.
echo [4/4] Starting services...

REM Start backend in new window
echo   Starting backend...
start "Backend" cmd /c "cd /d %ROOT_DIR% && python %BACKEND_SCRIPT%"
timeout /t 3 >nul

REM Start frontend in new window
echo   Starting frontend...
start "Frontend" cmd /c "cd /d %FRONTEND_DIR% && npm run dev"

echo.
echo ============================================
echo     Services restarted!
echo ============================================
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo.
pause
