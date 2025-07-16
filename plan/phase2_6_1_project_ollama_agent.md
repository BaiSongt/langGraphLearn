
# 阶段二：实践项目 | 6.1. 构建 Ollama 工具调用 Agent

**目标：** 整合第二阶段的所有知识点（循环、状态累积），连接到一个真实的 LLM（Ollama `qwen3:4b`），并赋予它执行 Python 工具的能力，最终构建一个有记忆、能行动的 Agent。

**项目描述：** 我们将构建一个研究助手 Agent。用户可以向它提问，Agent 会利用一个真实的网页搜索工具（Tavily Search）来查找信息，然后根据搜索结果整合出最终答案。我们将清晰地看到“思考-行动-观察”的完整循环。

---

### 前置准备

1.  **安装 Ollama:** 确保你的电脑上已经安装了 Ollama，并拉取了 `qwen3:4b` 模型。
    ```bash
    ollama pull qwen3:4b
    ```
2.  **安装必要的 Python 库:**
    ```bash
    pip install langgraph langchain_core langchain-ollama langchain-openai tavily-python
    ```
3.  **获取 API Key (可选):**
    -   如果你想使用 Tavily 搜索工具，请前往 [Tavily AI](https://tavily.com/) 获取一个免费的 API Key，并将其设置为环境变量 `TAVILY_API_KEY`。
    -   如果你想尝试 OpenAI 的模型，也需要设置相应的 `OPENAI_API_KEY`。

---

### 项目流程图

这是我们即将构建的 Agent 的完整工作流程。

```mermaid
graph TD
    A[Start] --> B{Agent Node: 调用 LLM 思考};
    B --> C{Router: 检查 LLM 的回复};
    C -->|回复中包含 Tool Calls| D[Tool Node: 执行搜索工具];
    C -->|回复中不含 Tool Calls| E[END];
    D --> B; // 关键的循环边：将工具结果带回给 Agent 再思考
```

---

### 分步实现指南

**对应的代码示例文件是 `src/phase2_tool_agent.py`。**

#### 步骤 1: 导入与环境设置

```python
import os
import operator
from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_ollama.chat_models import ChatOllama
# from langchain_openai import ChatOpenAI # 如果使用 OpenAI API，取消此行注释
from langgraph.graph import StateGraph, END

# (可选) 如果你想使用 LangSmith 调试，请设置以下环境变量
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = "YOUR_LANGSMITH_API_KEY"

# (可选) 设置 Tavily API Key
# os.environ["TAVILY_API_KEY"] = "YOUR_TAVILY_API_KEY"
```

#### 步骤 2: 定义工具 (Tools)

我们将使用 `TavilySearchResults` 作为我们的核心工具。`@tool` 装饰器可以轻松地将任何 Python 函数转换为 LangChain 工具。

```python
# TavilySearchResults 已经是一个预构建好的工具类
# 我们也可以用 @tool 装饰器自己定义一个
@tool
def simple_search(query: str):
    """一个简单的网页搜索工具。"""
    search_tool = TavilySearchResults(max_results=2)
    return search_tool.invoke({"query": query})

tools = [simple_search]
```

#### 步骤 3: 定义 LLM 并绑定工具

这是关键一步。我们告诉 LLM 有哪些工具可供它使用。

```python
# --- 使用 Ollama --- 
# model="qwen3:4b" 是你本地运行的模型名称
llm = ChatOllama(model="qwen3:4b", temperature=0)

# --- (备选) 使用 OpenAI API --- 
# from langchain_openai import ChatOpenAI
# os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
# llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 将工具列表绑定到 LLM
# 这会告诉 LLM 在需要时可以调用这些工具
llm_with_tools = llm.bind_tools(tools)
```

#### 步骤 4: 定义 Agent 状态

我们的状态只需要一个 `messages` 列表，但必须使用 `Annotated` 和 `operator.add` 来确保对话历史可以被**累积**。

```python
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]
```

#### 步骤 5: 定义图的节点 (Nodes)

-   **`agent_node`**: 调用绑定了工具的 LLM。
-   **`tool_node`**: 解析 LLM 的 `tool_calls` 并执行相应的工具。

```python
from langgraph.prebuilt import ToolNode

# Agent 节点：调用 LLM
def agent_node(state: AgentState):
    print("---AGENT NODE---")
    response = llm_with_tools.invoke(state['messages'])
    return {"messages": [response]}

# Tool 节点：LangGraph 提供了预构建的 ToolNode，非常方便
# 它会自动执行 AIMessage 中请求的工具，并返回 ToolMessage
tool_node = ToolNode(tools)
```

#### 步骤 6: 定义条件路由

路由函数检查最新的消息。如果它是一条包含 `tool_calls` 的 `AIMessage`，就路由到工具节点；否则，就结束。

```python
def router(state: AgentState) -> str:
    print("---ROUTER---")
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        # 如果 LLM 请求调用工具，则路由到工具节点
        return "tools"
    else:
        # 否则，结束流程
        return "__end__"
```

#### 步骤 7: 构建并编译图

```python
workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges("agent", router)

# 创建循环边
workflow.add_edge("tools", "agent")

app = workflow.compile()
```

#### 步骤 8: 运行 Agent

现在，让我们向 Agent 提问，并观察它的思考-行动循环。

```python
# 使用 .stream() 来观察每一步的状态变化
inputs = {"messages": [HumanMessage(content="LangGraph 和 LangChain 的关系是什么？它们各自最适合做什么？")]}

for event in app.stream(inputs, {"recursion_limit": 10}):
    for message in event.get("messages", []):
        message.pretty_print()
    print("----")
```

当你运行这段代码时，你会清晰地看到 Agent 首先调用 LLM，LLM 决定使用搜索工具，然后 `ToolNode` 执行搜索，结果被添加回状态，流程再次回到 Agent 节点，Agent 根据搜索结果生成最终答案，最后流程结束。

---

## LLM 相关知识: `bind_tools` 的魔力

`llm.bind_tools(tools)` 是一个非常重要的方法。它在背后做了什么？

它获取了你提供的 `tools` 列表，并将每个工具的结构（函数名、参数、描述）转换成一个符合特定 LLM API 要求的 JSON Schema。然后，它将这个 Schema “绑定”到 LLM 实例上。从此以后，每次你调用这个 `llm_with_tools` 实例时，LangChain 会自动将工具的 Schema 附加到发送给 LLM 的 API 请求中。这就是 LLM 如何知道“我有哪些工具可以用”的秘密。

## 相关 Python 语法详解

### 1. `@tool` 装饰器

-   **语法**: 将 `@tool` 放在一个函数定义的正上方。
-   **功能**: 这是 `langchain_core.tools` 提供的一个语法糖。它接收一个普通的 Python 函数，并自动地：
    1.  读取函数的名称 (`simple_search`)。
    2.  通过内省（Introspection）分析函数的参数 (`query: str`) 和类型提示。
    3.  读取函数的文档字符串 (`"""一个简单的网页搜索工具。"""`) 作为工具的描述。
    4.  将以上所有信息打包成一个标准的 `Tool` 对象。
-   **好处**: 让你无需手动实例化 `Tool` 类，代码更简洁、更 Pythonic。

### 2. 环境变量 `os.getenv()`

-   **语法**: `os.getenv("ENV_VAR_NAME", "default_value")`
-   **功能**: 安全地从你的操作系统环境变量中读取一个值。如果该环境变量不存在，它会返回 `None` 或你指定的默认值。
-   **最佳实践**: **永远不要**将 API Key、密码等敏感信息硬编码在你的代码里。将其存储在环境变量中，并通过 `os.getenv` 来读取，是一种安全、灵活的最佳实践。这使得你的代码可以被安全地分享或提交到版本控制中，而不会泄露敏感信息。
