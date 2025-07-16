

# 本示例代码对应 plan 文件夹中的以下文档：
# - 阶段三：实践项目 | 9.1. 构建带用户确认的 Agent (phase3_9_1_project_agent_with_confirmation.md)

import os
import operator
import uuid
from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver

# --- API Key Setup ---
# 请确保您已在操作系统环境中设置了 DEEPSEEK_API_KEY
os.environ["DEEPSEEK_API_KEY"] = "sk-a37f15cbba404a3fa708d07c925fc38c"

# 1. 定义一个“危险”的工具：写入文件
@tool
def write_summary_to_file(filename: str, summary: str):
    """将会议总结写入指定的 Markdown 文件。"""
    # 在真实应用中，这里可以添加更多的路径安全检查
    with open(f"./{filename}", "w", encoding="utf-8") as f:
        f.write(summary)
    return f"文件 '{filename}' 已成功保存。"

tools = [write_summary_to_file]

# 2. 定义 LLM 并绑定工具
llm = ChatDeepSeek(model="deepseek-chat", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# 3. 定义 Agent 状态
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]

# 4. 定义图的节点和路由
def agent_node(state: AgentState):
    print("---AGENT NODE---")
    return {"messages": [llm_with_tools.invoke(state['messages'])]}

tool_node = ToolNode(tools)

def router(state: AgentState) -> str:
    print("---ROUTER---")
    last_message = state['messages'][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        print("决策：调用工具")
        return "tools"
    else:
        print("决策：结束")
        return "__end__"

import sqlite3

# 5. 构建并编译带中断的图
conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
memory = SqliteSaver(conn=conn)

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", router)
workflow.add_edge("tools", "__end__") # 工具执行完就结束

# 核心：在编译时设置中断点！
app = workflow.compile(checkpointer=memory, interrupt_before=["tools"])

# 6. 编写交互式运行逻辑
def run_agent():
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}

    meeting_content = """
    会议主题：LangGraph 项目第三阶段规划
    参与者：AI 助手, 用户
    讨论内容：
    1. 确认需要加入人工干预机制。
    2. 决定使用文件写入工具作为“危险操作”的示例。
    结论：按计划进行，创建带用户确认的 Agent 项目。
    """
    
    initial_prompt = f"请帮我总结以下会议内容，并将其保存到名为 'meeting_summary.md' 的文件中。\n\n会议内容：\n{meeting_content}"
    inputs = {"messages": [HumanMessage(content=initial_prompt)]}

    print(f"--- 开始新会话 (ID: {session_id}) ---")
    # 第一次调用，图会运行直到中断点
    for event in app.stream(inputs, config, stream_mode="values"):
        event["messages"][-1].pretty_print()

    # --- 人工干预环节 ---
    current_state = app.get_state(config)
    last_message = current_state.values['messages'][-1]
    tool_call = last_message.tool_calls[0]

    print("\n--- AGENT 已暂停 ---")
    print(f"Agent 准备调用工具: {tool_call['name']}")
    print(f"参数: {tool_call['args']}")

    while True:
        user_approval = input("是否批准执行此操作？ (yes/no): ")
        if user_approval.lower() in ["yes", "no"]:
            break

    if user_approval.lower() == "yes":
        print("--- 用户已批准，继续执行 ---")
        for event in app.stream(None, config, stream_mode="values"):
            event['messages'][-1].pretty_print()
        print("--- 流程结束 ---")
    else:
        print("--- 用户已拒绝，操作取消 ---")

if __name__ == "__main__":
    run_agent()
