# 职业规划智能体 - 应用目录说明

## 目录结构

```
app/
├── backend/          # FastAPI 后端服务
│   ├── __init__.py
│   └── api_server.py # API 服务器主文件
└── frontend/         # Streamlit 前端应用
    ├── __init__.py
    └── app.py        # Streamlit 应用主文件
```

## 启动方式

### 后端 API 服务器

**推荐方式：**
```bash
python -m app.backend.api_server
```

**兼容方式（项目根目录）：**
```bash
python api_server.py
```

后端提供以下 API 端点：
- `GET /` - API 根路径
- `POST /api/upload` - 上传简历
- `POST /api/chat` - 普通对话
- `POST /api/chat/stream` - 流式对话（支持思考过程输出）
- `GET /api/session/{session_id}` - 获取会话状态
- `DELETE /api/session/{session_id}` - 删除会话

### 前端 Streamlit 应用

**推荐方式：**
```bash
streamlit run app/frontend/app.py
```

**兼容方式（项目根目录）：**
```bash
python app.py
```

## 新功能说明

### 1. 无简历对话支持
智能体现在支持在不上传简历的情况下进行对话。当用户没有上传简历时：
- 可以进行正常对话
- 可以查询岗位画像和基本要求
- 会适时提示用户上传简历以获取更精准的人岗匹配分析

### 2. 流式输出支持
后端新增 `/api/chat/stream` 端点，支持实时流式输出：
- **思考过程** (`type: reasoning`) - 智能体的思考内容
- **回答内容** (`type: answer`) - 智能体的实时回复
- **工具调用** (`type: tool_call`) - 调用的工具名称和参数
- **工具结果** (`type: tool_result`) - 工具返回的结果
- **最终答案** (`type: final_answer`) - 综合所有信息后的最终回复

流式输出采用 NDJSON 格式，每行一个 JSON 对象。

## 测试

### 测试后端 API
```bash
python tests/test_api.py
```

### 测试流式输出
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "我想了解 Java 开发工程师岗位", "session_id": null}'
```

## 迁移说明

原有的 `api_server.py` 和 `app.py` 文件保留在项目根目录作为兼容入口，
它们会导入新位置的代码。建议未来使用新的目录结构。
