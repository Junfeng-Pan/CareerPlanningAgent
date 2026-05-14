# 职业规划智能体 - 前端部署指南

## 项目结构

```
frontend_optimized/
├── index.html              # HTML 入口
├── package.json            # 项目依赖
├── vite.config.js          # Vite 配置
├── src/
│   ├── main.js             # 应用入口
│   ├── App.vue             # 根组件
│   ├── router/
│   │   └── index.js        # 路由配置
│   ├── services/
│   │   └── api.js          # API 服务层
│   ├── store/
│   │   └── app.js          # 状态管理
│   └── views/
│       ├── Layout.vue      # 主布局
│       ├── Home.vue        # 首页
│       ├── StudentProfile.vue  # 学生画像
│       ├── JobAnalysis.vue     # 岗位分析
│       ├── MatchResult.vue     # 人岗匹配
│       └── Chat.vue            # 智能对话
```

## 快速开始

### 1. 安装依赖

```bash
cd app/frontend_optimized
npm install
```

### 2. 启动后端服务

在_project根目录_启动 FastAPI 后端：

```bash
# 返回项目根目录
cd ../..

# 启动后端服务（端口 8000）
python -m uvicorn app.backend.api_server:app --reload --host 0.0.0.0 --port 8000
```

### 3. 启动前端开发服务器

```bash
cd app/frontend_optimized
npm run dev
```

访问 http://localhost:3000

## 功能模块

### 首页 (`/`)
- 欢迎界面和功能导航卡片
- 简历拖拽上传区域
- 当前状态实时展示（简历、学生画像、岗位画像、匹配结果）
- 数据概览卡片

### 学生画像 (`/student-profile`)
- 技能能力雷达图（ECharts）
- 技能详情列表
- 职业素养和发展潜力进度条
- 证书和经历列表

### 岗位分析 (`/job-analysis`)
- 岗位信息输入表单
- 常用岗位快捷选择
- 岗位画像展示（技能、门槛、素养要求）
- 技能要求分布柱状图
- 职业发展路径时间线

### 人岗匹配 (`/match-result`)
- 匹配度总览卡片（仪表图）
- 优势和差距分析
- 技能匹配详情表格
- 技能匹配分布饼图
- 发展建议列表

### 智能对话 (`/chat`)
- 流式对话界面
- 思考过程展示
- 工具调用可视化
- 快速提问按钮
- 对话历史管理

## 技术特性

- **Vue 3 Composition API** - 现代化的组件开发方式
- **Pinia 状态管理** - 轻量级全局状态管理
- **Vue Router** - 前端路由管理
- **Element Plus** - UI 组件库
- **ECharts 5** - 数据可视化图表
- **Axios** - HTTP 请求
- **SCSS** - CSS 预处理器

## API 配置

前端通过 Vite 代理连接到后端 API 服务：

```javascript
// vite.config.js
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

## 生产构建

```bash
npm run build
```

构建产物输出到 `dist/` 目录

## 常见问题

### 后端服务未启动

如果前端无法获取数据，请确保后端服务已启动并运行在 `http://localhost:8000`

### 跨域问题

开发环境通过 Vite 代理解决跨域问题，生产环境需要配置 CORS 或 Nginx 反向代理

### 会话状态丢失

确保后端和前端使用相同的 session_id，上传简历后会自动创建会话

## 下一步优化建议

1. 添加用户认证系统
2. 使用 Redis 存储会话数据（替代内存存储）
3. 添加历史记录功能
4. 支持导出匹配报告（PDF）
5. 添加更多图表类型和数据可视化
6. 支持多语言国际化
