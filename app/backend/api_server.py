"""
职业规划智能体 - FastAPI 后端服务
提供 REST API 用于智能体交互
"""
import os
import sys
import json
import logging
from pathlib import Path

# 配置日志
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 配置日志格式
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 文件处理器
file_handler = logging.FileHandler(LOG_DIR / "api_server.log", encoding='utf-8')
file_handler.setFormatter(log_format)
file_handler.setLevel(logging.DEBUG)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
console_handler.setLevel(logging.INFO)

# 配置根日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 设置环境变量以支持 UTF-8 输出
os.environ['PYTHONUTF8'] = '1'

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid

# 确保项目根目录在 sys.path 中
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from studentprofile_agent.utils.file_reader import read_word, read_pdf
from main_agent.workflow import create_workflow
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

app = FastAPI(title="职业规划智能体 API", version="1.0.0")

# 启用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"收到请求：{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"响应状态：{response.status_code}")
    return response

# ==================== 数据存储 ====================
# 内存存储会话状态 (生产环境应使用 Redis 等)
sessions: Dict[str, Dict[str, Any]] = {}

# ==================== 数据模型 ====================
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class UploadResponse(BaseModel):
    success: bool
    message: str
    session_id: str

class FrontendLog(BaseModel):
    timestamp: str
    level: str
    message: str

# 前端日志处理器
frontend_log_handler = logging.FileHandler(LOG_DIR / "frontend.log", encoding='utf-8')
frontend_log_handler.setFormatter(log_format)
frontend_log_handler.setLevel(logging.DEBUG)
frontend_logger = logging.getLogger('frontend')
frontend_logger.setLevel(logging.DEBUG)
frontend_logger.addHandler(frontend_log_handler)

# ==================== 辅助函数 ====================
def read_resume_content(file_content: bytes, filename: str) -> Optional[str]:
    """读取简历内容"""
    try:
        file_ext = filename.lower().split('.')[-1]

        # 保存临时文件
        temp_path = ROOT_DIR / "temp_uploads"
        temp_path.mkdir(exist_ok=True)
        file_save_path = temp_path / filename

        with open(file_save_path, 'wb') as f:
            f.write(file_content)

        # 根据文件类型读取
        if file_ext == 'txt':
            with open(file_save_path, 'r', encoding='utf-8') as f:
                content = f.read()
        elif file_ext == 'docx':
            content = read_word(str(file_save_path))
        elif file_ext == 'pdf':
            content = read_pdf(str(file_save_path))
        else:
            return None

        # 清理临时文件
        file_save_path.unlink()
        return content

    except Exception as e:
        return None

def get_or_create_session(session_id: Optional[str] = None) -> tuple[str, Dict]:
    """获取或创建会话"""
    if session_id is None or session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "workflow_app": create_workflow(),
            "agent_state": None,
            "resume_text": None,
            "student_profile": None,
            "job_profile": None,
            "match_result": None
        }
    return session_id, sessions[session_id]

def reset_agent_state(session_data: Dict) -> Dict:
    """重置智能体状态"""
    session_data["agent_state"] = {
        "messages": [],
        "resume_text": session_data.get("resume_text"),
        "student_profile": session_data.get("student_profile"),
        "target_job_name": None,
        "job_profile": None,
        "match_result": None,
        "next_step": "agent"
    }
    return session_data["agent_state"]

