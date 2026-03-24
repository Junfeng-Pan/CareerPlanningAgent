import yaml
import os
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from .schemas import JobProfile
from .prompts import get_job_extractor_prompt
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class JobExtractor:
    def __init__(self, config_path: str = None):
        # 默认配置
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.model_name = os.getenv("DASHSCOPE_MODEL_NAME", "qwen3.5-flash")
        self.temperature = 0.0
        self.max_retries = 3

        # 1. 初始化解析器
        self.parser = PydanticOutputParser(pydantic_object=JobProfile)
        
        # 2. 初始化 LLM
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model_name,
            temperature=self.temperature,
            max_retries=self.max_retries,
            streaming=True  # 明确启用流式
        )
        
        # 3. 获取 ChatPromptTemplate
        self.prompt = get_job_extractor_prompt()
        
        # 4. 构建执行链 (将 format_instructions 注入)
        self.prompt_with_instructions = self.prompt.partial(
            format_instructions=self.parser.get_format_instructions()
        )
        
        # 此时不能直接将 parser 拼入链尾，因为我们要拦截流式中间过程
        self.chain = self.prompt_with_instructions | self.llm

    def extract(self, job_detail: str) -> JobProfile:
        """执行结构化抽取逻辑，并实时流式打印"""
        print("\n" + "-"*20 + " [专家模型] 正在生成画像 " + "-"*20)
        full_content = ""
        try:
            # 实时流式输出
            for chunk in self.chain.stream({"job_detail": job_detail}):
                content = chunk.content
                if content:
                    print(content, end="", flush=True)
                    full_content += content
            
            print("\n" + "-"*50)
            # 完成后进行解析
            return self.parser.parse(full_content)
        except Exception as e:
            print(f"\n[JobExtractor] LLM 抽取过程发生错误: {str(e)}")
            # 如果流式解析失败，可能是部分输出，尝试挽救性返回
            raise

if __name__ == "__main__":
    pass
