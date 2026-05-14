@echo off
chcp 65001 >nul
echo ========================================
echo   职业规划智能体前端 - 启动脚本
echo ========================================
echo.

cd /d "%~dp0"

if not exist "node_modules" (
    echo [1/2] 正在安装依赖...
    call npm install
    if errorlevel 1 (
        echo 依赖安装失败！
        pause
        exit /b 1
    )
    echo 依赖安装完成！
    echo.
)

echo [2/2] 正在启动开发服务器...
echo.
echo 访问地址：http://localhost:3000
echo 按 Ctrl+C 停止服务
echo.

call npm run dev
