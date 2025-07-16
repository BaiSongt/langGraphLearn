
# -----------------------------------------------------------------------------
# 欢迎来到 LangGraph AI 聊天应用!
#
# 本文件是整个应用的核心，它定义了 AI Agent 的大脑、工具、记忆和工作流程。
# 我们将在这里综合运用之前学到的所有 LangGraph 知识。
# -----------------------------------------------------------------------------

# --- 核心库导入 ---
# Python 标准库
import os
import operator
import sqlite3
from typing import TypedDict, Annotated, List

# LangChain & LangGraph 库
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver

# --- Python 语法详解: `import` ---
# `import` 语句用于将其他 Python 文件（称为模块）中的代码引入到当前文件中。
# `from ... import ...` 允许我们从一个模块中只引入特定的类或函数，
# 这样我们就可以直接使用它们的名字（如 `StateGraph`），而不需要写完整的路径（如 `langgraph.graph.StateGraph`）。


# --- 步骤 1: 设置 API Keys ---
# 最佳实践是从操作系统的环境变量中读取敏感信息，而不是将它们硬编码在代码里。
# `os.getenv("KEY_NAME")` 会安全地读取环境变量。如果不存在，它会返回 None。
# 为了方便运行，如果环境变量不存在，我们在此处提供一个备用的假 Key，但这会导致程序在调用 API 时失败。
# 请确保您已经在您的环境中正确设置了这些环境变量。
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY", "sk-a37f15cbba404a3fa708d07c925fc38c")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY", "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")


# --- 步骤 2: 定义 Agent 可以使用的工具 (Tools) ---
# "工具"是 Agent 可以执行的特殊函数，用来与外部世界交互（如搜索、读文件等）。
@tool
def search_tool(query: str):
    """当需要回答关于最新事件、人物或具体事实的问题时，使用此工具进行网页搜索。"""
    # --- Python 语法详解: `@tool` 装饰器 ---
    # 这是一个“装饰器”。装饰器是一个函数，它接收另一个函数作为输入，并返回一个新的函数，
    # 通常用于在不修改原函数代码的情况下增加额外功能。
    # LangChain 的 `@tool` 装饰器会自动将这个 Python 函数转换成一个 LLM 可以理解和调用的“工具”对象。
    # 它会自动解析函数名、文档字符串（作为工具描述）和参数类型。
    print(f"---TOOL: 正在执行搜索，查询: '{query}'---")
    try:
        search_results = TavilySearch(max_results=3).invoke(query)
        return search_results
    except Exception as e:
        # --- Python 语法详解: `try...except` ---
        # 这是一个异常处理块。`try` 中的代码会被尝试执行。
        # 如果在执行过程中发生任何错误（例如，网络问题、API Key 无效），
        # 程序不会崩溃，而是会跳转到 `except` 块中执行，并将错误信息赋值给变量 `e`。
        # 这使得我们的工具更加健壮。
        return f"搜索时发生错误: {e}"

# 将所有我们希望 Agent 使用的工具放入一个列表中。
tools = [search_tool]


# --- 步骤 3: 定义 Agent 的状态 (State) ---
# Agent 的“状态”是其记忆的载体。它是一个在整个对话过程中被持续传递和更新的对象。
class AgentState(TypedDict):
    """定义了我们 Agent 记忆的结构。"""
    # `messages` 字段将存储一个消息列表，记录了整个对话历史。
    messages: Annotated[List[AnyMessage], operator.add]
    # --- Python 语法详解: `TypedDict` & `Annotated` ---
    # `TypedDict`: 让我们像定义一个类一样，为一个字典规定好它必须包含哪些键，以及每个键对应的值是什么类型。
    #             这提供了代码自动补全和静态类型检查，让代码更健壮。
    # `Annotated[List, operator.add]`: 这是一个高级类型提示。它告诉 LangGraph，
    #             当更新 `messages` 字段时，不要用新列表“替换”旧列表，
    #             而是应该用 `operator.add`（等同于 `+`）将新消息“追加”到旧列表的末尾。
    #             这是实现对话历史累积的关键。


# --- 步骤 4: 定义图的节点 (Nodes) 和边 (Edges) ---
# 我们的图由几个“节点”和连接它们的“边”组成，定义了 Agent 的工作流程。

# 节点 1: Agent 节点 (大脑)
# 这个节点负责调用 LLM 进行思考和决策。
def agent_node(state: AgentState):
    """调用 LLM 来决定下一步行动。"""
    print("---AGENT: 思考中...---")
    # `llm_with_tools.invoke` 会将当前的所有消息历史发送给 LLM。
    # LLM 会根据历史和它被绑定的工具，决定是直接回答，还是请求调用工具。
    response = llm_with_tools.invoke(state['messages'])
    # 节点必须返回一个字典，这个字典会被用来更新状态。
    return {"messages": [response]}

# 节点 2: Tool 节点 (手臂)
# 这个节点负责执行 Agent 请求的工具调用。
# LangGraph 提供了预构建的 `ToolNode`，它会自动处理工具的解析和执行，非常方便。
tool_node = ToolNode(tools)

# 边: 条件路由 (决策中心)
# 这条边决定了在 Agent 思考之后，流程应该走向何方。
def router(state: AgentState) -> str:
    """根据 Agent 的最新回复，决定下一步是调用工具还是结束。"""
    print("---ROUTER: 决策中...---")
    # 获取消息列表中的最后一条消息。
    last_message = state['messages'][-1]
    # --- Python 语法详解: `hasattr` & `.tool_calls` ---
    # `hasattr(object, 'attribute_name')`: 检查一个对象是否有名为 'attribute_name' 的属性。
    #                                    这里用来安全地检查 `last_message` 是否有 `tool_calls` 属性。
    # `.tool_calls`: 如果 LLM 决定调用工具，它返回的 AIMessage 对象就会包含一个非空的 `tool_calls` 列表。
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print("---ROUTER: 决定调用工具。---")
        return "tools" # 返回字符串 "tools"，告诉图走向工具节点。
    else:
        print("---ROUTER: 决定直接回复。---")
        return "__end__" # 返回特殊字符串 `__end__`，告诉图这个流程分支结束了。


# --- 步骤 5: 构建并编译图 (Graph) ---
# 现在，我们将上面定义的所有组件组装成一个可执行的图。

# 初始化 LLM 并绑定工具
llm = ChatDeepSeek(model="deepseek-chat", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# 初始化图状态
workflow = StateGraph(AgentState)

# 添加节点到图中
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

# 设置图的入口点
workflow.set_entry_point("agent")

# 添加条件边
workflow.add_conditional_edges("agent", router)

# 添加常规边，创建循环
# 这条边是 Agentic Loop 的关键：工具执行完毕后，流程返回给 Agent 节点，
# 让 Agent 可以根据工具返回的结果进行下一步思考。
workflow.add_edge("tools", "agent")

# 设置持久化/记忆
# `SqliteSaver` 会将每一次对话的状态都保存到一个 SQLite 数据库文件中。
# `check_same_thread=False` 是在多线程应用中使用 SQLite 的一个必要设置。
conn = sqlite3.connect("chat_history.sqlite", check_same_thread=False)
memory = SqliteSaver(conn=conn)

# 编译图，并为其配备记忆功能
# `interrupt_before=["tools"]` 是一个可选的调试功能，我们暂时不启用它。
chatapp = workflow.compile(checkpointer=memory)

print("AI 聊天应用已成功初始化！")