async def run_agent_step_stream(session_data: Dict, user_message: str):
    """流式运行智能体，实时输出思考过程和回答"""
    from main_agent.utils.config_loader import settings
    from openai import OpenAI
    from main_agent.nodes.supervisor import MainAgentNode
    from main_agent.tools.expert_tools import EXPERT_TOOLS_SPEC, get_student_profile, analyze_job_match

    # 初始化或更新状态
    if session_data["agent_state"] is None:
        reset_agent_state(session_data)

    # 添加用户消息到状态
    session_data["agent_state"]["messages"].append(HumanMessage(content=user_message))
    logger.info(f"[Chat] 用户消息：{user_message}")

    client = OpenAI(
        api_key=settings['llm']['api_key'],
        base_url=settings['llm']['base_url'],
    )

    agent_node = MainAgentNode()
    messages = agent_node._build_messages(session_data["agent_state"])
    logger.info(f"[Chat] 发送消息到 LLM，共 {len(messages)} 条")

    # 发送流式请求
    completion = client.chat.completions.create(
        model="qwen3.5-plus",
        messages=messages,
        tools=EXPERT_TOOLS_SPEC,
        extra_body={"enable_thinking": True},
        stream=True
    )

    full_content = ""
    tool_calls_dict = {}

    for chunk in completion:
        delta = chunk.choices[0].delta

        # 输出思考过程
        if hasattr(delta, "reasoning_content") and delta.reasoning_content:
            yield json.dumps({"type": "reasoning", "content": delta.reasoning_content}, ensure_ascii=False) + "\n"

        # 输出回复内容
        if hasattr(delta, "content") and delta.content:
            yield json.dumps({"type": "answer", "content": delta.content}, ensure_ascii=False) + "\n"
            full_content += delta.content

        # 处理工具调用
        if hasattr(delta, "tool_calls") and delta.tool_calls:
            for tc in delta.tool_calls:
                idx = tc.index
                if idx not in tool_calls_dict:
                    tool_calls_dict[idx] = {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": "", "arguments": ""}
                    }
                if tc.function.name:
                    tool_calls_dict[idx]["function"]["name"] += tc.function.name
                if tc.function.arguments:
                    tool_calls_dict[idx]["function"]["arguments"] += tc.function.arguments

    logger.info(f"[Chat] LLM 响应完成，full_content: {full_content[:100]}...")
    logger.info(f"[Chat] 工具调用数量：{len(tool_calls_dict)}")

    # 执行工具调用
    tool_calls = list(tool_calls_dict.values()) if tool_calls_dict else None

    if tool_calls:
        for tc in tool_calls:
            tool_name = tc['function']['name']
            tool_args = json.loads(tc['function']['arguments']) if tc['function']['arguments'] else {}

            logger.info(f"[Chat] 执行工具：{tool_name}, 参数：{tool_args}")
            yield json.dumps({"type": "tool_call", "name": tool_name, "args": tool_args}, ensure_ascii=False) + "\n"

            # 执行工具
            try:
                tool_result = ""
                if tool_name == "get_student_profile":
                    tool_result = get_student_profile(session_data)
                    # 更新会话状态（不再通过流式传输）
                    try:
                        student_profile = json.loads(tool_result)
                        session_data["student_profile"] = student_profile
                        logger.info(f"[Chat] 学生画像已更新")
                    except Exception as e:
                        logger.warning(f"[Chat] 解析学生画像失败：{e}")
                elif tool_name == "analyze_job_match":
                    tool_result = analyze_job_match(
                        tool_args.get("match_job", ""),
                        tool_args.get("description", ""),
                        session_data
                    )
                    logger.info(f"[Chat] 人岗匹配结果：{tool_result[:200]}...")
                    # 更新会话状态（不再通过流式传输）
                    try:
                        result_data = json.loads(tool_result)
                        if "job_profile" in result_data:
                            session_data["job_profile"] = result_data["job_profile"]
                            logger.info(f"[Chat] 岗位画像已更新")
                        if "match_result" in result_data:
                            session_data["match_result"] = result_data["match_result"]
                            logger.info(f"[Chat] 匹配结果已更新")
                    except Exception as e:
                        logger.warning(f"[Chat] 解析匹配结果失败：{e}")
                else:
                    tool_result = "未知工具"

                yield json.dumps({"type": "tool_result", "name": tool_name, "result": tool_result[:500]}, ensure_ascii=False) + "\n"
            except Exception as e:
                logger.error(f"[Chat] 工具执行失败：{e}")
                yield json.dumps({"type": "tool_error", "name": tool_name, "error": str(e)}, ensure_ascii=False) + "\n"

        # 工具执行后，继续迭代获取最终回复
        if tool_calls:
            logger.info(f"[Chat] 工具执行完成，继续生成最终回复...")
            # 将工具结果添加到消息历史
            for tc in tool_calls:
                tool_name = tc['function']['name']
                tool_args = json.loads(tc['function']['arguments']) if tc['function']['arguments'] else {}

                # 执行工具获取结果
                try:
                    if tool_name == "get_student_profile":
                        tool_result = get_student_profile(session_data)
                    elif tool_name == "analyze_job_match":
                        tool_result = analyze_job_match(
                            tool_args.get("match_job", ""),
                            tool_args.get("description", ""),
                            session_data
                        )
                    else:
                        tool_result = "未知工具"

                    # 添加工具结果到消息历史
                    # 注意：assistant 消息必须有 content（即使是空字符串），不能是 None
                    session_data["agent_state"]["messages"].append(AIMessage(
                        content="",
                        additional_kwargs={"tool_calls": [tc]}
                    ))
                    session_data["agent_state"]["messages"].append(ToolMessage(
                        content=tool_result,
                        tool_call_id=tc.get("id", "")
                    ))
                    logger.info(f"[Chat] 已添加工具结果到消息历史")
                except Exception as e:
                    logger.error(f"[Chat] 添加工具结果失败：{e}")
                    session_data["agent_state"]["messages"].append(ToolMessage(
                        content=f"工具执行失败：{str(e)}",
                        tool_call_id=tc.get("id", "")
                    ))

            # 继续流式生成最终回复
            try:
                messages = agent_node._build_messages(session_data["agent_state"])
                logger.info(f"[Chat] 发送第二次请求到 LLM，共 {len(messages)} 条消息")
                completion = client.chat.completions.create(
                    model="qwen3.5-plus",
                    messages=messages,
                    tools=EXPERT_TOOLS_SPEC,
                    extra_body={"enable_thinking": True},
                    stream=True
                )

                final_content = ""
                has_final_answer = False
                for chunk in completion:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                        yield json.dumps({"type": "reasoning", "content": delta.reasoning_content}, ensure_ascii=False) + "\n"
                    if hasattr(delta, "content") and delta.content:
                        yield json.dumps({"type": "answer", "content": delta.content}, ensure_ascii=False) + "\n"
                        final_content += delta.content
                        has_final_answer = True

                logger.info(f"[Chat] 最终回复内容：{final_content[:100] if final_content else '(空)'}...")
                if final_content:
                    yield json.dumps({"type": "final_answer", "content": final_content}, ensure_ascii=False) + "\n"
                else:
                    logger.warning("[Chat] 最终回复为空，可能是 LLM 没有生成内容")
            except Exception as e:
                logger.error(f"[Chat] 生成最终回复失败：{e}")
                yield json.dumps({"type": "error", "content": str(e)}, ensure_ascii=False) + "\n"
        else:
            # 没有工具调用，直接返回 accumulated content
            if full_content:
                yield json.dumps({"type": "final_answer", "content": full_content}, ensure_ascii=False) + "\n"

