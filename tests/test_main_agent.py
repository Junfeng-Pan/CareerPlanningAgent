import os
import sys
import json
from pathlib import Path

# 确保项目根目录在 sys.path 中
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main_agent.workflow import create_workflow
from studentprofile_agent.utils.file_reader import read_word, read_pdf
from langchain_core.messages import HumanMessage

def test_full_workflow():
    # 1. 准备工作流
    app = create_workflow()
    
    # 2. 读取测试简历 (更改为 test_resume.txt)
    resume_path = ROOT_DIR / "resources" / "student_resumes" / "test_resume.txt"
    if resume_path.suffix == ".txt":
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_text = f.read()
    elif resume_path.suffix == ".docx":
        resume_text = read_word(str(resume_path))
    else:
        resume_text = read_pdf(str(resume_path))
    
    print(f"--- [测试] 读取简历完成，字符数: {len(resume_text)} ---")
    
    # 3. 初始状态
    initial_state = {
        "messages": [HumanMessage(content="你好，这是我的简历，我想申请 Java 开发工程师岗位。")],
        "resume_text": resume_text,
        "student_profile": None,
        "target_job_name": None,
        "job_profile": None,
        "match_result": None,
        "next_step": "supervisor"
    }
    
    # 4. 运行工作流
    print("--- [测试] 开始执行工作流 ---")
    for output in app.stream(initial_state, config={"recursion_limit": 50}):
        for node_name, state_update in output.items():
            print(f"\n{'='*60}")
            print(f">>> 节点 [{node_name}] 执行完毕")
            
            # 打印决策信息
            if "next_step" in state_update:
                print(f"    [决策] 下一步: {state_update['next_step']}")
            
            if "target_job_name" in state_update:
                print(f"    [岗位识别] 目标岗位: {state_update['target_job_name']}")
            
            # 打印原始输出 (JSON 格式)
            if "student_profile" in state_update:
                profile = state_update['student_profile']
                print(f"    [学生专家] 原始输出画像 JSON:")
                print(json.dumps(profile, ensure_ascii=False, indent=2))
                
            if "job_profile" in state_update:
                profile = state_update['job_profile']
                print(f"    [岗位专家] 原始输出画像 JSON:")
                if profile:
                    print(json.dumps(profile, ensure_ascii=False, indent=2))
                else:
                    print("null (未找到匹配岗位)")
            
            if "match_result" in state_update:
                res = state_update['match_result']
                # 兼容 Pydantic 对象
                if hasattr(res, 'model_dump'): res = res.model_dump()
                print(f"    [匹配专家] 原始匹配分析 JSON:")
                print(json.dumps(res, ensure_ascii=False, indent=2))
            
            # 打印对话消息
            if "messages" in state_update:
                last_msg = state_update['messages'][-1].content
                print(f"    [系统回复] 完整内容: \n{'-'*20}\n{last_msg}\n{'-'*20}")
            
            print(f"{'='*60}")

    print("\n--- [测试] 工作流执行结束 ---")

if __name__ == "__main__":
    test_full_workflow()
