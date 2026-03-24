import os
import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from job_system.knowledge_base.rag_service import get_job_kb

def test_rag_query():
    print("--- 开始测试 RAG 检索 ---")
    kb = get_job_kb()
    
    query = "Java 开发工程师"
    print(f"查询关键词: {query}")
    
    context = kb.query(query)
    
    if context:
        print("\n检索到的上下文预览:")
        print("-" * 30)
        print(context[:500] + "...")
        print("-" * 30)
    else:
        print("\n未检索到相关内容。")

if __name__ == "__main__":
    test_rag_query()
