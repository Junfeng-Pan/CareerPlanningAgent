@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================
echo     Career Planning Agent - Start
echo ============================================
echo.

cd /d "%~dp0.."
set ROOT_DIR=%CD%

echo [1/4] Finding running services...

REM Get PIDs using wmic (more reliable)
wmic process where "commandline like '%%api_server.py%%'" get ProcessId /value > %TEMP%\backend_pid.txt
for /f "tokens=2 delims==" %%a in ('findstr "ProcessId" %TEMP%\backend_pid.txt 2^>nul') do (
    set BACKEND_PID=%%a
)

wmic process where "commandline like '%%npm run dev%%'" get ProcessId /value > %TEMP%\frontend_pid.txt
for /f "tokens=2 delims==" %%a in ('findstr "ProcessId" %TEMP%\frontend_pid.txt 2^>nul') do (
    set FRONTEND_PID=%%a
)

echo [2/4] Stopping existing services...

if defined BACKEND_PID (
    echo   Stopping backend (PID: !BACKEND_PID!)
    taskkill /F /PID !BACKEND_PID! >nul 2>&1
) else (
    echo   Backend not running
)

if defined FRONTEND_PID (
    echo   Stopping frontend (PID: !FRONTEND_PID!)
    taskkill /F /PID !FRONTEND_PID! >nul 2>&1
) else (
    echo   Frontend not running
)

REM Also try to kill by port as fallback
for /f "delims=" %%i in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    for %%a in (%%i) do set PID=%%a
    if defined PID (
        echo   Killing process on port 8000 (PID: !PID!)
        taskkill /F /PID !PID! >nul 2>&1
        set PID=
    )
)

for /f "delims=" %%i in ('netstat -ano ^| findstr ":3000 " ^| findstr "LISTENING"') do (
    for %%a in (%%i) do set PID=%%a
    if defined PID (
        echo   Killing process on port 3000 (PID: !PID!)
        taskkill /F /PID !PID! >nul 2>&1
        set PID=
    )
)

echo   Waiting for ports to be released...
timeout /t 3 >nul

echo.
echo [3/4] Creating log directory...
if not exist "%ROOT_DIR%\logs" mkdir "%ROOT_DIR%\logs"
echo   Log directory: %ROOT_DIR%\logs

echo.
echo [4/4] Starting services...

start "Backend" cmd /k "cd /d %ROOT_DIR% && echo Starting backend... && python app\backend\api_server.py"
echo   Waiting for backend to initialize...
timeout /t 5 >nul

start "Frontend" cmd /k "cd /d %ROOT_DIR%\app\frontend_optimized && echo Starting frontend... && npm run dev"

echo.
echo ============================================
echo     Services started!
echo ============================================
echo.
echo   Backend API:  http://localhost:8000
echo   Frontend:     http://localhost:3000
echo   Log file:     %ROOT_DIR%\logs\api_server.log
echo.
pause

REM Cleanup temp files
del /q %TEMP%\backend_pid.txt >nul 2>&1
del /q %TEMP%\frontend_pid.txt >nul 2>&1
