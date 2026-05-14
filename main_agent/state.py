from typing import Annotated, List, Optional, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Agent 状态定义（重构版 v3）

    主要变更：
    - 添加 student_profile 字段：缓存学生画像，避免重复调用 LLM
    - 保留 job_profile 字段：存储 RAG 检索出来的岗位画像
    - 注意：学生画像不注入提示词，因为简历原文已包含足够信息
    """
    # 消息列表，用于存储对话历史
    messages: Annotated[List[BaseMessage], add_messages]

    # 简历原文内容
    resume_text: Optional[str]

    # 学生结构化画像 (来自 studentprofile-agent)
    # 注意：此字段仅用于缓存，不注入提示词（简历原文已包含足够信息）
    student_profile: Optional[dict]

    # 用户目标岗位名称（可选，用于记录用户明确提到的岗位）
    target_job_name: Optional[str]

    # 岗位结构化画像 (来自 job_system，RAG 检索结果)
    # 注入提示词有助于大模型理解岗位要求，支持职业规划分析
    job_profile: Optional[dict]

    # 匹配结果 (来自 matching_engine)
    # 包含 skills、thresholds、professionalism 的匹配详情及 summary
    match_result: Optional[dict]

    # 下一步执行的节点名称
    next_step: str
