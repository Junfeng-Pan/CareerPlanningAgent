import yaml
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from .schemas import StudentProfile

from .prompt import RESUME_EXTRACTION_SYSTEM_PROMPT, RESUME_EXTRACTION_HUMAN_PROMPT

class QwenExtractionService:
    """
    大模型抽取服务类，负责与 Qwen 模型交互并提取结构化简历信息。
    """
    def __init__(self, config_path: str = "config/settings.yaml"):
        # 1. 加载配置
        if not os.path.exists(config_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, config_path)
            
        if not os.path.exists(config_path):
            # 兼容性处理
            self.api_key = os.getenv("DASHSCOPE_API_KEY")
            self.base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
            self.model_name = os.getenv("DASHSCOPE_MODEL_NAME", "qwen3.5-flash")
        else:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            llm_config = config.get('llm', {})
            self.api_key = llm_config.get('api_key') or os.getenv("DASHSCOPE_API_KEY")
            self.base_url = llm_config.get('base_url') or os.getenv("DASHSCOPE_BASE_URL")
            self.model_name = llm_config.get('model_name') or os.getenv("DASHSCOPE_MODEL_NAME", "qwen3.5-flash")

        # 2. 初始化解析器
        self.parser = PydanticOutputParser(pydantic_object=StudentProfile)

        # 3. 初始化 LLM
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model_name,
            temperature=0,
            streaming=True
        )

        # 4. 定义 Prompt 模板并注入格式指令
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", RESUME_EXTRACTION_SYSTEM_PROMPT + "\n\n{format_instructions}"),
            ("human", RESUME_EXTRACTION_HUMAN_PROMPT)
        ]).partial(format_instructions=self.parser.get_format_instructions())

    def extract_profile(self, text: str) -> StudentProfile:
        """
        核心方法：调用 LLM 提取结构化信息，并实时流式打印。
        """
        chain = self.prompt | self.llm
        print("\n" + "-"*20 + " [学生专家] 正在生成画像 " + "-"*20)
        full_content = ""
        try:
            for chunk in chain.stream({"resume_text": text}):
                content = chunk.content
                if content:
                    print(content, end="", flush=True)
                    full_content += content
            
            print("\n" + "-"*50)
            return self.parser.parse(full_content)
        except Exception as e:
            print(f"\n[StudentExtractor] LLM Extraction Error: {e}")
            return StudentProfile()
