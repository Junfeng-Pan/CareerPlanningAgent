#!/bin/bash

echo "============================================"
echo "     职业规划智能体 - 一键启动脚本"
echo "============================================"
echo ""

# 获取项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

echo "[1/4] 检查已运行的服务..."

# 终止后端服务
BACKEND_PID=$(lsof -ti:8000 2>/dev/null)
if [ -n "$BACKEND_PID" ]; then
    echo "  终止后端服务 (PID: $BACKEND_PID)"
    kill -9 $BACKEND_PID 2>/dev/null
else
    echo "  后端服务未运行"
fi

# 终止前端服务
FRONTEND_PID=$(lsof -ti:3000 2>/dev/null)
if [ -n "$FRONTEND_PID" ]; then
    echo "  终止前端服务 (PID: $FRONTEND_PID)"
    kill -9 $FRONTEND_PID 2>/dev/null
fi

echo ""
echo "[2/4] 创建日志目录..."
mkdir -p "$ROOT_DIR/logs"
echo "  日志目录：$ROOT_DIR/logs"

echo ""
echo "[3/4] 启动后端服务..."
cd "$ROOT_DIR"
nohup python app/backend/api_server.py > "$ROOT_DIR/logs/backend.log" 2>&1 &
BACKEND_PID=$!
echo "  后端服务已启动 (PID: $BACKEND_PID)"
echo "  等待后端服务启动..."
sleep 3

echo ""
echo "[4/4] 启动前端服务..."
cd "$ROOT_DIR/app/frontend_optimized"
nohup npm run dev > "$ROOT_DIR/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "  前端服务已启动 (PID: $FRONTEND_PID)"

echo ""
echo "============================================"
echo "     服务启动完成！"
echo "============================================"
echo ""
echo "  后端 API:  http://localhost:8000"
echo "  前端页面：http://localhost:3000"
echo "  日志文件：$ROOT_DIR/logs/api_server.log"
echo ""
echo "============================================"
