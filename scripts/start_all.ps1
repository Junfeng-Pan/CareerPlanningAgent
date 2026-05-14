# Career Planning Agent - Start Script (PowerShell)
# Usage: .\start_all.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================"
Write-Host "    Career Planning Agent - Start"
Write-Host "============================================"
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$FrontendDir = Join-Path $RootDir "app\frontend_optimized2"
$LogsDir = Join-Path $RootDir "logs"

Write-Host "[1/5] Checking service status..."

# Check and stop backend on port 8000
Write-Host "[2/5] Stopping backend service..."
$backendProc = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($backendProc) {
    Write-Host "  Killing process on port 8000 (PID: $backendProc)"
    Stop-Process -Id $backendProc -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
} else {
    Write-Host "  Backend not running"
}

# Check and stop frontend on port 3000
Write-Host "[3/5] Stopping frontend service..."
$frontendProc = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($frontendProc) {
    Write-Host "  Killing process on port 3000 (PID: $frontendProc)"
    Stop-Process -Id $frontendProc -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
} else {
    Write-Host "  Frontend not running"
}

Write-Host "  Waiting for ports to release..."
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "[4/5] Creating log directory..."
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
}
Write-Host "  Log directory: $LogsDir"

Write-Host ""
Write-Host "[5/5] Checking frontend dependencies..."
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
Write-Host "    Services started!"
Write-Host "============================================"
Write-Host ""
Write-Host "  Backend API:  http://localhost:8000"
Write-Host "  Frontend:     http://localhost:3000"
Write-Host "  Log file:     $LogsDir\api_server.log"
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
