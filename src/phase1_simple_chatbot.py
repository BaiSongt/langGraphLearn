

# 本示例代码对应 plan 文件夹中的以下文档：
# - 阶段一：核心概念 | 3.1. 构建简单问答机器人 (phase1_3_1_project_simple_chatbot.md)

import random
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

class SimpleBotState(TypedDict):
    """定义我们应用的状态"""
    question: str
    answer: str | None
    next_node: Literal["tool_node", "__end__"] # __end__ 是一个特殊的路由目标，代表结束

def agent_node(state: SimpleBotState) -> dict:
    """分析问题，决定是直接回答还是使用工具。"""
    print("---AGENT NODE---")
    question = state["question"]

    if "langgraph" in question.lower():
        print("决策：问题复杂，需要使用工具。")
        # 返回对状态的更新，告诉路由函数下一步去 tool_node
        return {"next_node": "tool_node"}
    else:
        print("决策：问题简单，直接回答。")
        simple_answer = f"对 '{question}' 的简单回答是：这是一个秘密！"
        # 返回更新，包含答案并告诉路由函数结束
        return {"answer": simple_answer, "next_node": "__end__"}

def tool_node(state: SimpleBotState) -> dict:
    """模拟工具节点，处理复杂问题。"""
    print("---TOOL NODE---")
    question = state["question"]
    tool_answer = f"通过工具查找到的答案是：LangGraph 是一个用于构建有状态 LLM 应用的库。"
    return {"answer": tool_answer}

def router(state: SimpleBotState) -> Literal["tool_node", "__end__"]:
    """根据 state['next_node'] 的值来决定路由方向。"""
    print("---ROUTER---")
    return state['next_node']

# 1. 初始化 StateGraph
workflow = StateGraph(SimpleBotState)

# 2. 添加节点
workflow.add_node("agent", agent_node)
workflow.add_node("tool", tool_node)

# 3. 设置入口点
workflow.set_entry_point("agent")

# 4. 添加条件边
workflow.add_conditional_edges(
    "agent",
    router,
    {
        "tool_node": "tool", # 如果 router 返回 "tool_node", 则去 "tool" 节点
        "__end__": END       # 如果返回 "__end__", 则结束
    }
)

# 5. 添加常规边
workflow.add_edge("tool", END)

# 6. 编译图
app = workflow.compile()

# --- 测试案例 1: 简单问题 ---
print("\n--- 开始测试简单问题 ---")
inputs1 = {"question": "你好吗？"}
final_state1 = app.invoke(inputs1)
print(f"最终答案: {final_state1['answer']}")

# --- 测试案例 2: 复杂问题 ---
print("\n--- 开始测试复杂问题 ---")
inputs2 = {"question": "请问什么是 LangGraph？"}
final_state2 = app.invoke(inputs2)
print(f"最终答案: {final_state2['answer']}")

