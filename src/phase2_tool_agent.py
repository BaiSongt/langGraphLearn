
# 本示例代码对应 plan 文件夹中的以下文档：
# - 阶段二：实践项目 | 6.1. 构建 Ollama 工具调用 Agent (phase2_6_1_project_ollama_agent.md)

import os
import operator
from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

# --- API Key Setup ---
# 在真实项目中，请从环境变量中读取这些值。
# 为了方便本次交互式学习，我们在此处直接设置。
os.environ["TAVILY_API_KEY"] = "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"
os.environ["DEEPSEEK_API_KEY"] = "sk-a37f15cbba404a3fa708d07c925fc38c"
os.environ["GEMINI_API_KEY"] = "AIzaSyDD2mPMXWr6nxG5HqccrbsdHC_UA1qV_sk"

# --- 模型选择 ---
# 在这里切换你想要使用的模型: 'deepseek' 或 'gemini'
MODEL_TO_USE = "gemini"

# 1. 定义工具
@tool
def simple_search(query: str):
    """一个简单的网页搜索工具，用于查找关于技术、事件或人物的最新信息。"""
    try:
        search_tool = TavilySearch(max_results=3)
        return search_tool.invoke(query)
    except Exception as e:
        return f"搜索工具遇到错误: {e}"

tools = [simple_search]

# 2. 根据选择初始化 LLM 并绑定工具
if MODEL_TO_USE == 'deepseek':
    print("--- 使用 DeepSeek 模型 ---")
    llm = ChatDeepSeek(model="deepseek-chat", temperature=0)
elif MODEL_TO_USE == 'gemini':
    print("--- 使用 Gemini 模型 ---")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, google_api_key=os.getenv("GEMINI_API_KEY"))
else:
    raise ValueError(f"未知的模型: {MODEL_TO_USE}")

llm_with_tools = llm.bind_tools(tools)

# 3. 定义 Agent 状态
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]

# 4. 定义图的节点
def agent_node(state: AgentState):
    print("---AGENT NODE---")
    response = llm_with_tools.invoke(state['messages'])
    return {"messages": [response]}

tool_node = ToolNode(tools)

# 5. 定义条件路由
def router(state: AgentState) -> str:
    print("---ROUTER---")
    last_message = state['messages'][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        print("决策：调用工具")
        return "tools"
    else:
        print("决策：结束")
        return "__end__"

# 6. 构建并编译图
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", router)
workflow.add_edge("tools", "agent")
app = workflow.compile()

# 7. 运行 Agent
def run_agent():
    prompt = "你必须使用搜索工具来回答以下问题：LangGraph 和 LangChain 的关系是什么？它们各自最适合做什么？"
    inputs = {"messages": [HumanMessage(content=prompt)]}

    print(f"--- 开始执行 Agent (模型: {MODEL_TO_USE}) ---")
    for event in app.stream(inputs, {"recursion_limit": 10}):
        messages = event.get("messages", [])
        if messages:
            messages[-1].pretty_print()
        print("----")

if __name__ == "__main__":
    run_agent()