# ==================== API 端点 ====================
@app.get("/")
async def root():
    """API 根路径"""
    return {
        "name": "职业规划智能体 API",
        "version": "1.0.0",
        "description": "提供简历分析、人岗匹配、职业规划功能",
        "endpoints": {
            "POST /api/upload": "上传简历文件",
            "POST /api/chat/stream": "与智能体对话（流式输出）",
            "GET /api/profile/student": "获取学生画像",
            "GET /api/profile/job": "获取岗位画像",
            "GET /api/match/result": "获取匹配结果",
            "POST /api/job/analyze": "分析岗位并生成画像和匹配结果",
            "GET /api/session/{session_id}": "获取会话状态",
            "DELETE /api/session/{session_id}": "删除会话"
        }
    }


class JobAnalyzeRequest(BaseModel):
    job_name: str
    job_description: Optional[str] = None

@app.get("/api/profile/student")
async def get_student_profile_api(session_id: Optional[str] = None):
    """
    获取学生画像
    - session_id: 可选，指定会话 ID
    """
    if session_id is None or session_id not in sessions:
        return {"student_profile": None, "message": "未找到会话或学生画像"}

    session_data = sessions[session_id]
    student_profile = session_data.get("student_profile")

    if student_profile is None:
        return {"student_profile": None, "message": "学生画像不存在"}

    return {"student_profile": student_profile}


