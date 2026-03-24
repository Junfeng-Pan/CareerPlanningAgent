import json
from typing import Dict, Any, Optional
from main_agent.state import AgentState

# 直接导入底层服务
from studentprofile_agent.agentService.service import QwenExtractionService
from job_system.job_service import JobService
from matching_engine.src.llm_service.chain import LLMMatchingService

# 实例化底层服务
student_service = QwenExtractionService()
job_service = JobService()
match_service = LLMMatchingService()

def get_student_profile(state_data: Dict[str, Any], **kwargs) -> str:
    """
    分析学生简历，提取能力建模和画像。
    """
    print("\n[工具执行] 正在分析学生画像...")
    resume_text = state_data.get("resume_text")
    if not resume_text:
        return "错误：未找到简历文本，请提醒用户上传。"
    
    profile = student_service.extract_profile(resume_text)
    return profile.model_dump_json()

def get_job_profile(target_job_name: str, state_data: Dict[str, Any], **kwargs) -> str:
    """
    获取指定岗位的标准画像。
    """
    print(f"\n[工具执行] 正在检索岗位画像: {target_job_name}")
    profile = job_service.get_job_profile(target_job_name)
    if profile:
        # 兼容 Pydantic 对象和字典
        return profile.model_dump_json() if hasattr(profile, 'model_dump_json') else json.dumps(profile)
    return f"未找到岗位【{target_job_name}】的相关信息。"

def analyze_match(state_data: Dict[str, Any], **kwargs) -> str:
    """
    进行人岗匹配分析。
    """
    print("\n[工具执行] 正在进行人岗匹配...")
    student_profile = state_data.get("student_profile")
    job_profile = state_data.get("job_profile")
    resume_text = state_data.get("resume_text")
    
    if not student_profile or not job_profile:
        return "错误：缺少学生画像或岗位画像，请先调用相关工具生成。"
    
    result = match_service.match(job_profile, resume_text)
    return result.model_dump_json() if hasattr(result, 'model_dump_json') else json.dumps(result)

def search_main_knowledge_base(query: str, **kwargs) -> str:
    """
    检索职业规划知识库。
    """
    print(f"\n[工具执行] 检索知识库: {query}")
    return "【知识库暂无相关内容】"

# 工具描述字典列表
EXPERT_TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "get_student_profile",
            "description": "分析简历文本并生成学生能力模型画像",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_job_profile",
            "description": "根据岗位名称检索或生成岗位的详细画像要求",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_job_name": {"type": "string", "description": "岗位名称"}
                },
                "required": ["target_job_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_match",
            "description": "综合学生画像和岗位画像，进行深度匹配分析并给出建议",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_main_knowledge_base",
            "description": "检索职业规划知识库，获取行业洞察、面试指南等",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "检索关键词"}
                },
                "required": ["query"]
            }
        }
    }
]
