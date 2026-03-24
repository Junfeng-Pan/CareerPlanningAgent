from typing import Annotated, List, Optional, TypedDict, Union
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # 消息列表，用于存储对话历史
    messages: Annotated[List[BaseMessage], add_messages]
    
    # 简历原文内容
    resume_text: Optional[str]
    
    # 学生结构化画像 (来自 studentprofile-agent)
    student_profile: Optional[dict]
    
    # 用户目标岗位名称
    target_job_name: Optional[str]
    
    # 岗位结构化画像 (来自 job-system)
    job_profile: Optional[dict]
    
    # 匹配结果 (来自 matching_engine)
    match_result: Optional[dict]
    
    # 下一步执行的节点名称
    next_step: str
