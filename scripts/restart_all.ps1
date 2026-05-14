# Career Planning Agent - Restart Script (PowerShell)
# Usage: .\restart_all.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================"
Write-Host "    Career Planning Agent - Restart"
Write-Host "============================================"
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$FrontendDir = Join-Path $RootDir "app\frontend_optimized2"
$LogsDir = Join-Path $RootDir "logs"

Write-Host "[1/4] Stopping backend service..."
$backendProc = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($backendProc) {
    Write-Host "  Killing process on port 8000 (PID: $backendProc)"
    Stop-Process -Id $backendProc -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
} else {
    Write-Host "  Backend not running"
}

Write-Host "[2/4] Stopping frontend service..."
$frontendProc = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($frontendProc) {
    Write-Host "  Killing process on port 3000 (PID: $frontendProc)"
    Stop-Process -Id $frontendProc -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
} else {
    Write-Host "  Frontend not running"
}

Write-Host "  Waiting for ports to release..."
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "[3/4] Cleaning log files..."
$logFile = Join-Path $LogsDir "api_server.log"
if (Test-Path $logFile) {
    Remove-Item $logFile -Force
}
Write-Host "  Logs cleared"

Write-Host ""
Write-Host "[4/4] Checking frontend dependencies..."
Set-Location $FrontendDir
if (-not (Test-Path "node_modules")) {
    Write-Host "  Installing frontend dependencies..."
    npm install
} else {
    Write-Host "  Frontend dependencies exist"
}

Write-Host ""
Write-Host "Starting services..."

# Start backend
Write-Host "  Starting backend..."
$backendArgs = @{
    FilePath = "python"
    ArgumentList = "app\backend\api_server.py"
    WorkingDirectory = $RootDir
    WindowStyle = "Normal"
    PassThru = $true
}
Start-Process @backendArgs
Write-Host "  Waiting for backend to initialize..."
Start-Sleep -Seconds 5

# Start frontend
Write-Host "  Starting frontend..."
$frontendArgs = @{
    FilePath = "npm"
    ArgumentList = "run", "dev"
    WorkingDirectory = $FrontendDir
    WindowStyle = "Normal"
    PassThru = $true
}
Start-Process @frontendArgs

Write-Host ""
Write-Host "============================================"
Write-Host "    Services restarted!"
Write-Host "============================================"
Write-Host ""
Write-Host "  Backend API:  http://localhost:8000"
Write-Host "  Frontend:     http://localhost:3000"
Write-Host "  Log file:     $LogsDir\api_server.log"
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
