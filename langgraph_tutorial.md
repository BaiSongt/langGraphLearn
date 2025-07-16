# LangGraph 入门指南

欢迎来到 LangGraph 的世界！本指南旨在帮助你快速理解 LangGraph 的核心概念，并构建你的第一个有状态的 LLM 应用。

## 1. LangGraph 是什么？

LangGraph 是 LangChain 生态系统的一个扩展，专门用于构建**有状态、可循环**的多步应用程序。

- **为什么需要它？** 传统的 LangChain 表达式语言 (LCEL) 非常适合创建线性的、无环的工作流（DAGs）。但对于需要“思考-行动”循环的 Agent 来说，流程往往不是线性的。Agent 可能需要多次调用工具，或者根据中间结果决定下一步做什么。LangGraph 正是为这种复杂的、带有循环的流程而设计的。
- **核心思想**：将你的应用逻辑构建成一个“图”（Graph）。图由“节点”（Nodes）和“边”（Edges）组成，所有节点共享一个持续更新的“状态”（State）对象。

---

## 2. 三大核心概念

理解以下三个概念是掌握 LangGraph 的关键。

### a. 状态 (State)

**状态是你的图的“内存”**。它是一个在图的整个执行过程中被传递和修改的 Python 对象。

- **定义**：通常，我们使用 `TypedDict` 来定义状态的结构，这样做可以获得更好的代码提示和健壮性。
- **作用**：每个节点都可以读取当前的状态，并返回一个字典来更新这个状态。

```python
from typing import TypedDict, Literal

class GraphState(TypedDict):
    question: str
    answer: str | None
    next: Literal["agent", "tool", "end"] # 用于条件路由
```

### b. 节点 (Nodes)

**节点是你的图的“工人”**。它们是执行具体任务的 Python 函数。

- **输入**：每个节点函数都接收当前的 `state` 对象作为其唯一的参数。
- **输出**：节点返回一个字典。这个字典**不是**新的状态，而是对状态的**更新**。LangGraph 会自动将返回的字典合并到主状态中。

```python
def my_node(state: GraphState):
    # 执行一些逻辑...
    print(f"当前问题是: {state['question']}")
    
    # 返回一个字典来更新状态
    return {"answer": "这是一个新的答案"}
```

### c. 边 (Edges)

**边是你的图的“流程控制器”**。它们连接节点，决定了工作流的方向。

1.  **入口点 (Entry Point)**：定义图从哪个节点开始执行。
2.  **普通边 (Normal Edges)**：`A -> B`。执行完节点 A 后，固定流向节点 B。
3.  **条件边 (Conditional Edges)**：这是 LangGraph 最强大的功能。它允许你根据当前的状态动态地决定下一个节点。你需要提供一个“路由函数”，该函数读取状态并返回一个字符串，这个字符串对应着下一条边的名字。
4.  **结束点 (END)**：一个特殊的标识，表示图的执行流程结束。

---

## 3. 构建一个图：完整示例

让我们用一个实际的例子来把所有概念串联起来。这个例子将构建一个简单的问答机器人，它可以决定是直接回答问题还是先使用“搜索工具”。

### 步骤 1: 完整代码

这是我们之前在 `main.py` 中使用的完整代码。

```python
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
import random

# 1. 定义状态 (State)
class GraphState(TypedDict):
    question: str
    answer: str | None
    next: Literal["agent", "tool", "end"] 

# 2. 定义节点 (Nodes)
def agent_node(state: GraphState):
    print(f"--- 正在执行 Agent 节点 ---")
    question = state['question']
    print(f"思考问题: {question}")
    if "langgraph" in question.lower():
        print("决策: 问题比较复杂，需要使用搜索工具。")
        return {"next": "tool"}
    else:
        print("决策: 问题很简单，直接回答。")
        answer = f"这是一个简单的回答：'{question}' 的答案是 {random.randint(1, 100)}。"
        return {"answer": answer, "next": "end"}

def tool_node(state: GraphState):
    print(f"--- 正在执行 Tool 节点 ---")
    print("正在使用搜索工具查找 'LangGraph' 的资料...")
    tool_result = "LangGraph 是一个强大的库，用于构建有状态的 LLM 应用。"
    answer = f"通过搜索工具找到了答案：{tool_result}"
    return {"answer": answer, "next": "end"}

# 3. 定义条件边的路由函数
def router(state: GraphState) -> Literal["agent", "tool", "end"]:
    print(f"--- 正在执行 Router ---")
    next_step = state['next']
    print(f"路由决策: 下一步是 -> {next_step}")
    return next_step

# 4. 构建图
# 实例化一个状态图
workflow = StateGraph(GraphState)

# 添加节点
workflow.add_node("agent", agent_node)
workflow.add_node("tool", tool_node)

# 设置入口点
workflow.set_entry_point("agent")

# 添加条件边
# 从 "agent" 节点出来后，调用 router 函数决定去 "tool" 还是 "end"
workflow.add_conditional_edges(
    "agent",
    router,
    {
        "tool": "tool",
        "end": END
    }
)

# 添加普通边
# 从 "tool" 节点出来后，固定结束
workflow.add_edge("tool", END)

# 编译图，生成可执行的应用
app = workflow.compile()
```

### 步骤 2: 运行图

你可以通过 `.invoke()` 一次性获得最终结果，或者用 `.stream()` 查看每一步的执行过程。

```python
# 运行一个需要调用工具的例子
inputs = {"question": "请介绍一下 LangGraph", "next": "agent"}

# 使用 .stream() 查看中间步骤
for s in app.stream(inputs, {"recursion_limit": 5}):
    print(s)
    print("--------------------")

# 使用 .invoke() 直接获取最终结果
final_state = app.invoke(inputs, {"recursion_limit": 5})
print(f"\n最终答案: {final_state['answer']}")
```

---

## 4. 接下来学什么？

恭喜你！你已经掌握了 LangGraph 的基础。

下一步，你可以探索更高级的主题：

-   **构建循环**：修改路由逻辑，让 Agent 可以在“思考”和“行动”之间多次循环。
-   **集成真正的 LLM 和工具**：将示例中的模拟函数替换为真实的 LangChain LLM 调用和工具调用。
-   **管理更复杂的状态**：在状态中添加列表（如 `messages`）来保存对话历史，并使用 `functools.partial` 或 `operator.add` 来定义如何更新这些列表。

祝你学习愉快！
