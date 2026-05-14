# 职业规划智能体 - 一键重启脚本 (PowerShell 版本)

Write-Host ""
Write-Host "============================================"
Write-Host "    职业规划智能体 - 一键重启脚本"
Write-Host "============================================"
Write-Host ""

# 获取项目根目录
$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

Write-Host "[1/3] 终止已运行的服务..."

# 终止后端服务
$backendPid = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($backendPid) {
    Write-Host "  终止后端服务 (PID: $backendPid)"
    Stop-Process -Id $backendPid -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "  后端服务未运行"
}

# 终止前端服务
$frontendPid = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($frontendPid) {
    Write-Host "  终止前端服务 (PID: $frontendPid)"
    Stop-Process -Id $frontendPid -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "[2/3] 清空日志文件..."
$logPath = Join-Path $RootDir "logs\api_server.log"
if (Test-Path $logPath) {
    Clear-Content $logPath
    Write-Host "  日志已清空"
}

Write-Host ""
Write-Host "[3/3] 启动服务..."

# 启动后端
Write-Host "  启动后端服务..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootDir'; python app\backend\api_server.py" -WindowStyle Normal

Write-Host "  等待后端服务启动..."
Start-Sleep -Seconds 5

# 启动前端
Write-Host "  启动前端服务..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootDir\app\frontend_optimized'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "============================================"
Write-Host "    服务重启完成!"
Write-Host "============================================"
Write-Host ""
Write-Host "  后端 API:  http://localhost:8000"
Write-Host "  前端页面：http://localhost:3000"
Write-Host "  日志文件：$RootDir\logs\api_server.log"
Write-Host ""
Write-Host "按任意键继续..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