@app.get("/api/profile/job")
async def get_job_profile_api(session_id: Optional[str] = None):
    """
    获取岗位画像
    - session_id: 可选，指定会话 ID
    """
    if session_id is None or session_id not in sessions:
        return {"job_profile": None, "message": "未找到会话或岗位画像"}

    session_data = sessions[session_id]
    job_profile = session_data.get("job_profile")

    if job_profile is None:
        return {"job_profile": None, "message": "岗位画像不存在"}

    return {"job_profile": job_profile}


@app.get("/api/match/result")
async def get_match_result_api(session_id: Optional[str] = None):
    """
    获取匹配结果
    - session_id: 可选，指定会话 ID
    """
    if session_id is None or session_id not in sessions:
        return {"match_result": None, "message": "未找到会话或匹配结果"}

    session_data = sessions[session_id]
    match_result = session_data.get("match_result")

    if match_result is None:
        return {"match_result": None, "message": "匹配结果不存在"}

    return {"match_result": match_result}


@app.post("/api/job/analyze")
async def analyze_job(request: JobAnalyzeRequest, session_id: Optional[str] = None):
    """
    分析岗位并生成画像和匹配结果
    - job_name: 岗位名称
    - job_description: 岗位描述（可选）
    - session_id: 可选，指定会话 ID
    """
    session_id, session_data = get_or_create_session(session_id)

    # 调用工具分析岗位
    from main_agent.tools.expert_tools import analyze_job_match

    try:
        tool_result = analyze_job_match(
            match_job=request.job_name,
            description=request.job_description or "",
            state_data=session_data
        )

        result_data = json.loads(tool_result)

        if "job_profile" in result_data:
            session_data["job_profile"] = result_data["job_profile"]
        if "match_result" in result_data:
            session_data["match_result"] = result_data["match_result"]

        return {
            "success": True,
            "job_profile": result_data.get("job_profile"),
            "match_result": result_data.get("match_result")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/log")
async def receive_frontend_log(log: FrontendLog):
    """接收前端日志并写入文件"""
    frontend_logger.info(f"[{log.level}] {log.message}")
    return {"success": True}

@app.post("/api/upload", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...), session_id: Optional[str] = None):
    """
    上传简历文件
    - 支持：.txt, .docx, .pdf
    - 返回：session_id
    """
    file_content = await file.read()
    resume_text = read_resume_content(file_content, file.filename)

    if resume_text is None:
        raise HTTPException(status_code=400, detail="无法读取简历文件，请检查格式是否正确")

    # 使用现有会话或创建新会话
    session_id, session_data = get_or_create_session(session_id)
    session_data["resume_text"] = resume_text

    # 提取学生画像并保存到 session（不返回给客户端）
    from main_agent.tools.expert_tools import student_service
    try:
        # 使用非流式模式避免 HTTP 请求超时问题
        logger.info("开始提取学生画像（非流式模式）...")
        profile = student_service.extract_profile(resume_text, streaming=False)
        session_data["student_profile"] = profile.model_dump()
        logger.info(f"学生画像提取成功：{len(profile.skills)} 个技能，{len(profile.Experience)} 段经历")
    except Exception as e:
        logger.warning(f"学生画像提取失败：{e}")

    return UploadResponse(
        success=True,
        message="简历上传成功",
        session_id=session_id
    )


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    与智能体对话（流式输出）
    返回 NDJSON 格式，每行一个 JSON 对象
    事件类型包括：
    - reasoning: 思考过程
    - answer: 回答内容（流式累加）
    - tool_call: 工具调用
    - tool_result: 工具返回结果
    - final_answer: 最终回答
    """
    session_id, session_data = get_or_create_session(request.session_id)

    return StreamingResponse(
        run_agent_step_stream(session_data, request.message),
        media_type="application/x-ndjson"
    )

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": f"会话 {session_id} 已删除"}
    raise HTTPException(status_code=404, detail="会话不存在")

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """获取会话状态"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在")

    session_data = sessions[session_id]
    return {
        "session_id": session_id,
        "has_resume": session_data.get("resume_text") is not None,
        "has_student_profile": session_data.get("student_profile") is not None,
        "has_job_profile": session_data.get("job_profile") is not None,
        "has_match_result": session_data.get("match_result") is not None,
        "student_profile": session_data.get("student_profile"),
        "job_profile": session_data.get("job_profile"),
        "match_result": session_data.get("match_result")
    }

# ==================== 启动命令 ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
