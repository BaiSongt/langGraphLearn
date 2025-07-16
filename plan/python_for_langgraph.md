
# Python for LangGraph: 核心知识点

掌握 LangGraph 不仅仅是学习其 API，更需要理解其背后依赖的 Python 特性。本文档旨在为你梳理学习 LangGraph 所需的核心 Python 知识。

---

## 1. Python 基础回顾

### 1.1. 函数是一等公民 (Functions are First-Class Citizens)

**核心概念**: 在 Python 中，函数和其他数据类型（如整数、字符串、列表）的地位是相同的。这意味着你可以：
-   将函数赋值给一个变量。
-   将函数作为参数传递给另一个函数。
-   让函数返回一个函数。

**与 LangGraph 的关系**: 这是 LangGraph API 设计的基石。`workflow.add_node` 和 `workflow.add_conditional_edges` 等方法都要求你传入一个函数作为参数。

```python
# 示例：将函数作为参数传递
def say_hello(name):
    print(f"Hello, {name}")

def greet(greeter_func, person_name):
    # 调用传入的函数
    greeter_func(person_name)

# 将 say_hello 函数传递给 greet 函数
greet(say_hello, "Alice") # 输出: Hello, Alice

# 在 LangGraph 中，你也是这么做的：
# workflow.add_node("my_node", say_hello_node) # 此处 say_hello_node 就是一个函数
```

### 1.2. 字典 (dict) 操作

**核心概念**: 字典是 Python 中非常重要的数据结构。对于 LangGraph，你需要熟悉以下操作：
-   `get(key, default)`: 安全地获取键值，如果键不存在，可以返回一个默认值。
-   `update(other_dict)`: 用另一个字典的键值对来更新当前字典。如果键已存在，则覆盖；如果不存在，则添加。

**与 LangGraph 的关系**: LangGraph 的节点返回一个字典，这个字典通过 `update` 的方式合并到主状态（State）中。理解这一点有助于你预测状态的变化。

```python
# 初始状态
state = {"question": "What is LangGraph?", "answer": None}

# 节点返回的更新
node_return = {"answer": "It is a library for building stateful agents."}

# LangGraph 内部会这样做：
state.update(node_return)

print(state)
# 输出: {'question': 'What is LangGraph?', 'answer': 'It is a library for building stateful agents.'}
```

---

## 2. Python 类型提示 (Type Hinting)

类型提示让代码更易读、更健壮，是现代 Python 开发的最佳实践。

### 2.1. `typing` 模块基础
-   `List`, `Dict`, `Any`, `Tuple`: 用于描述集合类型。
-   `Literal`: 用于限定一个变量只能是某几个特定的值。在 LangGraph 中常用于定义路由决策的可能结果。

### 2.2. `TypedDict`

**核心概念**: `TypedDict` 允许你像定义一个类一样，为一个字典规定好它应该包含哪些键，以及每个键对应的值是什么类型。

**与 LangGraph 的关系**: 这是定义 `GraphState` 的**首选方式**。它能让你的 IDE（如 VSCode）在你访问状态时提供自动补全，并检查你是否写错了键名，极大地提升了开发效率和代码稳定性。

```python
from typing import TypedDict, List

class GraphState(TypedDict):
    question: str
    answer: str | None # `| None` 表示这个值可以是字符串或 None
    tool_calls: List[dict]

# 使用 TypedDict 的好处
def my_node(state: GraphState):
    # 当你输入 state['...'] 时，IDE 会提示 question, answer, tool_calls
    # 如果你写了 state['quesiton'] (拼写错误)，静态检查工具会报错
    pass
```

### 2.3. `Annotated`

**核心概念**: `Annotated` (Python 3.9+) 是一个高级类型工具，它允许你为一个类型附加额外的元数据。它的语法是 `Annotated[SomeType, metadata1, metadata2]`。

**与 LangGraph 的关系**: 这是 LangGraph 中实现**状态累积**的“魔法”。LangGraph 会检查类型注解，如果发现是 `Annotated[list, operator.add]`，它就不会用新列表“替换”旧列表，而是将两个列表“相加”（追加内容）。

```python
import operator
from typing import Annotated, List
from langchain_core.messages import AnyMessage

class AgentState(TypedDict):
    # 这里的 operator.add 就是附加的元数据
    # 它告诉 LangGraph 如何处理对 messages 字段的更新
    messages: Annotated[List[AnyMessage], operator.add]
```

---

## 3. Python 中高级编程

### 3.1. 类与对象 (Classes and Objects)

**核心概念**: 类是创建对象的蓝图。你可以用类来封装数据（属性）和行为（方法）。

**与 LangGraph 的关系**: 虽然 LangGraph 的节点通常是函数，但将你的**工具 (Tools)** 定义为类是一种非常好的实践。这样可以把工具的逻辑和状态封装在一起。

```python
class WebSearchTool:
    def __init__(self, api_key: str):
        self.api_key = api_key
        print("Tool initialized.")

    def search(self, query: str) -> str:
        # ... 使用 self.api_key 调用外部 API 的逻辑 ...
        return f"Search results for '{query}'"

# 在图中，你可以实例化这个工具并使用它
# search_tool = WebSearchTool(api_key="YOUR_KEY")
# result = search_tool.search("LangGraph")
```

### 3.2. 装饰器与闭包 (Advanced)

这些是更高级的概念，不直接要求，但理解有益。
-   **装饰器**: 一个函数，它接收另一个函数作为参数，并返回一个新的函数，通常用于在不修改原函数代码的情况下增加额外功能（如日志、计时）。
-   **闭包**: 一个函数“记住”了它被创建时所处的环境（即其外部作用域的变量），即使外部函数已经执行完毕。

---

## 4. 常用标准库

### 4.1. `operator` 模块

**核心概念**: 这个模块提供了一系列函数，功能上对应 Python 的内置运算符。
-   `operator.add(a, b)`: 等同于 `a + b`。
-   `operator.itemgetter(key)`: 返回一个可调用对象，该对象会从其操作数中获取 `key` 对应的项。

**与 LangGraph 的关系**:
-   `operator.add` 是实现 `messages` 列表累积的关键，如上文 `Annotated` 部分所述。
-   `operator.itemgetter` 在需要从复杂的状态中提取特定部分作为 LLM 输入时非常有用。

### 4.2. `functools` 模块

**核心概念**: `functools.partial` 可以将一个多参数的函数“固定”住一个或多个参数，从而创建一个新的、参数更少的函数。

**与 LangGraph 的关系**: 当你的节点函数需要一些固定的额外参数（比如一个 LLM 实例或一个工具实例）时，`partial` 非常有用，可以避免使用全局变量。

```python
from functools import partial

# 原始节点函数需要一个 llm 参数
def llm_node(state, llm):
    # ... call llm ...
    return {"answer": "..."}

# my_llm = ChatOllama(...) # 假设我们有一个 LLM 实例

# 使用 partial 创建一个符合 LangGraph 节点签名的新函数
# 这个新函数只需要 state 作为参数
# partial_llm_node = partial(llm_node, llm=my_llm)

# 现在可以将其添加到图中
# workflow.add_node("llm", partial_llm_node)
```
