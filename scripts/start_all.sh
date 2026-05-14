#!/bin/bash

# 职业规划智能体 - 启动/重启脚本 (Linux/Mac/WSL)
# 用法：./start_all.sh [start|restart]

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/app/frontend_optimized2"
LOGS_DIR="$ROOT_DIR/logs"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查端口是否被占用
is_port_used() {
    local port=$1
    if command -v lsof &> /dev/null; then
        lsof -i :$port &> /dev/null
    elif command -v netstat &> /dev/null; then
        netstat -tuln | grep -q ":$port "
    else
        ss -tuln | grep -q ":$port "
    fi
}

# 停止指定端口的进程
stop_port() {
    local port=$1
    local name=$2

    if is_port_used $port; then
        print_info "停止 $name (端口 $port)..."
        if command -v lsof &> /dev/null; then
            lsof -ti :$port | xargs kill -9 2>/dev/null || true
        elif command -v fuser &> /dev/null; then
            fuser -k $port/tcp 2>/dev/null || true
        else
            print_warning "无法自动停止端口 $port，请手动处理"
        fi
    else
        print_info "$name 未运行"
    fi
}

# 主函数
main() {
    local action="${1:-start}"

    echo ""
    echo "============================================"
    echo "    Career Planning Agent"
    echo "    职业规划智能体 - 服务管理"
    echo "============================================"
    echo ""

    if [ "$action" == "restart" ]; then
        print_info "模式：重启服务"

        # 停止服务
        stop_port 8000 "后端服务"
        stop_port 3000 "前端服务"

        print_info "等待端口释放..."
        sleep 2

        # 清理日志
        if [ -d "$LOGS_DIR" ]; then
            rm -f "$LOGS_DIR/api_server.log"
            print_success "日志已清理"
        fi
    else
        print_info "模式：启动服务"

        # 检查是否已运行
        if is_port_used 8000; then
            print_warning "后端服务已在运行，是否先停止？(y/n)"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                stop_port 8000 "后端服务"
            else
                print_error "后端端口 8000 已被占用，请先停止现有服务"
                exit 1
            fi
        fi

        if is_port_used 3000; then
            print_warning "前端服务已在运行，是否先停止？(y/n)"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                stop_port 3000 "前端服务"
            else
                print_error "前端端口 3000 已被占用，请先停止现有服务"
                exit 1
            fi
        fi
    fi

    # 创建日志目录
    mkdir -p "$LOGS_DIR"
    print_success "日志目录：$LOGS_DIR"

    # 检查前端依赖
    cd "$FRONTEND_DIR"
    if [ ! -d "node_modules" ]; then
        print_info "安装前端依赖..."
        npm install
    else
        print_info "前端依赖已存在"
    fi

    echo ""
    print_info "启动服务..."

    # 启动后端
    cd "$ROOT_DIR"
    print_info "启动后端服务..."
    python app/backend/api_server.py > "$LOGS_DIR/api_server.log" 2>&1 &
    BACKEND_PID=$!
    sleep 3

    # 检查后端是否启动成功
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_error "后端启动失败，查看日志：$LOGS_DIR/api_server.log"
        exit 1
    fi
    print_success "后端已启动 (PID: $BACKEND_PID)"

    # 启动前端
    cd "$FRONTEND_DIR"
    print_info "启动前端服务..."
    npm run dev > "$LOGS_DIR/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    sleep 2

    # 检查前端是否启动成功
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_error "前端启动失败，查看日志：$LOGS_DIR/frontend.log"
        exit 1
    fi
    print_success "前端已启动 (PID: $FRONTEND_PID)"

    echo ""
    echo "============================================"
    echo "    服务已${action}!"
    echo "============================================"
    echo ""
    echo "  后端 API:   http://localhost:8000"
    echo "  前端页面：http://localhost:3000"
    echo "  日志文件：$LOGS_DIR/api_server.log"
    echo ""
    echo "停止服务命令:"
    echo "  kill $BACKEND_PID  # 停止后端"
    echo "  kill $FRONTEND_PID # 停止前端"
    echo ""
}

# 显示帮助
show_help() {
    echo "用法：$0 [start|restart]"
    echo ""
    echo "参数:"
    echo "  start   启动服务 (默认)"
    echo "  restart 重启服务（先停止再启动）"
    echo ""
    echo "示例:"
    echo "  $0          # 启动服务"
    echo "  $0 start    # 启动服务"
    echo "  $0 restart  # 重启服务"
}

# 处理参数
case "${1:-start}" in
    start|restart)
        main "$1"
        ;;
    -h|--help|help)
        show_help
        ;;
    *)
        print_error "未知参数：$1"
        show_help
        exit 1
        ;;
esac
