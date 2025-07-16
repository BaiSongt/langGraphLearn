
# 阶段二：Agentic Loop | 4.1. 构建循环

**目标：** 理解 Agentic Loop（代理循环）的本质，并掌握如何通过 `add_edge` 创建一个从工具节点指回代理节点的循环边，这是构建真正 Agent 的核心技巧。

---

## Agentic Loop: Agent 思考的闭环

在第一阶段，我们的工作流是线性的：`Agent -> Tool -> End`。但在现实中，Agent 需要能够处理工具返回的结果，并根据新信息进行下一轮思考。这，就是循环。

一个典型的 Agentic Loop 如下：

1.  **Agent 思考**: LLM 分析现有信息，决定是否需要调用工具。
2.  **Tool 执行**: 如果需要，则执行工具。
3.  **Agent 观察与再思考**: 工具的结果被返回给 Agent，Agent 观察结果，然后再次进入思考阶段，决定是调用另一个工具，还是已经可以得出最终答案。

### 流程图：循环的魔力

这个流程的关键在于，Tool 节点执行完毕后，流程**返回**到了 Agent 节点，而不是走向 `END`。

```mermaid
graph TD
    A[Start] --> B{Agent Node: 思考};
    B -->|决策: 需要工具| C[Tool Node: 执行];
    B -->|决策: 问题解决| D[END];
    C --> B;  // 关键的循环边！
```
*图1: `Tool Node` 通过一条边指回 `Agent Node`，形成了思考-行动的闭环。*

--- 

## 实现循环：`add_edge("tool", "agent")`

在 LangGraph 中，实现这个循环异常简单，只需要一行代码：

```python
# workflow.add_edge("tool", "agent")
```

这行代码的字面意思是：“当名为 `tool` 的节点执行完毕后，下一个无条件地执行名为 `agent` 的节点。”

通过这条边，我们将 Agent 和 Tool 连接成了一个可以持续运转的“引擎”。Agent 负责掌舵（思考），Tool 负责提供动力（行动），直到 Agent 决定驶向终点（END）。

--- 

## LLM 相关知识：工具调用 (Tool Calling)

Agent 如何“决策”要使用哪个工具？这背后是现代 LLM 的一项核心能力：**工具调用（或函数调用）**。

当我们把工具的描述（如函数名、参数、功能说明）提供给 LLM 时，LLM 在回答我们的问题的同时，还能以一种结构化的格式（通常是 JSON）输出它想要调用的工具和相应的参数。

**简化的交互过程：**

1.  **我们 (User):** (向 LLM 的 Prompt 中加入了工具描述) "用户问：纽约现在天气怎么样？"
2.  **LLM (Agent):** (返回一个特殊的 AIMessage) "我需要调用工具。请执行 `get_weather(city="New York")`。"
3.  **我们 (Tool Executor):** 解析 LLM 的回复，执行 `get_weather` 函数，得到结果 `"15 度，晴"`。
4.  **我们 (User):** (将工具结果再次发给 LLM) "工具 `get_weather` 返回了：`15 度，晴`。"
5.  **LLM (Agent):** (返回最终答案) "纽约现在是 15 度，晴天。"

LangGraph 的 Agent 节点就是负责处理第 2 步和第 5 步，而 Tool 节点负责处理第 3 步。

--- 

## 相关 Python 语法详解

### 1. 字符串作为标识符

-   **语法**: 在 LangGraph 中，我们使用普通的 Python 字符串（如 `"agent"`, `"tool"`）来作为节点的唯一名称和边连接的“地址”。
-   **工作原理**: `StateGraph` 内部维护了一个字典，将这些字符串名称映射到你实际提供的节点函数。当你调用 `add_edge("tool", "agent")` 时，它实际上是在查找名为 `"tool"` 的函数和名为 `"agent"` 的函数，并在其内部流程图中建立连接。
-   **重要性**: 这意味着节点的命名必须是唯一的。如果你用同一个名字添加两个不同的节点，后一个会覆盖前一个。

```python
def agent_node(state):
    # ...
    return {}

def tool_node(state):
    # ...
    return {}

# workflow.add_node("agent", agent_node) # 将字符串 "agent" 与 agent_node 函数关联
# workflow.add_node("tool", tool_node)   # 将字符串 "tool" 与 tool_node 函数关联

# LangGraph 现在知道 "agent" 和 "tool" 分别代表哪个函数了
# workflow.add_edge("tool", "agent")
```

这个看似简单的机制是 LangGraph 声明式 API 的基础，它允许我们用一种非常直观和可读的方式来描述复杂的计算图。
