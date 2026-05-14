import logging
from database.knowledgebase.rag_service import JobKnowledgeBase
from .llm_service.extractor import JobExtractor

logger = logging.getLogger(__name__)

class JobService:
    def __init__(self):
        # 实例化知识库和提取器
        self.kb = JobKnowledgeBase()
        self.extractor = JobExtractor()

    def get_job_profile(self, job_name: str):
        """
        二级检索逻辑（重构后）：
        1. RAG: 在岗位库中检索相似描述
        2. LLM: 如果找不到，利用 LLM 的通用知识生成
        """
        try:
            # Tier 1: RAG 知识库模糊检索
            logger.info(f"[JobService] Tier 1: 尝试从知识库检索【{job_name}】...")
            context = self.kb.query(job_name, k=3)
            if context and len(context.strip()) > 10:
                logger.info("[JobService] RAG 命中，正在利用提取器生成画像...")
                return self.extractor.extract(context)

            # Tier 2: LLM 内部知识生成
            logger.info(f"[JobService] Tier 2: RAG 未命中，利用 LLM 通用知识生成【{job_name}】画像...")
            return self.extractor.extract(f"请根据你的通用知识，为【{job_name}】这个岗位生成标准的画像要求。")

        except Exception as e:
            logger.error(f"[JobService] 检索过程出错：{e}")
            return None
