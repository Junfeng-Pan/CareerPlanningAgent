import sys
import os
import time
from tqdm import tqdm

from database.mysql.database import SessionLocal, Job, JobFeature
from ..llm_service.extractor import JobExtractor
from ..data_processor.feature_store import FeatureStore

class JobOrchestrator:
    """
    任务调度与控制模块 (Orchestrator)
    负责从数据库读取原始数据，调用 LLM 抽取，并存入特征表。
    """

    def __init__(self):
        self.extractor = JobExtractor()
        self.store = FeatureStore()

    def run_pipeline(self, limit: int = 10, skip_processed: bool = True):
        """
        执行完整处理流水线
        """
        session = SessionLocal()
        
        print(f"--- [任务调度开始] 处理上限: {limit} ---")
        
        try:
            # 1. 获取待处理的岗位
            query = session.query(Job)
            
            if skip_processed:
                query = query.outerjoin(JobFeature).filter(JobFeature.id == None)
            
            jobs_to_process = query.limit(limit).all()
            
            if not jobs_to_process:
                print("没有发现待处理的岗位数据。")
                return

            print(f"准备处理 {len(jobs_to_process)} 条记录...")
            
            # 2. 遍历处理
            success_count = 0
            for job in tqdm(jobs_to_process, desc="正在抽取岗位画像"):
                try:
                    profile = self.extractor.extract(job.raw_detail)
                    self.store.save_profile(job.id, profile)
                    success_count += 1
                except Exception as e:
                    print(f"\n[错误] 处理岗位 ID {job.id} 失败: {e}")
                    continue
            
            print(f"\n--- [任务调度结束] 成功处理: {success_count} / {len(jobs_to_process)} ---")

        finally:
            session.close()

if __name__ == "__main__":
    orchestrator = JobOrchestrator()
    orchestrator.run_pipeline(limit=5)
