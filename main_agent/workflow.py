import json
from langgraph.graph import StateGraph, START, END
from main_agent.state import AgentState
from main_agent.nodes.supervisor import MainAgentNode
from main_agent.tools.expert_tools import (
    get_student_profile, 
    get_job_profile, 
    analyze_match, 
    search_main_knowledge_base
)
from langchain_core.messages import ToolMessage, AIMessage

# 工具映射表
TOOL_MAP = {
    "get_student_profile": get_student_profile,
    "get_job_profile": get_job_profile,
    "analyze_match": analyze_match,
    "search_main_knowledge_base": search_main_knowledge_base
}

def tool_node(state: AgentState):
    """
    统一的工具执行节点 (Acting & Observation)
    """
    last_message = state["messages"][-1]
    if not hasattr(last_message, "additional_kwargs") or "tool_calls" not in last_message.additional_kwargs:
        return {"messages": []}

    tool_calls = last_message.additional_kwargs.get("tool_calls", [])
    
    new_messages = []
    updates = {}

    for tool_call in tool_calls:
        name = tool_call["function"]["name"]
        args_str = tool_call["function"]["arguments"]
        try:
            args = json.loads(args_str)
        except Exception as e:
            print(f"[ToolNode] 解析参数失败: {args_str}, 错误: {e}")
            args = {}
        
        # 执行工具
        if name in TOOL_MAP:
            # 统一注入 state_data 以便工具内部获取 resume_text 等
            result_str = TOOL_MAP[name](state_data=state, **args)
            
            # 包装成 ToolMessage
            new_messages.append(ToolMessage(
                tool_call_id=tool_call["id"],
                content=result_str
            ))
            
            # 同步更新状态中的结构化数据
            try:
                res_data = json.loads(result_str)
                if name == "get_student_profile":
                    updates["student_profile"] = res_data
                elif name == "get_job_profile":
                    updates["job_profile"] = res_data
                elif name == "analyze_match":
                    updates["match_result"] = res_data
            except:
                pass

    return {
        "messages": new_messages,
        **updates
    }

def router(state: AgentState):
    """
    路由逻辑：继续工具循环或结束
    """
    next_step = state.get("next_step", "end")
    if next_step == "tools":
        return "tools"
    return END

def create_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", MainAgentNode())
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    
    workflow.add_conditional_edges(
        "agent",
        router,
        {
            "tools": "tools",
            END: END
        }
    )

    workflow.add_edge("tools", "agent")

    return workflow.compile()
