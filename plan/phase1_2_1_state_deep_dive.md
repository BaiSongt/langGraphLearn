
# 阶段一：核心概念 | 2.1. 详解核心组件：State

**目标：** 掌握定义 LangGraph 状态 (State) 的两种方式，并深刻理解为什么使用 `TypedDict` 是构建健壮、可维护应用的最佳实践。

---

## State: 图的蓝图

正如我们在“状态驱动架构”中所学，State 是 LangGraph 的核心。因此，清晰、准确地**定义 State 的结构**，是构建任何工作流的第一步，也是最重要的一步。

定义 State 的结构，就如同为一座建筑绘制蓝图。它规定了你的工作流中可以存储哪些信息，以及这些信息的类型是什么。

LangGraph 提供了两种定义 State 的方式：
1.  使用普通的 Python `dict` (不推荐)。
2.  使用 `typing.TypedDict` (官方推荐的最佳实践)。

--- 

## 方式一：使用普通 `dict`

你可以直接将一个普通的 Python 字典类型 `dict` 传递给 `StateGraph`。 

```python
from langgraph.graph import StateGraph

# 直接使用 dict 作为 State 的类型
workflow = StateGraph(dict)

# 节点函数也只接收一个普通的 dict
def my_node(state: dict):
    # 你可以自由地读写任何键
    question = state.get("question", "")
    return {"answer": "some answer"}

workflow.add_node("a", my_node)
# ...
```

### `dict` 的问题：过于灵活，缺乏约束

虽然简单，但这种方式在项目变大时会带来诸多问题：

-   **容易出错:** 你可能会在不同的节点中拼错同一个键名（例如，`'question'` vs `'quesiton'`），程序在运行时才会报错，甚至不报错但逻辑错误。
-   **可读性差:** 当其他人（或未来的你）阅读代码时，无法一目了然地知道 `state` 字典里到底有哪些合法的键和值的类型。
-   **无代码提示:** 你的 IDE（如 VSCode）无法提供自动补全功能，降低了开发效率。

--- 

## 方式二：使用 `TypedDict` (最佳实践)

`TypedDict` 是 Python `typing` 模块提供的一个工具，它允许你为一个字典定义一个明确的“形状”或“模式”。

```python
from typing import TypedDict, List
from langgraph.graph import StateGraph

# 1. 定义一个继承自 TypedDict 的类
class AgentState(TypedDict):
    question: str
    answer: str | None # 值可以是 str 或 None
    history: List[str]

# 2. 将这个类传递给 StateGraph
workflow = StateGraph(AgentState)

# 3. 在节点中使用这个类型注解
def my_node(state: AgentState):
    # 当你输入 state['...'] 时，IDE 会自动提示
    # question, answer, history
    current_question = state['question'] 
    return {"answer": "some answer"}
```

### `TypedDict` vs. `dict` 详细对比

| 特性 | 普通 `dict` | `TypedDict` |
| :--- | :--- | :--- |
| **代码健壮性** | 差 (运行时才可能发现错误) | **高** (静态检查工具可提前发现拼写和类型错误) |
| **可读性** | 差 (需要读遍所有节点才能猜出结构) | **高** (State 结构一目了然) |
| **开发效率** | 低 (无自动补全) | **高** (IDE 提供精准的键名自动补全) |
| **约束力** | 无 | 强，像一份清晰的契约 |

**结论：** 永远优先使用 `TypedDict` 来定义你的 State。这是一种前期投入少量精力，后期节省大量调试时间和维护成本的明智之举。

--- 

## State 的初始化

无论你用哪种方式定义 State，当你开始运行一个图时，你需要提供一个**初始状态**。这个初始状态就是图执行的起点。

初始状态是一个字典，它的键必须符合你定义的 `TypedDict`（或你期望的 `dict` 结构）。

```python
# 假设我们已经编译好了图
# app = workflow.compile()

# 定义一个符合 AgentState 结构的初始状态字典
initial_state = {
    "question": "How does LangGraph work?",
    "answer": None, # 可以是 None
    "history": [] # 列表可以是空的
}

# 将初始状态传入 .stream() 或 .invoke() 方法
# for event in app.stream(initial_state):
#     print(event)
```

正确地定义和初始化 State，是保证 LangGraph 工作流能够顺利、可靠执行的第一步。
