# CareerPlanningAgent 职业规划智能体系统

CareerPlanningAgent 是一个基于 **Single Agent + Tools (ReAct)** 架构构建的职业规划助手。它利用大模型的推理与决策能力，通过调用多个专家工具，为用户提供简历分析、岗位画像检索及人岗匹配建议。

## 🌟 核心特性

- **ReAct 推理循环**：主智能体采用“思考-行动-观察” (Thought-Action-Observation) 循环，自主规划任务路径。
- **三级岗位画像检索**：
  1. **Tier 1 (MySQL)**: 优先检索已人工审核或批量生成的画像特征。
  2. **Tier 2 (RAG)**: 在 9000+ 岗位知识库中基于向量相似度进行实时检索。
  3. **Tier 3 (LLM)**: 若前两级均未命中，则利用 LLM 的通用行业知识生成基准画像。
- **Agentic RAG**：主智能体可主动检索职业规划知识库，获取面试技巧、行业趋势等通用建议。
- **流式实时反馈**：所有专家工具调用及主智能体思考过程均支持 Token 级的流式输出。

## 📂 项目结构

```text
D:\pythonP\Professional_workplace\CareerPlanningAgent\
├───database\             # 统一数据存储层 (MySQL & KnowledgeBase)
├───main_agent\           # 主智能体逻辑 (ReAct 工作流、工具定义)
├───job_system\           # 岗位画像专家服务
├───matching_engine\      # 人岗匹配算法服务
├───studentprofile_agent\ # 学生简历分析服务
├───data\                 # 持久化数据 (ChromaDB, SQLite, 忽略上传)
├───config\               # 配置文件
└───tests\                # 全流程与单元测试
```

## 🛠️ 环境搭建

1. **安装依赖**：
   本项目采用 monorepo 结构，推荐使用 editable 模式安装各个子模块：
   ```bash
   pip install -e ./job_system
   pip install -e ./matching_engine
   pip install -e ./studentprofile_agent
   pip install -r requirements.txt
   ```

2. **配置环境变量**：
   在根目录下创建 `.env` 文件，配置如下参数：
   ```env
   DASHSCOPE_API_KEY=your_api_key_here
   DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   DASHSCOPE_MODEL_NAME=qwen3.5-plus
   ```

3. **数据库初始化**：
   - 执行 `database/mysql/init_db.sql` 初始化 MySQL 表结构。
   - 运行 `database/knowledgebase/rag_service.py` 初始化向量知识库。

## 🚀 快速开始

运行全流程测试脚本，观察主智能体的推理过程：
```bash
python tests/test_main_agent.py
```

---
感谢使用 CareerPlanningAgent！
