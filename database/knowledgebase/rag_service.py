import os
import pandas as pd
from pathlib import Path
from typing import List
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from main_agent.utils.config_loader import settings

class JobKnowledgeBase:
    def __init__(self):
        # 修正路径：Path(__file__).resolve() 是 database/knowledgebase/rag_service.py
        # .parent.parent.parent 是项目根目录 CareerPlanningAgent
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.persist_directory = str(self.root_dir / "data" / "chroma_db")
        self.csv_path = str(self.root_dir / "database" / "knowledgebase" / "cleaned_job_data.csv")
        
        # 使用 dashscope 的 text-embedding-v4 模型
        self.embeddings = DashScopeEmbeddings(
            dashscope_api_key=settings['llm']['api_key'],
            model="text-embedding-v4"
        )
        
        self.vector_store = self._init_vector_store()

    def _init_vector_store(self):
        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            print("[RAG] 正在加载现有向量数据库...")
            return Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
        
        print("[RAG] 正在从 CSV 初始化向量数据库 (这可能需要一点时间)...")
        if not os.path.exists(self.csv_path):
            print(f"[RAG] 警告：未找到知识库文件 {self.csv_path}")
            return Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)

        # 读取 CSV
        try:
            df = pd.read_csv(self.csv_path)
        except Exception as e:
            print(f"[RAG] 读取 CSV 失败: {e}")
            return Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
            
        documents = []
        
        # 处理前 100 条数据作为知识库
        for _, row in df.head(100).iterrows():
            content = f"岗位名称: {row['岗位名称']}\n所属行业: {row['所属行业']}\n岗位详情: {row['岗位详情']}"
            doc = Document(
                page_content=content,
                metadata={"job_name": str(row['岗位名称']), "industry": str(row['所属行业'])}
            )
            documents.append(doc)
        
        if not documents:
            return Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)

        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        return vector_store

    def query(self, job_name: str, k: int = 3) -> str:
        """检索相关岗位信息"""
        try:
            results = self.vector_store.similarity_search(job_name, k=k)
            if not results:
                return ""
            
            context = "\n---\n".join([doc.page_content for doc in results])
            return context
        except Exception as e:
            print(f"[RAG] 检索过程发生错误: {e}")
            return ""

# 全局单例
job_kb = None

def get_job_kb():
    global job_kb
    if job_kb is None:
        job_kb = JobKnowledgeBase()
    return job_kb

if __name__ == "__main__":
    # 初始化向量库
    kb = get_job_kb()
    test_query = "Java开发"
    print(f"测试查询: {test_query}")
    result = kb.query(test_query)
    print(f"检索结果预览: {result[:200]}...")
