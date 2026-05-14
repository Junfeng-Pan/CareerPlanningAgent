import yaml
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from .schemas import StudentProfile

from .prompt import RESUME_EXTRACTION_SYSTEM_PROMPT, RESUME_EXTRACTION_HUMAN_PROMPT

# 配置日志
logger = logging.getLogger(__name__)

class QwenExtractionService:
    """
    大模型抽取服务类，负责与 Qwen 模型交互并提取结构化简历信息。
    """
    def __init__(self, config_path: str = None):
        # 0. 加载 .env 文件
        # 路径：studentprofile_agent/agentService/service.py -> 需要向上 3 级到项目根目录
        root_dir = Path(__file__).resolve().parent.parent.parent
        env_path = root_dir / ".env"
        load_dotenv(str(env_path))

        # 1. 加载配置 - 优先从环境变量读取
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.model_name = os.getenv("DASHSCOPE_MODEL_NAME", "qwen3.5-flash")

        # 如果环境变量中没有，尝试从配置文件读取
        if not self.api_key:
            if config_path is None:
                config_path = root_dir / "config" / "settings.yaml"

            if config_path and os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                llm_config = config.get('llm', {})
                self.api_key = llm_config.get('api_key') or self.api_key
                self.base_url = llm_config.get('base_url') or self.base_url
                self.model_name = llm_config.get('model_name') or self.model_name

        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY 未配置！请在 .env 文件中设置")

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

    def extract_profile(self, text: str, streaming: bool = True) -> StudentProfile:
        """
        核心方法：调用 LLM 提取结构化信息。

        参数：
        - text: 简历文本
        - streaming: 是否流式输出（默认 True）。设置为 False 可避免 HTTP 请求超时问题
        """
        chain = self.prompt | self.llm
        logger.info("-" * 20 + " [学生专家] 正在生成画像 " + "-" * 20)
        full_content = ""
        try:
            if streaming:
                # 流式模式：实时打印输出
                for chunk in chain.stream({"resume_text": text}):
                    content = chunk.content
                    if content:
                        content_text = content.replace('💡', '[INFO]').replace('**', '').replace('✅', '[OK]').replace('❌', '[X]')
                        logger.debug(content_text)
                        full_content += content
            else:
                # 非流式模式：一次性获取结果，避免 HTTP 超时
                logger.info("[非流式模式] 正在调用 LLM...")
                response = chain.invoke({"resume_text": text}, config={"timeout": 60})
                full_content = response.content
                logger.info("[非流式模式] 已获取完整响应")

            logger.info("-" * 50)
            return self.parser.parse(full_content)
        except Exception as e:
            logger.error(f"[StudentExtractor] LLM Extraction Error: {e}")
            return StudentProfile()
