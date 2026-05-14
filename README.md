# CareerPlanningAgent 职业规划智能体系统

CareerPlanningAgent 是一个基于 **Single Agent + Tools (ReAct)** 架构构建的职业规划助手。它利用大模型的推理与决策能力，通过调用多个专家工具，为用户提供简历分析、岗位画像检索及人岗匹配建议。

## 🎨 全新前端界面 (v2.0)

本项目现已配备全新的现代化前端界面，采用 **Vue 3 + Element Plus + ECharts** 技术栈构建。

![前端界面](./app/docs/前端设计需求.txt)

### 核心功能

| 功能模块 | 说明 |
|---------|------|
| **智能对话** | 与 Agent 进行流式对话，支持简历文件上传，markdown 格式渲染 |
| **学生画像** | 可视化展示学生能力画像，包含雷达图分析、技能/证书/经历展示 |
| **岗位画像** | 展示目标岗位画像，支持岗位 JD 分析，职业发展路径展示 |
| **人岗匹配** | 智能匹配结果展示，雷达图对比、技能匹配详情、推荐建议 |

### 技术特性

- **深色/浅色模式切换** - 支持主题切换，保护用户视力
- **实时流式对话** - Token 级流式输出，支持思考过程可见
- **Markdown 渲染** - AI 回复支持代码高亮、表格、列表等格式化输出
- **对话历史持久化** - 基于 sessionStorage 保存对话记录
- **响应式设计** - 适配不同屏幕尺寸

### 快速启动前端

```bash
# 方式一：使用启动脚本 (Windows)
scripts\start_all.ps1

# 方式二：手动启动
cd app/frontend_optimized2
npm install
npm run dev
```

访问 http://localhost:3000 即可使用前端界面。

---

## 🌟 后端核心特性

- **ReAct 推理循环**：主智能体采用"思考 - 行动 - 观察" (Thought-Action-Observation) 循环，自主规划任务路径。
- **三级岗位画像检索**：
  1. **Tier 1 (MySQL)**: 优先检索已人工审核或批量生成的画像特征。
  2. **Tier 2 (RAG)**: 在 9000+ 岗位知识库中基于向量相似度进行实时检索。
  3. **Tier 3 (LLM)**: 若前两级均未命中，则利用 LLM 的通用行业知识生成基准画像。
- **Agentic RAG**：主智能体可主动检索职业规划知识库，获取面试技巧、行业趋势等通用建议。
- **流式实时反馈**：所有专家工具调用及主智能体思考过程均支持 Token 级的流式输出。

## 📂 项目结构

```text
CareerPlanningAgent/
├── app/
│   ├── frontend_optimized2/    # Vue 3 前端应用
│   └── backend/                # FastAPI 后端服务
├── database/                   # 统一数据存储层 (MySQL & KnowledgeBase)
├── main_agent/                 # 主智能体逻辑 (ReAct 工作流、工具定义)
├── job_system/                 # 岗位画像专家服务
├── matching_engine/            # 人岗匹配算法服务
├── studentprofile_agent/       # 学生简历分析服务
├── data/                       # 持久化数据 (ChromaDB, SQLite)
├── config/                     # 配置文件
├── scripts/                    # 启动/重启脚本
└── tests/                      # 全流程与单元测试
```

## 🛠️ 环境搭建

### 1. 安装依赖

```bash
# 使用 uv 安装 (推荐)
uv pip install -e .

# 或使用 pip
pip install -e .
```

### 2. 配置环境变量

在根目录下创建 `.env` 文件，配置如下参数：

```env
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_MODEL_NAME=qwen3.5-plus
```

### 3. 数据库初始化

- 执行 `database/mysql/init_db.sql` 初始化 MySQL 表结构
- 运行 `database/knowledgebase/rag_service.py` 初始化向量知识库

## 🚀 快速开始

### 方式一：使用启动脚本 (推荐)

```bash
# Windows PowerShell
scripts\start_all.ps1

# Linux/Mac
./scripts/start_all.sh
```

### 方式二：手动启动

```bash
# 终端 1 - 启动后端
python app/backend/api_server.py

# 终端 2 - 启动前端
cd app/frontend_optimized2
npm run dev
```

### 方式三：运行测试脚本

```bash
python tests/test_main_agent.py
```

## 📡 API 文档

后端 API 采用 RESTful 风格设计，主要端点如下：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/upload` | POST | 上传简历文件 |
| `/api/profile/student` | GET | 获取学生画像 |
| `/api/profile/job` | GET | 获取岗位画像 |
| `/api/match/result` | GET | 获取匹配结果 |
| `/api/job/analyze` | POST | 分析岗位 JD |
| `/api/chat/stream` | POST | 流式对话 |
| `/api/session/{id}` | GET/DELETE | 会话管理 |

详细 API 文档请查看 `app/docs/openapi-docs.md`。

## 🔧 开发工具

### 启动脚本

| 脚本 | 功能 | 平台 |
|------|------|------|
| `start_all.ps1` | 一键启动前后端 | Windows PowerShell |
| `restart_all.ps1` | 一键重启前后端 | Windows PowerShell |
| `start_all.sh` | 启动/重启服务 | Linux/Mac/WSL |

### 依赖管理

```bash
# 更新依赖
pip install --upgrade -r requirements.txt

# 导出当前依赖
pip freeze > requirements.txt
```

## 📝 工作总结

- ✅ 已完成前端系统开发 (Vue 3 + Element Plus + ECharts)
- ✅ 已实现深色/浅色主题切换
- ✅ 已实现 Markdown 渲染和代码高亮
- ✅ 已实现对话历史持久化
- ✅ 已实现上传进度动画
- ✅ 已实现雷达图可视化
- ⚠️ 三个子模块（学生能力建模、岗位画像、人岗匹配）需要重新设计
- ⚠️ 职业规划、路径规划系统还没有实现
- ⚠️ 主智能体和岗位画像专家所需的知识库和数据库没有配置

## 📄 许可证

MIT License

## 🔗 相关链接

- [学生能力建模专家](https://github.com/Junfeng-Pan/studentprofile-agent.git)
- [岗位建模专家](https://github.com/Junfeng-Pan/job-system.git)
- [人岗匹配专家](https://github.com/Junfeng-Pan/matching_engine.git)
