import os
from pathlib import Path
from main_agent.utils.config_loader import settings

class MainAgentKnowledgeBase:
    def __init__(self):
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.kb_path = self.root_dir / "data" / "knowledgebase_main" / "主智能体知识库.txt"
        self._content = ""
        
        if self.kb_path.exists():
            with open(self.kb_path, "r", encoding="utf-8") as f:
                self._content = f.read()
        else:
            print(f"[Warning] 主智能体知识库文件不存在: {self.kb_path}")

    def search(self, query: str) -> str:
        """
        简单的全文检索逻辑，用于目前的测试。
        未来可以升级为向量检索。
        """
        if not self._content:
            return "知识库为空。"
        
        # 目前简单返回整个内容或根据关键词截取
        # 实际 Agentic RAG 会由模型决定检索关键词
        return f"【主智能体知识库相关参考】：\n{self._content[:2000]}"

main_kb = MainAgentKnowledgeBase()
