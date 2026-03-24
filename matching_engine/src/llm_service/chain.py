import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from .models import MatchingResult
from .prompts import get_matching_prompt
from langchain_core.output_parsers import PydanticOutputParser

# 加载环境变量
load_dotenv()

class LLMMatchingService:
    def __init__(self):
        # 初始化阿里云百炼的 OpenAI 兼容客户端
        self.llm = ChatOpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url=os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            model=os.getenv("DASHSCOPE_MODEL_NAME", "qwen-max"),
            temperature=0.1,
            streaming=True
        )
        
        # 使用 Pydantic 解析器以便能够手动拦截流
        self.parser = PydanticOutputParser(pydantic_object=MatchingResult)
        
        # 组装 Prompt
        self.prompt = get_matching_prompt()
        
        # 构建 LangChain 链
        self.chain = self.prompt | self.llm

    def match(self, job_profile: dict, student_resume: str) -> MatchingResult:
        """
        核心匹配方法，支持流式打印
        """
        # 将岗位画像转换为 JSON 字符串注入 Prompt
        job_profile_json = json.dumps(job_profile, ensure_ascii=False, indent=2)
        
        print("\n" + "-"*20 + " [匹配专家] 正在进行人岗匹配分析 " + "-"*20)
        
        full_content = ""
        try:
            # 执行流式调用
            for chunk in self.chain.stream({
                "job_profile_json": job_profile_json,
                "student_resume_text": student_resume
            }):
                content = chunk.content
                if content:
                    print(content, end="", flush=True)
                    full_content += content
            
            print("\n" + "-"*50)
            # 解析最终结果
            return self.parser.parse(full_content)
        except Exception as e:
            print(f"\n[MatchingService] 匹配过程发生错误: {str(e)}")
            raise
