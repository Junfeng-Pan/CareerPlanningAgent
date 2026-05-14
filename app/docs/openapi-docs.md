# 职业规划智能体 API

_Version: 1.0.0_

## Table of Contents

- [`GET` /](#root-get)
- [`GET` /api/profile/student](#get-student-profile-api-api-profile-student-get)
- [`GET` /api/profile/job](#get-job-profile-api-api-profile-job-get)
- [`GET` /api/match/result](#get-match-result-api-api-match-result-get)
- [`POST` /api/job/analyze](#analyze-job-api-job-analyze-post)
- [`POST` /api/log](#receive-frontend-log-api-log-post)
- [`POST` /api/upload](#upload-resume-api-upload-post)
- [`POST` /api/chat/stream](#chat-stream-api-chat-stream-post)
- [`DELETE` /api/session/{session_id}](#delete-session-api-session-session-id-delete)
- [`GET` /api/session/{session_id}](#get-session-api-session-session-id-get)


## Endpoints

### `/`

#### GET

**Operation ID:** `root__get`
**Summary:** Root

API 根路径

**Responses:**

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |

**Response Examples — `200`**

### `/api/profile/student`

#### GET

**Operation ID:** `get_student_profile_api_api_profile_student_get`
**Summary:** Get Student Profile Api

获取学生画像
- session_id: 可选，指定会话 ID

**Parameters:**

| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `session_id` | query | no |  |  |

**Responses:**

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `422` | Validation Error |

**Response Examples — `200`**

**Response Examples — `422`**

### `/api/profile/job`

#### GET

**Operation ID:** `get_job_profile_api_api_profile_job_get`
**Summary:** Get Job Profile Api

获取岗位画像
- session_id: 可选，指定会话 ID

**Parameters:**

| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `session_id` | query | no |  |  |

**Responses:**

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `422` | Validation Error |

**Response Examples — `200`**

**Response Examples — `422`**

### `/api/match/result`

#### GET

**Operation ID:** `get_match_result_api_api_match_result_get`
**Summary:** Get Match Result Api

获取匹配结果
- session_id: 可选，指定会话 ID

**Parameters:**

| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `session_id` | query | no |  |  |

**Responses:**

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `422` | Validation Error |

**Response Examples — `200`**

**Response Examples — `422`**

### `/api/job/analyze`

#### POST

**Operation ID:** `analyze_job_api_job_analyze_post`
**Summary:** Analyze Job

分析岗位并生成画像和匹配结果
- job_name: 岗位名称
- job_description: 岗位描述（可选）
- session_id: 可选，指定会话 ID

**Parameters:**

| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `session_id` | query | no |  |  |

**Request Body:**

| Media type | Schema |
| ---------- | ------ |
| `application/json` | `#/components/schemas/JobAnalyzeRequest` |

**Responses:**

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `422` | Validation Error |

**Response Examples — `200`**

**Response Examples — `422`**

### `/api/log`

#### POST

**Operation ID:** `receive_frontend_log_api_log_post`
**Summary:** Receive Frontend Log

接收前端日志并写入文件

**Request Body:**

| Media type | Schema |
| ---------- | ------ |
| `application/json` | `#/components/schemas/FrontendLog` |

**Responses:**

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `422` | Validation Error |

**Response Examples — `200`**

**Response Examples — `422`**

### `/api/upload`

#### POST

**Operation ID:** `upload_resume_api_upload_post`
**Summary:** Upload Resume

上传简历文件
- 支持：.txt, .docx, .pdf
- 返回：session_id

**Parameters:**

| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `session_id` | query | no |  |  |

**Request Body:**

| Media type | Schema |
| ---------- | ------ |
| `multipart/form-data` | `#/components/schemas/Body_upload_resume_api_upload_post` |

**Responses:**

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `422` | Validation Error |

**Response Examples — `200`**

**Response Examples — `422`**

### `/api/chat/stream`

#### POST

**Operation ID:** `chat_stream_api_chat_stream_post`
**Summary:** Chat Stream

与智能体对话（流式输出）
返回 NDJSON 格式，每行一个 JSON 对象
事件类型包括：
- reasoning: 思考过程
- answer: 回答内容（流式累加）
- tool_call: 工具调用
- tool_result: 工具返回结果
- final_answer: 最终回答

**Request Body:**

| Media type | Schema |
| ---------- | ------ |
| `application/json` | `#/components/schemas/ChatRequest` |

**Responses:**

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `422` | Validation Error |

**Response Examples — `200`**

**Response Examples — `422`**

### `/api/session/{session_id}`

#### DELETE

**Operation ID:** `delete_session_api_session__session_id__delete`
**Summary:** Delete Session

删除会话

**Parameters:**

| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `session_id` | path | yes | string |  |

**Responses:**

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `422` | Validation Error |

**Response Examples — `200`**

**Response Examples — `422`**

#### GET

**Operation ID:** `get_session_api_session__session_id__get`
**Summary:** Get Session

获取会话状态

**Parameters:**

| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `session_id` | path | yes | string |  |

**Responses:**

| Code | Description |
| ---- | ----------- |
| `200` | Successful Response |
| `422` | Validation Error |

**Response Examples — `200`**

**Response Examples — `422`**

## Schemas

### `Body_upload_resume_api_upload_post`

| Property | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `file` | string | yes |  |

### `ChatRequest`

| Property | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `message` | string | yes |  |
| `session_id` |  | no |  |

### `FrontendLog`

| Property | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `timestamp` | string | yes |  |
| `level` | string | yes |  |
| `message` | string | yes |  |

### `HTTPValidationError`

| Property | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `detail` | array<#/components/schemas/ValidationError> | no |  |

### `JobAnalyzeRequest`

| Property | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `job_name` | string | yes |  |
| `job_description` |  | no |  |

### `UploadResponse`

| Property | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `success` | boolean | yes |  |
| `message` | string | yes |  |
| `session_id` | string | yes |  |

### `ValidationError`

| Property | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `loc` | array<> | yes |  |
| `msg` | string | yes |  |
| `type` | string | yes |  |
| `input` |  | no |  |
| `ctx` | object | no |  |