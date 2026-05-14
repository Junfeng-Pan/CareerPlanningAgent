# 职业规划智能体 - 前端

基于 Vue3 + Element Plus + ECharts 的现代化前端界面

## 技术栈

- **Vue 3** - Composition API
- **Vite** - 构建工具
- **Element Plus** - UI 组件库
- **ECharts 5** - 数据可视化
- **Pinia** - 状态管理
- **Axios** - HTTP 请求

## 功能特性

### 主要功能

1. **智能对话（主界面）**
   - 流式输出回答，实时显示
   - 思考过程可折叠查看
   - 工具调用可视化
   - 快捷提问按钮

2. **简历上传**
   - 支持拖拽上传
   - 支持 .txt / .docx / .pdf 格式
   - 自动解析并提取学生画像

3. **学生画像**
   - 技能雷达图
   - 职业素养/发展潜力进度条
   - 技能、证书、经历列表

4. **岗位分析**
   - 岗位信息输入
   - 常用岗位快捷选择
   - 技能分布柱状图
   - 职业发展路径时间线

5. **人岗匹配**
   - 匹配度仪表图
   - 优势/差距分析
   - 技能匹配饼图
   - 详细匹配表格
   - 发展建议

## 快速开始

### 安装依赖

```bash
cd app/frontend_optimized
npm install
```

### 启动服务

1. 启动后端（在项目根目录）：
```bash
python -m uvicorn app.backend.api_server:app --reload --host 0.0.0.0 --port 8000
```

2. 启动前端（在新终端）：
```bash
npm run dev
```

访问 http://localhost:3000

## 界面布局

```
┌─────────────────────────────────────────────────────────┐
│ 侧边栏 (360px)          │ 主内容区 - 对话界面           │
│ ├─ 状态指示器          │                               │
│ ├─ 功能面板           │  ┌─────────────────────────┐  │
│   - 简历上传          │  │  欢迎屏幕/消息列表     │  │
│   - 学生画像          │  │                         │  │
│   - 岗位分析          │  │  [用户消息]            │  │
│   - 匹配结果          │  │  [AI 回复 (流式)]        │  │
│                       │  │                         │  │
│                       │  └─────────────────────────┘  │
│                       │  [输入框 + 发送按钮]          │
└─────────────────────────────────────────────────────────┘
```

## 文件结构

```
frontend_optimized/
├── index.html
├── package.json
├── vite.config.js
├── src/
│   ├── main.js
│   ├── App.vue
│   ├── router/
│   │   └── index.js
│   ├── services/
│   │   └── api.js      # API 服务层
│   ├── store/
│   │   └── app.js      # Pinia 状态管理
│   ├── components/
│   │   ├── StudentProfileDetail.vue  # 学生画像详情
│   │   ├── JobProfileDetail.vue      # 岗位画像详情
│   │   └── MatchResultDetail.vue     # 匹配结果详情
│   └── views/
│       └── Layout.vue    # 主布局（对话界面）
```

## API 配置

前端通过 Vite 代理连接后端：

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

## 状态管理 (Pinia)

```javascript
const appStore = useAppStore()

// State
appStore.sessionId         // 会话 ID
appStore.hasResume         // 是否已上传简历
appStore.studentProfile    // 学生画像数据
appStore.jobProfile        // 岗位画像数据
appStore.matchResult       // 匹配结果数据
appStore.chatMessages      // 对话历史
appStore.isChatStreaming   // 是否正在流式输出

// Actions
await appStore.uploadResume(file)      // 上传简历
await appStore.sendMessage(message)    // 发送消息（流式）
await appStore.analyzeJob(name, desc)  // 分析岗位
```

## 流式输出

对话使用流式输出，实时显示 AI 回答：

```javascript
// API 服务
async chatStream(message, onEvent) {
  const response = await fetch('/api/chat/stream', { ... })
  const reader = response.body.getReader()
  
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    
    // 解析 NDJSON 格式的事件
    const lines = decoder.decode(value).split('\n')
    for (const line of lines) {
      const event = JSON.parse(line)
      onEvent(event)  // 回调处理
    }
  }
}
```

事件类型：
- `reasoning` - 思考过程
- `answer` - 回答内容（流式）
- `tool_call` - 工具调用
- `tool_result` - 工具结果
- `final_answer` - 最终回答

## 图表组件

使用 ECharts 5 实现：

- **雷达图** - 技能能力展示
- **柱状图** - 技能要求分布
- **饼图** - 技能匹配分布
- **仪表图** - 匹配度展示

## 生产构建

```bash
npm run build
```

输出到 `dist/` 目录

## License

MIT
