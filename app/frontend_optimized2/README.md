# 前端系统文档

## 快速开始

### 1. 安装 Node.js

本项目需要 Node.js 18+ 版本。请从 [https://nodejs.org](https://nodejs.org) 下载并安装。

### 2. 安装依赖

```bash
cd app/frontend_optimized2
npm install
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 4. 构建生产版本

```bash
npm run build
```

## 功能特性

### 1. 智能对话
- 流式对话支持
- Markdown 格式渲染
- 代码高亮显示
- 对话历史持久化

### 2. 学生画像
- 能力雷达图
- 技能/证书/经历展示
- 职业素养与发展潜力评估

### 3. 岗位画像
- 岗位 JD 分析
- 专业技能要求
- 基础门槛要求
- 职业发展路径

### 4. 人岗匹配
- 匹配度评估
- 雷达图对比
- 技能匹配详情
- 推荐建议

### 5. 主题切换
- 深色/浅色模式
- 主题偏好持久化
- 平滑过渡动画

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ^3.4.0 | 前端框架 |
| Element Plus | ^2.5.0 | UI 组件库 |
| ECharts | ^5.5.0 | 数据可视化 |
| Vue Router | ^4.2.5 | 路由管理 |
| Axios | ^1.6.0 | HTTP 请求 |
| Markdown-it | ^14.1.0 | Markdown 渲染 |

## 项目结构

```
app/frontend_optimized2/
├── src/
│   ├── api/              # API 服务封装
│   │   ├── index.js      # Axios 实例
│   │   └── services.js   # API 端点
│   ├── assets/           # 静态资源
│   │   └── main.css      # 全局样式
│   ├── components/       # 可复用组件
│   ├── router/           # 路由配置
│   ├── views/            # 页面组件
│   │   ├── ChatView.vue        # 对话页面
│   │   ├── StudentProfileView.vue  # 学生画像
│   │   ├── JobProfileView.vue    # 岗位画像
│   │   └── MatchResultView.vue   # 人岗匹配
│   ├── App.vue           # 根组件
│   └── main.js           # 入口文件
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## API 配置

开发环境下，Vite 会自动代理 `/api` 请求到后端服务 `http://localhost:8000`。

如需修改后端地址，编辑 `vite.config.js`：

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://your-backend-url:8000',
      changeOrigin: true
    }
  }
}
```

## 主题系统

项目使用 CSS 变量实现主题切换，支持深色和浅色两种模式。

### 深色模式 (Catppuccin Mocha)
- 背景色：`#11111b`, `#1e1e2e`
- 文字色：`#cdd6f4`
- 主色调：`#89b4fa`

### 浅色模式 (Catppuccin Latte)
- 背景色：`#eff1f5`, `#e6e9ef`
- 文字色：`#4c4f69`
- 主色调：`#1e66f5`

## 开发指南

### 添加新页面

1. 在 `src/views/` 目录下创建新的 Vue 组件
2. 在 `src/router/index.js` 中添加路由配置
3. 在 `App.vue` 的菜单中添加导航项

### 调用新 API

1. 在 `src/api/services.js` 中添加新的 API 方法
2. 在组件中导入并使用

### 样式开发

所有组件使用 scoped CSS，全局样式在 `src/assets/main.css` 中定义。

## 常见问题

### Q: 前端无法连接后端？
A: 确保后端服务已在 `http://localhost:8000` 运行。

### Q: 主题切换后图表颜色不对？
A: ECharts 图表会在主题切换时自动重新初始化，如未更新请刷新页面。

### Q: 对话内容没有 Markdown 格式？
A: AI 回复的内容会自动渲染 Markdown，确保后端返回的是有效的 Markdown 格式。

## 许可证

MIT License
