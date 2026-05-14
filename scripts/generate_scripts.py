#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 Windows 批处理启动脚本 (GBK 编码)
"""
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

restart_content = """@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================
echo     职业规划智能体 - 一键重启脚本
echo ============================================
echo.

cd /d "%~dp0.."
set ROOT_DIR=%CD%

echo [1/3] 终止已运行的服务...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 "') do (
    echo   终止后端服务 (PID: %%a)
    taskkill /F /PID %%a
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000 "') do (
    echo   终止前端服务 (PID: %%a)
    taskkill /F /PID %%a
)

timeout /t 2 >nul

echo.
echo [2/3] 清空日志文件...
if exist "%ROOT_DIR%\\logs\\api_server.log" (
    echo. > "%ROOT_DIR%\\logs\\api_server.log"
    echo   日志已清空
)

echo.
echo [3/3] 启动服务...

start "Backend" cmd /k "cd /d %ROOT_DIR% && python app\\backend\\api_server.py"
echo   等待后端服务启动...
timeout /t 5 >nul

start "Frontend" cmd /k "cd /d %ROOT_DIR%\\app\\frontend_optimized && npm run dev"

echo.
echo ============================================
echo     服务重启完成!
echo ============================================
echo.
echo   后端 API:  http://localhost:8000
echo   前端页面：http://localhost:3000
echo   日志文件：%ROOT_DIR%\\logs\\api_server.log
echo.
pause
"""

start_content = """@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================
echo     职业规划智能体 - 一键启动脚本
echo ============================================
echo.

cd /d "%~dp0.."
set ROOT_DIR=%CD%

echo [1/4] 检查已运行的服务...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 "') do (
    echo   终止后端服务 (PID: %%a)
    taskkill /F /PID %%a
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000 "') do (
    echo   终止前端服务 (PID: %%a)
    taskkill /F /PID %%a
)

timeout /t 2 >nul

echo.
echo [2/4] 创建日志目录...
if not exist "%ROOT_DIR%\\logs" mkdir "%ROOT_DIR%\\logs"
echo   日志目录：%ROOT_DIR%\\logs

echo.
echo [3/4] 启动后端服务...

start "Backend" cmd /k "cd /d %ROOT_DIR% && echo 后端服务启动中... && python app\\backend\\api_server.py"
echo   等待后端服务启动...
timeout /t 5 >nul

echo.
echo [4/4] 启动前端服务...

start "Frontend" cmd /k "cd /d %ROOT_DIR%\\app\\frontend_optimized && echo 前端服务启动中... && npm run dev"

echo.
echo ============================================
echo     服务启动完成!
echo ============================================
echo.
echo   后端 API:  http://localhost:8000
echo   前端页面：http://localhost:3000
echo   日志文件：%ROOT_DIR%\\logs\\api_server.log
echo.
pause
"""

# Write with GBK encoding
with open(os.path.join(SCRIPT_DIR, 'restart.bat'), 'wb') as f:
    f.write(restart_content.encode('gbk'))

with open(os.path.join(SCRIPT_DIR, 'start.bat'), 'wb') as f:
    f.write(start_content.encode('gbk'))

print("脚本生成完成!")
print(f"  restart.bat: {os.path.join(SCRIPT_DIR, 'restart.bat')}")
print(f"  start.bat: {os.path.join(SCRIPT_DIR, 'start.bat')}")
