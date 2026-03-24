import json
from database.mysql.database import SessionLocal, Job, JobFeature
from database.knowledgebase.rag_service import JobKnowledgeBase
from .llm_service.extractor import JobExtractor
from sqlalchemy.orm import joinedload

class JobService:
    def __init__(self):
        # 实例化知识库和提取器
        self.kb = JobKnowledgeBase()
        self.extractor = JobExtractor()

    def get_job_profile(self, job_name: str):
        """
        三级检索逻辑：
        1. MySQL: 查找是否有已处理好的画像
        2. RAG: 在岗位库中检索相似描述
        3. LLM: 如果都找不到，利用 LLM 的通用知识生成
        """
        session = SessionLocal()
        try:
            # Tier 1: MySQL 数据库精准匹配
            print(f"[JobService] Tier 1: 尝试从数据库匹配【{job_name}】...")
            feature = session.query(JobFeature).join(Job).filter(Job.job_name == job_name).first()
            if feature and feature.job_profile_json:
                print("[JobService] 数据库命中！")
                return json.loads(feature.job_profile_json)

            # Tier 2: RAG 知识库模糊检索
            print(f"[JobService] Tier 2: 数据库未命中，尝试 RAG 检索...")
            context = self.kb.query(job_name, k=1)
            if context and len(context.strip()) > 10:
                print("[JobService] RAG 命中，正在利用提取器生成画像...")
                return self.extractor.extract(context)

            # Tier 3: LLM 内部知识生成
            print(f"[JobService] Tier 3: RAG 未命中，利用 LLM 通用知识生成【{job_name}】画像...")
            return self.extractor.extract(f"请根据你的通用知识，为【{job_name}】这个岗位生成标准的画像要求。")

        except Exception as e:
            print(f"[JobService] 检索过程出错: {e}")
            return None
        finally:
            session.close()
