
# 本示例代码对应 plan 文件夹中的以下文档：
# - 阶段四：实践项目 | 11.1. 集成 LangSmith 调试 (phase4_11_1_project_langsmith_integration.md)

import os
from dotenv import load_dotenv
import operator
import uuid
import sqlite3
from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver

# --- API Key & LangSmith Setup ---
# 在真实项目中，请从操作系统环境变量中读取这些值。
# 为了方便本次交互式学习，我们在此处直接设置。
load_dotenv()

# 从环境变量中获取 API Key，如果未设置则抛出异常
if not os.getenv("DEEPSEEK_API_KEY"):
    raise ValueError("DEEPSEEK_API_KEY not set")
if not os.getenv("LANGCHAIN_API_KEY"):
    raise ValueError("LANGCHAIN_API_KEY not set")
os.environ["LANGCHAIN_PROJECT"] = "LangGraph Learning" # (可选) 指定项目名称

# 1. 定义工具
@tool
def write_summary_to_file(filename: str, summary: str):
    """将会议总结写入指定的 Markdown 文件。"""
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
        return "tools"
    else:
        return "__end__"

# 5. 构建并编译带中断的图
conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
memory = SqliteSaver(conn=conn)

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", router)
workflow.add_edge("tools", "__end__")

app = workflow.compile(checkpointer=memory, interrupt_before=["tools"])

# 6. 编写交互式运行逻辑
def run_agent():
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}
    
    initial_prompt = "请总结一次关于 LangGraph 项目的会议，并保存到 a_new_summary.md 文件中。"
    inputs = {"messages": [HumanMessage(content=initial_prompt)]}

    print(f"--- 开始新会话 (ID: {session_id}) ---")
    print("请注意：本次运行的轨迹将被发送到 LangSmith。")
    
    for event in app.stream(inputs, config, stream_mode="values"):
        event["messages"][-1].pretty_print()

    current_state = app.get_state(config)
    tool_call = current_state.values['messages'][-1].tool_calls[0]

    print("\n--- AGENT 已暂停 ---")
    print(f"Agent 准备调用工具: {tool_call['name']}")
    
    user_approval = input("是否批准执行此操作？ (yes/no): ")

    if user_approval.lower() == "yes":
        print("--- 用户已批准，继续执行 ---")
        for event in app.stream(None, config, stream_mode="values"):
            event['messages'][-1].pretty_print()
        print("--- 流程结束 ---")
    else:
        print("--- 用户已拒绝，操作取消 ---")

if __name__ == "__main__":
    run_agent()
