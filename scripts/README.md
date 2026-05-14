# Startup Scripts / 启动脚本

## 快速开始 / Quick Start

### Windows PowerShell (推荐)

```powershell
# 启动服务
.\start_all.ps1

# 重启服务
.\restart_all.ps1
```

如果遇到执行策略限制，运行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Windows 批处理文件

```cmd
:: 启动服务
cmd /c scripts\start_all.bat

:: 重启服务
cmd /c scripts\restart_all.bat
```

### Linux/Mac/WSL Shell 脚本

```bash
# 启动服务
./scripts/start_all.sh

# 重启服务
./scripts/start_all.sh restart
```

### Python 脚本 (跨平台)

```bash
# 启动服务
python scripts/start.py

# 重启服务
python scripts/restart.py
```

---

## 脚本说明 / Scripts Description

| 脚本文件 | 功能 | 平台 |
|---------|------|------|
| `start_all.ps1` | 一键启动前后端服务 | Windows (PowerShell) |
| `restart_all.ps1` | 一键重启前后端服务 | Windows (PowerShell) |
| `start_all.bat` | 一键启动前后端服务 | Windows (cmd) |
| `restart_all.bat` | 一键重启前后端服务 | Windows (cmd) |
| `start_all.sh` | 启动/重启服务 | Linux/Mac/WSL |
| `start.py` | 启动服务 (Python) | 跨平台 |
| `restart.py` | 重启服务 (Python) | 跨平台 |

---

## 服务地址 / Service URLs

启动后：
- **后端 API (Backend):** http://localhost:8000
- **前端页面 (Frontend):** http://localhost:3000
- **日志文件 (Log file):** `logs/api_server.log`

---

## 手动启动 / Manual Start

如果脚本无法工作，可以手动启动：

```bash
# 终端 1 - 后端
cd D:\pythonP\Professional_workplace\CareerPlanningAgent
python app/backend/api_server.py

# 终端 2 - 前端
cd D:\pythonP\Professional_workplace\CareerPlanningAgent\app\frontend_optimized2
npm run dev
```

---

## 故障排除 / Troubleshooting

### PowerShell 脚本无法执行

如果遇到执行策略错误：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 端口被占用 / Port already in use

**Windows:**
```powershell
# 查找占用端口的进程
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess

# 停止进程
Stop-Process -Id <PID> -Force
```

**Linux/Mac:**
```bash
# 查找占用端口的进程
lsof -i :8000

# 停止进程
kill -9 $(lsof -t -i :8000)
```

### 脚本显示乱码 / Scripts show garbled text

- 使用 PowerShell 脚本 (`.ps1` 文件) 而不是批处理文件
- 或使用 Python 脚本

### 前端依赖缺失 / Frontend dependencies missing

```bash
cd app/frontend_optimized2
npm install
```

---

## 前端目录说明 / Frontend Directory

当前使用的前端目录是 `app/frontend_optimized2`，采用 Vue 3 + Element Plus + ECharts 构建。

旧目录 `app/frontend_optimized` 已废弃。
