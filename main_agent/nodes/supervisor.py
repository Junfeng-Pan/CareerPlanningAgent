import os
import json
from openai import OpenAI
from typing import Dict, Any, List
from main_agent.state import AgentState
from main_agent.utils.config_loader import settings
from .prompts import MAIN_AGENT_SYSTEM_PROMPT
from main_agent.tools.expert_tools import EXPERT_TOOLS_SPEC
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

class MainAgentNode:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings['llm']['api_key'],
            base_url=settings['llm']['base_url'],
        )
        self.model = "qwen3.5-plus"
        
    def _build_messages(self, state: AgentState) -> List[Dict]:
        # 1. 基础系统提示词
        messages = [{"role": "system", "content": MAIN_AGENT_SYSTEM_PROMPT}]
        
        # 2. 注入简历文本 (如果已获取)
        resume_text = state.get("resume_text")
        if resume_text:
            resume_context = f"""
【用户上传的简历内容原文】
---
{resume_text}
---
注意：请基于上述简历内容，在需要时调用 `get_student_profile` 工具进行深度结构化建模。
"""
            messages.append({"role": "system", "content": resume_context})
        
        # 3. 注入系统状态辅助信息
        status_info = f"""
【系统当前数据状态】
- 简历文本: {"✅ 已获取" if resume_text else "❌ 缺失"}
- 学生画像: {"✅ 已生成" if state.get("student_profile") else "❌ 未生成"}
- 目标岗位: {state.get("target_job_name") or "未明确"}
- 岗位画像: {"✅ 已获取" if state.get("job_profile") else "❌ 未获取"}
- 匹配结果: {"✅ 已生成" if state.get("match_result") else "❌ 未生成"}
"""
        messages.append({"role": "system", "content": status_info})

        # 4. 添加历史对话（用户消息、AI回复、工具返回结果）
        for m in state['messages']:
            if isinstance(m, HumanMessage):
                messages.append({"role": "user", "content": m.content})
            elif isinstance(m, AIMessage):
                msg_dict = {"role": "assistant", "content": m.content}
                if m.additional_kwargs.get("tool_calls"):
                    msg_dict["tool_calls"] = m.additional_kwargs["tool_calls"]
                messages.append(msg_dict)
            elif isinstance(m, ToolMessage):
                messages.append({
                    "role": "tool",
                    "tool_call_id": m.tool_call_id,
                    "content": m.content
                })
        return messages

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        messages = self._build_messages(state)
        
        print("\n" + "=" * 20 + " Main Agent 思考中 (ReAct) " + "=" * 20)
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=EXPERT_TOOLS_SPEC,
            extra_body={"enable_thinking": True},
            stream=True
        )
        
        full_content = ""
        is_answering = False
        tool_calls_dict = {} # 用于累积流式输出中的 tool_calls

        for chunk in completion:
            delta = chunk.choices[0].delta
            # 1. 打印思考内容
            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                if not is_answering:
                    print(delta.reasoning_content, end="", flush=True)
            
            # 2. 处理回复内容
            if hasattr(delta, "content") and delta.content:
                if not is_answering:
                    print("\n" + "=" * 20 + " Agent 回复 " + "=" * 20)
                    is_answering = True
                print(delta.content, end="", flush=True)
                full_content += delta.content
                
            # 3. 处理工具调用 (Function Calling)
            if hasattr(delta, "tool_calls") and delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls_dict:
                        tool_calls_dict[idx] = {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": "", "arguments": ""}
                        }
                    if tc.function.name:
                        tool_calls_dict[idx]["function"]["name"] += tc.function.name
                    if tc.function.arguments:
                        tool_calls_dict[idx]["function"]["arguments"] += tc.function.arguments

        print("\n" + "=" * 50)
        
        # 整理工具调用结果
        tool_calls = list(tool_calls_dict.values()) if tool_calls_dict else None
        
        # 如果有工具调用，打印一下
        if tool_calls:
            for tc in tool_calls:
                print(f"[决策] 调用工具: {tc['function']['name']}({tc['function']['arguments']})")

        return {
            "messages": [AIMessage(
                content=full_content,
                additional_kwargs={"tool_calls": tool_calls} if tool_calls else {}
            )],
            "next_step": "tools" if tool_calls else "end"
        }
