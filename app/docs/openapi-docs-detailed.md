# 职业规划智能体 API 文档（详细版）

**版本：** 1.0.0  
**基础 URL:** `http://localhost:8000`  
**更新日期：** 2026-04-01

---

## 目录

1. [概述](#概述)
2. [认证与会话管理](#认证与会话管理)
3. [数据模型](#数据模型)
4. [API 端点详解](#api-端点详解)
   - [根端点](#根端点)
   - [简历上传](#简历上传)
   - [学生画像](#学生画像)
   - [岗位画像](#岗位画像)
   - [匹配结果](#匹配结果)
   - [岗位分析](#岗位分析)
   - [流式对话](#流式对话)
   - [前端日志](#前端日志上报)
   - [会话管理](#会话管理)
5. [错误处理](#错误处理)
6. [使用示例](#使用示例)

---

## 概述

职业规划智能体 API 提供基于 AI 的简历分析、人岗匹配和职业规划功能。  
所有 API 均采用 RESTful 风格设计，使用 JSON 格式进行数据交换。

### 核心功能

| 功能 | 说明 |
|------|------|
| 简历上传 | 支持 .txt、.docx、.pdf 格式简历的解析与存储 |
| 学生画像 | 从简历中提取技能、项目经历、实习经历等能力信息 |
| 岗位分析 | 分析岗位 JD，提取岗位要求的技能与能力 |
| 人岗匹配 | 对比学生能力与岗位要求，生成匹配度报告 |
| 智能对话 | 流式对话接口，支持多轮交互与工具调用 |
| 日志监控 | 前端日志上报与后端日志文件，支持调试与问题追踪 |

### 会话机制

本 API 采用 **Session-Based** 架构：
- 每个用户会话由唯一的 `session_id` (UUID) 标识
- 会话数据存储在服务器内存中（生产环境建议使用 Redis）
- 会话数据包括：简历文本、学生画像、岗位画像、匹配结果、对话历史

---

## 认证与会话管理

### 会话 ID 获取方式

```
┌─────────────────────────────────────────────────────────────┐
│ 方式一：上传简历                                            │
│ POST /api/upload → 返回 session_id                          │
│ 适用于：首次使用，需要上传简历的场景                        │
├─────────────────────────────────────────────────────────────┤
│ 方式二：自动创建                                            │
│ 任何带 session_id 的请求，如果 session_id 为空或无效       │
│ 系统会自动创建新会话并返回新的 session_id                   │
├─────────────────────────────────────────────────────────────┤
│ 方式三：显式创建                                            │
│ GET /api/session/{session_id} 可创建空会话                  │
│ 适用于：只需要会话 ID 暂不上传简历的场景                    │
└─────────────────────────────────────────────────────────────┘
```

### 会话生命周期

| 操作 | 说明 |
|------|------|
| 创建 | 上传简历或调用任何需要 session_id 的接口时自动创建 |
| 查询 | `GET /api/session/{session_id}` 查看会话状态 |
| 删除 | `DELETE /api/session/{session_id}` 手动删除会话 |
| 过期 | 当前版本不会自动过期，需手动删除（建议生产环境添加 TTL） |

---

## 数据模型

### 学生画像 (StudentProfile)

```json
{
  "name": "张三",
  "education": {
    "university": "某某大学",
    "degree": "本科",
    "major": "计算机科学与技术",
    "graduation_year": "2025"
  },
  "skills": [
    {
      "name": "Python",
      "proficiency": "熟练",
      "evidence": "使用 Python 完成了 XX 项目，实现了 XX 功能"
    }
  ],
  "projects": [
    {
      "name": "项目名称",
      "description": "项目描述",
      "role": "后端开发",
      "technologies": ["Python", "FastAPI", "MySQL"]
    }
  ],
  "internships": [
    {
      "company": "公司名称",
      "position": "实习岗位",
      "duration": "2024.06-2024.09",
      "description": "工作内容描述"
    }
  ]
}
```

### 岗位画像 (JobProfile)

```json
{
  "name": "Java 开发工程师",
  "company": "公司名称（如有）",
  "skills": [
    {
      "name": "Java",
      "required_level": "精通",
      "description": "5 年以上 Java 开发经验"
    },
    {
      "name": "Spring Boot",
      "required_level": "熟练",
      "description": "熟悉 Spring Boot 框架"
    }
  ],
  "requirements": [
    "计算机相关专业本科及以上学历",
    "熟悉 MySQL 数据库"
  ],
  "responsibilities": [
    "负责后端服务开发",
    "参与系统架构设计"
  ]
}
```

### 匹配结果 (MatchResult)

```json
{
  "summary": {
    "matching_degree": "高",
    "summary": "该学生具备岗位所需的大部分核心技能，匹配度较高",
    "advantages": ["具备 Java 开发经验", "有相关项目经历"],
    "gaps": ["缺少微服务经验", "没有大厂实习经历"]
  },
  "skills": [
    {
      "name": "Java",
      "required": true,
      "status": "具备",
      "student_evidence": "在 XX 项目中使用 Java 开发",
      "gap_analysis": ""
    },
    {
      "name": "Kubernetes",
      "required": true,
      "status": "缺失",
      "student_evidence": "",
      "gap_analysis": "岗位要求熟悉 K8s，但学生简历中未提及相关经验"
    }
  ],
  "recommendations": [
    "建议学习 Kubernetes 相关知识",
    "可以补充微服务项目经历"
  ]
}
```

---

## API 端点详解

### 1. 根路径

#### `GET /`

获取 API 基本信息和可用端点列表。

**请求参数：** 无

**响应示例 (200 OK):**
```json
{
  "name": "职业规划智能体 API",
  "version": "1.0.0",
  "description": "提供简历分析、人岗匹配、职业规划功能",
  "endpoints": {
    "POST /api/upload": "上传简历文件",
    "POST /api/chat/stream": "与智能体对话（流式输出）",
    "POST /api/log": "上报前端日志",
    "GET /api/profile/student": "获取学生画像",
    "GET /api/profile/job": "获取岗位画像",
    "GET /api/match/result": "获取匹配结果",
    "POST /api/job/analyze": "分析岗位并生成画像和匹配结果",
    "GET /api/session/{session_id}": "获取会话状态",
    "DELETE /api/session/{session_id}": "删除会话"
  }
}
```

---

### 2. 简历上传

#### `POST /api/upload`

上传简历文件，系统会自动解析并提取学生画像。

**支持格式:** `.txt`, `.docx`, `.pdf`

**请求参数:**

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| `file` | formData | File | 是 | 简历文件 |
| `session_id` | query | string | 否 | 会话 ID，不提供则自动创建新会话 |

**请求示例:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@resume.pdf"
```

**响应示例 (200 OK):**
```json
{
  "success": true,
  "message": "简历上传成功",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**错误响应:**

| 状态码 | 说明 |
|--------|------|
| 400 | 无法读取简历文件（格式不支持或文件损坏） |
| 422 | 请求参数验证失败 |

**后端处理流程:**
```
1. 接收文件 → 2. 保存临时文件 → 3. 根据扩展名选择解析器
→ 4. 提取文本内容 → 5. 调用 LLM 提取学生画像 → 6. 保存至会话
→ 7. 清理临时文件 → 8. 返回 session_id
```

---

### 3. 学生画像

#### `GET /api/profile/student`

获取当前会话的学生画像数据。

**请求参数:**

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| `session_id` | query | string | 否 | 会话 ID |

**请求示例:**
```bash
curl "http://localhost:8000/api/profile/student?session_id=550e8400-e29b-41d4-a716-446655440000"
```

**响应示例 (200 OK):**
```json
{
  "student_profile": {
    "name": "张三",
    "education": {
      "university": "某某大学",
      "degree": "本科",
      "major": "计算机科学与技术",
      "graduation_year": "2025"
    },
    "skills": [
      {
        "name": "Python",
        "proficiency": "熟练",
        "evidence": "使用 Python 完成了在线商城项目"
      }
    ]
  }
}
```

**响应示例 - 无数据 (200 OK):**
```json
{
  "student_profile": null,
  "message": "学生画像不存在"
}
```

**错误响应:**

| 状态码 | 说明 |
|--------|------|
| 404 | 会话不存在（当提供无效 session_id 时） |

**使用场景:**
- 用户点击"查看学生画像"按钮时调用
- 在对话前预加载用户信息
- 生成报告时获取基础数据

---

### 4. 岗位画像

#### `GET /api/profile/job`

获取当前会话的岗位画像数据。

**请求参数:**

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| `session_id` | query | string | 否 | 会话 ID |

**请求示例:**
```bash
curl "http://localhost:8000/api/profile/job?session_id=550e8400-e29b-41d4-a716-446655440000"
```

**响应示例 (200 OK):**
```json
{
  "job_profile": {
    "name": "Java 开发工程师",
    "skills": [
      {
        "name": "Java",
        "required_level": "精通",
        "description": "5 年以上 Java 开发经验"
      }
    ],
    "requirements": ["计算机相关专业本科及以上学历"],
    "responsibilities": ["负责后端服务开发"]
  }
}
```

**响应示例 - 无数据 (200 OK):**
```json
{
  "job_profile": null,
  "message": "岗位画像不存在"
}
```

**注意:** 岗位画像不会自动生成，需要先调用 `POST /api/job/analyze` 进行分析。

---

### 5. 匹配结果

#### `GET /api/match/result`

获取当前会话的人岗匹配结果。

**请求参数:**

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| `session_id` | query | string | 否 | 会话 ID |

**请求示例:**
```bash
curl "http://localhost:8000/api/match/result?session_id=550e8400-e29b-41d4-a716-446655440000"
```

**响应示例 (200 OK):**
```json
{
  "match_result": {
    "summary": {
      "matching_degree": "高",
      "summary": "该学生具备岗位所需的大部分核心技能",
      "advantages": ["具备 Java 开发经验"],
      "gaps": ["缺少微服务经验"]
    },
    "skills": [
      {
        "name": "Java",
        "required": true,
        "status": "具备",
        "student_evidence": "在 XX 项目中使用 Java"
      }
    ],
    "recommendations": ["建议学习 Kubernetes"]
  }
}
```

**响应示例 - 无数据 (200 OK):**
```json
{
  "match_result": null,
  "message": "匹配结果不存在"
}
```

**注意:** 匹配结果需要先有学生画像和岗位画像才能生成。

---

### 6. 岗位分析

#### `POST /api/job/analyze`

分析岗位描述，生成岗位画像并与学生画像进行匹配。

**请求参数:**

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| `session_id` | query | string | 否 | 会话 ID |

**请求体 (JSON):**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `job_name` | string | 是 | 岗位名称 |
| `job_description` | string | 否 | 岗位描述（JD） |

**请求示例:**
```bash
curl -X POST "http://localhost:8000/api/job/analyze?session_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "Java 开发工程师",
    "job_description": "负责 Java 后端开发，熟悉 Spring Boot、MySQL、Redis 等"
  }'
```

**响应示例 (200 OK):**
```json
{
  "success": true,
  "job_profile": {
    "name": "Java 开发工程师",
    "skills": [
      {"name": "Java", "required_level": "精通"},
      {"name": "Spring Boot", "required_level": "熟练"}
    ]
  },
  "match_result": {
    "summary": {
      "matching_degree": "中",
      "summary": "学生具备基础技能，但缺乏高级特性经验"
    },
    "skills": [...]
  }
}
```

**响应示例 - 失败 (200 OK):**
```json
{
  "success": false,
  "error": "LLM 服务连接失败"
}
```

**处理流程:**
```
1. 接收岗位信息 → 2. 调用 LLM 分析 JD 提取岗位要求
→ 3. 生成岗位画像 → 4. 获取学生画像 → 5. 对比分析生成匹配结果
→ 6. 保存至会话 → 7. 返回岗位画像和匹配结果
```

**超时建议:** LLM 分析可能需要 30-60 秒，建议客户端设置超时时间 ≥ 120 秒。

---

### 7. 流式对话

#### `POST /api/chat/stream`

与智能体进行流式对话，支持实时输出思考过程和回答。

**请求体 (JSON):**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message` | string | 是 | 用户消息 |
| `session_id` | string | 否 | 会话 ID |

**请求示例:**
```bash
curl -X POST "http://localhost:8000/api/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"message": "我想了解 Java 开发工程师的要求", "session_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

**响应格式:** NDJSON (Newline Delimited JSON)

每行一个 JSON 对象，事件类型如下：

| 事件类型 | 说明 | 数据字段 |
|----------|------|----------|
| `reasoning` | 思考过程 | `content`: 思考内容 |
| `answer` | 回答内容（流式） | `content`: 回答片段 |
| `tool_call` | 工具调用 | `name`: 工具名，`args`: 参数 |
| `tool_result` | 工具结果 | `name`: 工具名，`result`: 结果摘要 |
| `tool_error` | 工具错误 | `name`: 工具名，`error`: 错误信息 |
| `final_answer` | 最终回答 | `content`: 完整回答 |

**响应示例:**
```json
{"type": "reasoning", "content": "用户想了解 Java 工程师岗位..."}
{"type": "answer", "content": "Java 开发工程师通常需要具备"}
{"type": "answer", "content": "以下技能："}
{"type": "tool_call", "name": "get_student_profile", "args": {}}
{"type": "tool_result", "name": "get_student_profile", "result": "..."}
{"type": "final_answer", "content": "根据您的背景，Java 工程师岗位..."}
```

**前端处理示例 (JavaScript):**
```javascript
const response = await fetch('/api/chat/stream', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: '你好', session_id: 'xxx'})
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const {value, done} = await reader.read();
  if (done) break;
  
  const lines = decoder.decode(value).split('\n');
  for (const line of lines) {
    if (line.trim()) {
      const event = JSON.parse(line);
      if (event.type === 'reasoning') {
        // 显示思考过程
      } else if (event.type === 'answer') {
        // 流式显示回答
      }
    }
  }
}
```

**超时建议:** 对话可能涉及多次 LLM 调用，建议设置超时时间 ≥ 120 秒。

---

### 8. 前端日志上报

#### `POST /api/log`

接收前端应用发送的日志信息，并写入服务器日志文件。

**请求体 (JSON):**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `timestamp` | string | 是 | 日志时间戳（ISO 8601 格式） |
| `level` | string | 是 | 日志级别：`INFO`, `WARN`, `ERROR` |
| `message` | string | 是 | 日志消息内容 |

**请求示例:**
```bash
curl -X POST "http://localhost:8000/api/log" \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "2026-04-02T14:30:00Z", "level": "ERROR", "message": "Upload failed: network error"}'
```

**响应示例 (200 OK):**
```json
{
  "success": true
}
```

**日志文件位置:**
- 前端日志：`logs/frontend.log`
- 后端日志：`logs/api_server.log`

**后端处理流程:**
```
1. 接收日志请求 → 2. 验证请求格式 → 3. 写入 frontend.log
→ 4. 返回成功响应
```

**前端集成示例 (JavaScript):**
```javascript
// 发送日志到后端
function sendLog(level, message) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    level: level,
    message: message
  };
  
  // 使用 sendBeacon 确保日志在页面卸载时也能发送
  navigator.sendBeacon('/api/log', JSON.stringify(logEntry));
}

// 拦截 console.error
const originalError = console.error;
console.error = (...args) => {
  originalError(...args);
  sendLog('ERROR', args.join(' '));
};
```

---

### 9. 会话管理

#### `GET /api/session/{session_id}`

获取会话的完整状态信息。

**请求参数:**

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| `session_id` | path | string | 是 | 会话 ID |

**请求示例:**
```bash
curl "http://localhost:8000/api/session/550e8400-e29b-41d4-a716-446655440000"
```

**响应示例 (200 OK):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "has_resume": true,
  "has_student_profile": true,
  "has_job_profile": true,
  "has_match_result": true,
  "student_profile": {...},
  "job_profile": {...},
  "match_result": {...}
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| `session_id` | string | 会话 ID |
| `has_resume` | boolean | 是否已上传简历 |
| `has_student_profile` | boolean | 是否有学生画像 |
| `has_job_profile` | boolean | 是否有岗位画像 |
| `has_match_result` | boolean | 是否有匹配结果 |
| `student_profile` | object | 学生画像数据（完整） |
| `job_profile` | object | 岗位画像数据（完整） |
| `match_result` | object | 匹配结果数据（完整） |

**错误响应 (404 Not Found):**
```json
{
  "detail": "会话不存在"
}
```

---

#### `DELETE /api/session/{session_id}`

删除指定会话，释放服务器资源。

**请求参数:**

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| `session_id` | path | string | 是 | 会话 ID |

**请求示例:**
```bash
curl -X DELETE "http://localhost:8000/api/session/550e8400-e29b-41d4-a716-446655440000"
```

**响应示例 (200 OK):**
```json
{
  "message": "会话 550e8400-e29b-41d4-a716-446655440000 已删除"
}
```

**错误响应 (404 Not Found):**
```json
{
  "detail": "会话不存在"
}
```

---

### 9. 前端日志上报

#### `POST /api/log`

接收前端应用发送的日志信息，并写入服务器日志文件。

**请求体 (JSON):**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `timestamp` | string | 是 | 日志时间戳（ISO 8601 格式） |
| `level` | string | 是 | 日志级别：`INFO`, `WARN`, `ERROR` |
| `message` | string | 是 | 日志消息内容 |

**请求示例:**
```bash
curl -X POST "http://localhost:8000/api/log" \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "2026-04-02T14:30:00Z", "level": "ERROR", "message": "Upload failed: network error"}'
```

**响应示例 (200 OK):**
```json
{
  "success": true
}
```

**日志文件位置:**
- 前端日志：`logs/frontend.log`
- 后端日志：`logs/api_server.log`

**前端集成示例 (JavaScript):**
```javascript
// 发送日志到后端
function sendLog(level, message) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    level: level,
    message: message
  };
  
  // 使用 sendBeacon 确保日志在页面卸载时也能发送
  navigator.sendBeacon('/api/log', JSON.stringify(logEntry));
}

// 拦截 console.error
const originalError = console.error;
console.error = (...args) => {
  originalError(...args);
  sendLog('ERROR', args.join(' '));
};
```

---

## 错误处理

### HTTP 状态码

| 状态码 | 说明 | 处理建议 |
|--------|------|----------|
| 200 | 请求成功 | 检查响应数据 |
| 400 | 请求参数错误 | 检查上传的文件格式 |
| 404 | 资源不存在 | 检查 session_id 是否正确 |
| 422 | 请求体验证失败 | 检查 JSON 格式和必填字段 |
| 500 | 服务器内部错误 | 查看服务器日志（logs/api_server.log, logs/frontend.log） |
| 503 | 服务不可用 | 检查 LLM 服务连接 |

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

### 验证错误响应 (422)

```json
{
  "detail": [
    {
      "loc": ["body", "job_name"],
      "msg": "field required",
      "type": "value_error.missing",
      "input": {"other_field": "..."}
    }
  ]
}
```

---

## 使用示例

### 完整使用流程

#### 步骤 1: 上传简历

```bash
# 上传简历并获取 session_id
UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/upload" \
  -F "file=@resume.pdf")

SESSION_ID=$(echo $UPLOAD_RESPONSE | jq -r '.session_id')
echo "Session ID: $SESSION_ID"
```

#### 步骤 2: 查看学生画像

```bash
# 获取学生画像
curl "http://localhost:8000/api/profile/student?session_id=$SESSION_ID" \
  | jq '.student_profile'
```

#### 步骤 3: 分析岗位

```bash
# 分析目标岗位
curl -X POST "http://localhost:8000/api/job/analyze?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "Python 开发工程师",
    "job_description": "负责 Python 后端开发，熟悉 FastAPI、Django、MySQL"
  }' | jq '.'
```

#### 步骤 4: 查看匹配结果

```bash
# 获取匹配结果
curl "http://localhost:8000/api/match/result?session_id=$SESSION_ID" \
  | jq '.match_result.summary'
```

#### 步骤 5: 与智能体对话

```bash
# 流式对话
curl -X POST "http://localhost:8000/api/chat/stream" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"根据我的背景，我适合这个岗位吗？\", \"session_id\": \"$SESSION_ID\"}"
```

#### 步骤 6: 清理会话（可选）

```bash
# 删除会话
curl -X DELETE "http://localhost:8000/api/session/$SESSION_ID"
```

### Python 示例

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 上传简历
with open("resume.pdf", "rb") as f:
    response = requests.post(f"{BASE_URL}/api/upload", files={"file": f})
    session_id = response.json()["session_id"]

# 2. 获取学生画像
response = requests.get(
    f"{BASE_URL}/api/profile/student",
    params={"session_id": session_id}
)
student_profile = response.json()["student_profile"]
print(f"学生姓名：{student_profile['name']}")

# 3. 分析岗位
response = requests.post(
    f"{BASE_URL}/api/job/analyze",
    params={"session_id": session_id},
    json={
        "job_name": "Python 开发工程师",
        "job_description": "负责 Python 后端开发"
    }
)
if response.json()["success"]:
    match_result = response.json()["match_result"]
    print(f"匹配度：{match_result['summary']['matching_degree']}")

# 4. 流式对话
response = requests.post(
    f"{BASE_URL}/api/chat/stream",
    json={"message": "你好", "session_id": session_id},
    stream=True
)
for line in response.iter_lines():
    if line:
        event = eval(line.decode('utf-8'))  # 或使用 json.loads()
        if event["type"] == "final_answer":
            print(f"AI: {event['content']}")
```

---

## 附录

### 支持的文件格式

| 扩展名 | 类型 | 说明 |
|--------|------|------|
| `.txt` | 文本文件 | UTF-8 编码的纯文本简历 |
| `.docx` | Word 文档 | Microsoft Word 2007+ 格式 |
| `.pdf` | PDF 文档 | 文本型 PDF（非扫描件效果更佳） |

### LLM 配置

智能体使用以下 LLM 配置：

| 配置项 | 值 |
|--------|-----|
| 模型 | qwen3.5-plus |
| 功能 | 学生画像提取、岗位分析、匹配评估、对话生成 |

### 性能建议

| 场景 | 建议 |
|------|------|
| 简历上传 | < 5MB，解析耗时约 5-10 秒 |
| 岗位分析 | JD 长度建议 < 5000 字，耗时约 30-60 秒 |
| 流式对话 | 建议实现超时重试机制 |
| 并发请求 | 单 session 不支持并发，多用户使用不同 session |

---

**文档结束**
