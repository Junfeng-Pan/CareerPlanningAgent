import json
import logging
from typing import Dict, Any, Optional
from main_agent.state import AgentState

# 配置日志
logger = logging.getLogger(__name__)

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
    注意：学生画像采用贪婪加载策略，用户一上传简历系统就会自动提取并缓存。
    只有当用户显式表达"请你分析我的能力画像"等明确要求时，才需要调用此工具刷新画像。
    """
    logger.info("[工具执行] 正在分析学生画像...")

    # 检查是否已有缓存的学生画像
    cached_profile = state_data.get("student_profile")
    if cached_profile:
        logger.info("[工具执行] 使用已缓存的学生画像")
        return json.dumps(cached_profile, ensure_ascii=False)

    resume_text = state_data.get("resume_text")
    if not resume_text:
        return "错误：未找到简历文本，请提醒用户上传。"

    profile = student_service.extract_profile(resume_text)
    return profile.model_dump_json()

def analyze_job_match(match_job: str, description: str, state_data: Dict[str, Any], **kwargs) -> str:
    """
    检索岗位画像并进行人岗匹配分析。

    参数：
    - match_job: 匹配岗位名称（可以是大类的也可以是具体的，取决于用户需求）
    - description: 对于匹配岗位的描述性信息，用于增强向量检索的准确性

    功能说明：
    - 当用户已上传简历时：进行完整的人岗匹配分析，输出匹配度、差距分析
    - 当用户未上传简历时：仅检索并返回岗位画像，介绍岗位职责和要求

    示例：
    - match_job: "Java 工程师"
    - description: "用户想要从事 java 微服务的开发，使用 SpringBoot，SpringCloud 从事后端系统的构建。"
    """
    logger.info(f"[工具执行] 正在处理岗位相关请求...")
    logger.info(f"  - 匹配岗位：{match_job}")
    logger.info(f"  - 岗位描述：{description}")

    # 1. 检索岗位画像
    logger.info("[工具执行] 正在检索岗位画像...")
    job_profile = job_service.get_job_profile(match_job)

    if not job_profile:
        return f"错误：未找到岗位【{match_job}】的相关信息。"

    # 兼容 Pydantic 对象和字典
    if hasattr(job_profile, 'model_dump'):
        job_profile_dict = job_profile.model_dump()
    else:
        job_profile_dict = job_profile

    # 2. 检查是否有简历，决定进行匹配分析还是仅返回岗位画像
    resume_text = state_data.get("resume_text")

    if not resume_text:
        # 无简历模式：仅返回岗位画像
        logger.info("[工具执行] 用户未上传简历，仅返回岗位画像")
        result = {
            "mode": "job_profile_only",
            "job_profile": job_profile_dict,
            "message": f"以下是【{match_job}】的岗位画像，包含岗位职责、技能要求、发展路径等。如果你想进行人岗匹配分析，请上传你的简历。"
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    # 有简历模式：进行完整的人岗匹配分析
    logger.info("[工具执行] 已检测到简历，正在进行匹配分析...")
    match_result = match_service.match(job_profile_dict, resume_text)

    # 合并岗位画像和匹配结果
    result = {
        "mode": "full_analysis",
        "job_profile": job_profile_dict,
        "match_result": match_result.model_dump() if hasattr(match_result, 'model_dump') else match_result
    }

    return json.dumps(result, ensure_ascii=False, indent=2)

# 工具描述字典列表（重构后只保留两个工具）
EXPERT_TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "get_student_profile",
            "description": "分析用户简历文本并生成学生能力模型画像。注意：学生画像已自动提取并缓存，只有当用户显式要求重新分析时才调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_job_match",
            "description": "根据用户指定的岗位名称和描述性信息，检索岗位画像。如果用户已上传简历，则进行深度人岗匹配分析，输出匹配度、差距分析和求职建议；如果用户未上传简历，则仅返回岗位画像用于介绍岗位。岗位画像包含职业发展路径信息，可用于职业规划分析。",
            "parameters": {
                "type": "object",
                "properties": {
                    "match_job": {
                        "type": "string",
                        "description": "匹配岗位名称（可以是具体岗位如'Java 工程师'，也可以是大类如'软件开发'，取决于用户需求）"
                    },
                    "description": {
                        "type": "string",
                        "description": "对于匹配岗位的描述性信息，用于增强向量检索的准确性。例如：'用户想要从事 java 微服务的开发，使用 SpringBoot，SpringCloud 从事后端系统的构建。' 或者简单描述'用户想了解这个岗位的基本情况'"
                    }
                },
                "required": ["match_job", "description"]
            }
        }
    }
]
