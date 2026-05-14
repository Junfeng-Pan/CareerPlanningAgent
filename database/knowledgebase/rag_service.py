import os
import json
import glob
from pathlib import Path
from typing import List, Optional
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from main_agent.utils.config_loader import settings

class JobKnowledgeBase:
    """
    岗位知识库（重构版）

    设计原则：
    1. 每个岗位画像作为一个独立分片（JSON 文件）
    2. 仅对 name 和 summary 字段进行向量化表示
    3. 检索时返回完整的岗位画像 JSON
    """

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.persist_directory = str(self.root_dir / "data" / "chroma_db")
        self.knowledge_raw_dir = self.root_dir / "data" / "knowledgebase_raw"

        # 使用 dashscope 的 text-embedding-v4 模型
        self.embeddings = DashScopeEmbeddings(
            dashscope_api_key=settings['llm']['api_key'],
            model="text-embedding-v4"
        )

        self.vector_store = self._init_vector_store()

    def _init_vector_store(self) -> Chroma:
        """初始化向量数据库"""
        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            print("[RAG] 正在加载现有向量数据库...")
            return Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)

        print("[RAG] 正在从原始知识库文件初始化向量数据库...")
        if not self.knowledge_raw_dir.exists():
            print(f"[RAG] 警告：未找到知识库目录 {self.knowledge_raw_dir}")
            return Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)

        documents = []

        # 遍历知识库目录下的所有 JSON 文件
        for json_file in glob.glob(str(self.knowledge_raw_dir / "*.json")):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)

                # 提取 name 和 summary 用于向量化
                name = profile_data.get("name", "")
                summary = profile_data.get("summary", "")

                # 构建用于向量化的文本（仅包含 name 和 summary）
                vector_text = f"岗位名称：{name}。岗位综述：{summary}"

                # 完整画像数据保存在 metadata 中
                doc = Document(
                    page_content=vector_text,
                    metadata={
                        "full_profile": json.dumps(profile_data, ensure_ascii=False),
                        "name": name
                    }
                )
                documents.append(doc)

            except Exception as e:
                print(f"[RAG] 读取文件 {json_file} 失败：{e}")

        if not documents:
            print("[RAG] 未找到任何岗位画像文件，返回空向量库")
            return Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)

        print(f"[RAG] 成功加载 {len(documents)} 个岗位画像")
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        return vector_store

    def query(self, query_text: str, k: int = 3) -> Optional[str]:
        """
        检索相关岗位画像

        Args:
            query_text: 查询文本（岗位名称或描述）
            k: 返回结果数量

        Returns:
            匹配度最高的岗位画像 JSON 字符串，如果未找到则返回 None
        """
        try:
            results = self.vector_store.similarity_search(query_text, k=k)
            if not results:
                return None

            # 返回第一个匹配结果的完整画像
            best_match = results[0]
            full_profile_str = best_match.metadata.get("full_profile")

            if full_profile_str:
                return full_profile_str
            return None

        except Exception as e:
            print(f"[RAG] 检索过程发生错误：{e}")
            return None

    def add_job_profile(self, name: str, profile_data: dict):
        """
        添加新的岗位画像到知识库

        Args:
            name: 岗位名称
            profile_data: 完整的岗位画像字典
        """
        try:
            # 构建向量化文本
            summary = profile_data.get("summary", "")
            vector_text = f"岗位名称：{name}。岗位综述：{summary}"

            doc = Document(
                page_content=vector_text,
                metadata={
                    "full_profile": json.dumps(profile_data, ensure_ascii=False),
                    "name": name
                }
            )

            self.vector_store.add_documents([doc])
            print(f"[RAG] 已添加岗位画像：{name}")

        except Exception as e:
            print(f"[RAG] 添加岗位画像失败：{e}")

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
    test_query = "Java 开发"
    print(f"测试查询：{test_query}")
    result = kb.query(test_query)
    print(f"检索结果：{result}")
