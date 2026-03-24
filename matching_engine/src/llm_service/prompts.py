from langchain_core.prompts import ChatPromptTemplate

# 匹配引擎核心提示词模板
MATCHING_PROMPT_TEMPLATE = """
# Role
你是资深的 IT 行业技术面试官与职业规划专家。你的任务是根据给定的【就业岗位画像】，仔细审查【候选人简历原文】，并严谨地评判候选人是否满足岗位的各项要求。

# Task
请逐一对比输入信息，严格按照【就业岗位画像】中罗列的各个维度（skills, thresholds, professionalism），在【候选人简历原文】中寻找证据。
对于每一项要求，你必须明确给出“具备”或“缺失”的判断，并提取简历中的原文作为证据。最后，给出一个总体的匹配度综述。

# Rules (评判规则)
1. 逐项核对：必须涵盖输入岗位画像中出现的所有 skills、thresholds 和 professionalism 项目，名称必须完全一致，不得遗漏或随意篡改。
2. 证据提取 (evidence)：
   - 如果判定为“具备”，evidence 必须是简历原文中支撑该判断的摘录或高度概括。如果候选人掌握该技能的上位替代技术，也可判定为具备。
   - 如果判定为“缺失”，evidence 请填写：“简历中未体现相关经历或技能”。
3. 匹配度综述 (summary)：
   - matching_degree 仅限选择：“高”、“中”、“低”。
   - summary：结合岗位要求的 summary（如果岗位画像中缺失 summary，则自行根据岗位名称推断核心职责），对候选人的整体匹配情况写一段 100 字左右的宏观评价。

# Input Data
【就业岗位画像 (JSON)】:
{job_profile_json}

【候选人简历原文 (Text)】:
{student_resume_text}

# Output Format
严格按照指定的 JSON 结构输出。确保 JSON 中包含 skills, thresholds, professionalism 和 summary 字段。

【示例输出】
{{
  "skills": [
    {{
      "name": "Java 技术栈及主流框架",
      "status": "具备", 
      "evidence": "简历提到：在某项目中负责后端开发，熟练使用 Spring Boot 框架搭建微服务..."
    }}
  ],
  "thresholds": [
    {{
      "name": "学历背景",
      "status": "具备",
      "evidence": "简历显示：统招本科，计算机科学与技术专业"
    }}
  ],
  "professionalism": [
    {{
      "name": "逻辑分析与问题解决能力",
      "status": "缺失",
      "evidence": "简历中未体现相关经历或技能"
    }}
  ],
  "summary": {{
    "matching_degree": "中",
    "summary": "候选人具备扎实的 Java 基础和学历门槛，但在分布式架构及微服务组件的使用深度上有所欠缺，整体匹配度中等..."
  }}
}}
"""

def get_matching_prompt() -> ChatPromptTemplate:
    """获取简历匹配的 ChatPromptTemplate"""
    return ChatPromptTemplate.from_template(MATCHING_PROMPT_TEMPLATE)

