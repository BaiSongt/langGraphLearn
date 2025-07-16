
# 阶段三：可靠性 | 8.2. 中断后的检查与恢复机制

**目标：** 掌握在图中断后，用于检查、修改和恢复执行的具体 API，包括 `get_state` 和 `update_state`，以及如何通过再次调用 `stream`/`invoke` 来继续执行。

---

## 与暂停的图进行交互

当一个图因为 `interrupt_before` 而暂停时，它不是“死”了，而是进入了一种“待命”状态。它完整地保留了当前的状态，并等待外部指令来决定下一步做什么。我们有三种核心的交互方式：

1.  **检查 (Get):** 查看图当前的完整状态，以了解 Agent 的意图。
2.  **修改 (Update):** (可选) 在恢复执行前，手动修改图的状态。这允许我们“纠正”Agent 的行为。
3.  **继续 (Continue):** 让图从暂停点继续执行。

### 交互流程详解

```mermaid
graph TD
    A[Graph Paused] --> B{Inspect State?};
    B -- Yes --> C[app.get_state(config)];
    C --> D{Modify State?};
    B -- No --> D;
    D -- Yes --> E[app.update_state(config, new_values)];
    E --> F[app.stream(None, config)];
    D -- No --> F;
    F --> G[Graph Resumes Execution];
```
*图1: 与暂停的图进行交互的完整生命周期。*

--- 

## 1. 检查状态: `app.get_state(config)`

一旦图暂停，你的第一个动作通常是检查它为何暂停。`get_state` 方法就是用来做这个的。

**API 用法:**

```python
# config = {"configurable": {"thread_id": "some_session"}}

# 第一次调用，图会运行直到中断点
# for event in app.stream(inputs, config):
#     ...

# 图已暂停，现在我们可以检查它的状态
# current_state = app.get_state(config)

# current_state 是一个 StateSnapshot 对象，
# 它的 .values 属性包含了我们熟悉的 state 字典
# latest_message = current_state.values['messages'][-1]

# if latest_message.tool_calls:
#     print(f"Agent 准备调用工具: {latest_message.tool_calls[0]['name']}")
```

-   **`config` 参数是必须的**: 你必须提供 `thread_id`，这样 LangGraph 才知道你想检查的是**哪一个**被暂停的会话。
-   **返回值**: 它返回一个 `StateSnapshot` 对象，其中包含了状态值、父配置、后续配置等元数据。你最关心的通常是 `.values` 属性。

## 2. 继续执行: 再次调用 `stream` 或 `invoke`

如何让图从暂停点继续？答案可能有点出乎意料：**再次调用你之前用的那个方法（`stream` 或 `invoke`），但这次第一个参数传 `None`。**

**API 用法:**

```python
# 假设用户已经批准

# 再次调用 app.stream，但第一个参数（inputs）为 None
# 这告诉 LangGraph: "不要从头开始，而是从 thread_id 对应的会话
# 上次暂停的地方继续。"
# for event in app.stream(None, config):
#     print("--- 图正在从暂停点恢复 ---")
#     ...
```

-   **`None` 作为输入**: `None` 是一个信号，告诉 LangGraph 这是一个“继续”操作，而不是一个“启动”操作。
-   **`config` 仍然是必须的**: 你必须提供同一个 `thread_id`，以确保你恢复的是正确的会话。

## 3. (可选) 修改状态: `app.update_state(config, new_values)`

这是一个人机协作的高级功能。在恢复执行之前，你可以选择性地覆盖或添加状态中的值。这相当于你作为“人类”给 Agent 的下一步行动提供了新的输入或指示。

**API 用法:**

```python
# 假设用户不仅批准了，还给出了额外指示
# user_feedback = "很好，但在搜索时，请把结果限制在最近一年。"

# 在继续之前，我们可以向 messages 列表中添加一条新的消息
# update_patch = {"messages": [HumanMessage(content=user_feedback)]}

# 使用 update_state 来应用这个补丁
# app.update_state(config, update_patch)

# 现在，当我们继续执行时，Agent 会看到这条新的人类消息，
# 并可能据此调整它的工具调用参数
# app.stream(None, config)
```

-   **更新机制**: `update_state` 的行为和你定义的 State 更新机制（例如 `operator.add`）是一致的。所以，向 `messages` 添加消息会触发追加，而不是替换。

--- 

## LLM 相关知识：Few-Shot Learning in Action

`update_state` 的能力与 LLM 的 **Few-Shot Learning** 能力完美结合。

当 Agent 做出一个不太理想的决策并暂停时（例如，它想调用一个错误的工具），你可以：
1.  **暂停** 图的执行。
2.  使用 `update_state` 向 `messages` 列表中注入一条**修正信息**，例如：`HumanMessage(content="不，不要使用 search 工具，你应该使用 file_reader 工具来回答这个问题。")`
3.  **继续** 执行。

当 Agent 从暂停点恢复时，它会看到这条新的人类指令。对于现代的 LLM 来说，这条指令就像一个即时的“小样本学习”示例，它会立即理解并修正自己的行为，在下一次思考时选择正确的工具。这比从头开始修改 Prompt 要灵活和即时得多。

--- 

## 相关 Python 语法详解

### 1. `None` 作为特殊值

-   **概念**: `None` 是 Python 中一个特殊的单例对象，用来表示“没有值”或“空”。它不是 `0`，不是 `False`，也不是空字符串 `""`。它就是 `None`。
-   **用法**: 在编程中，`None` 常常被用作信号，来触发不同于常规值的特殊逻辑。在 LangGraph 中，将 `None` 作为 `stream`/`invoke` 的第一个参数，就是利用了它的这个“信号”特性，来区分“启动新流程”和“继续旧流程”。
-   **检查 `None`**: 推荐使用 `is` 关键字来检查一个变量是否是 `None`，例如 `if my_variable is None:`。这是因为 `None` 在整个 Python 程序中只有一个实例，`is` 可以直接比较对象身份，比 `==` 更快、更准确。

### 2. 对象属性访问

-   **语法**: `my_object.attribute_name`
-   **概念**: 在 Python 中，一切皆对象。对象可以有与之关联的变量（称为属性）和函数（称为方法）。我们使用点 (`.`) 操作符来访问它们。
-   **示例**: `app.get_state` 是访问 `app` 对象的 `get_state` 方法。`current_state.values` 则是访问 `current_state` 对象的 `values` 属性。
-   **与 LangGraph 的关系**: LangGraph 的 API 设计是高度面向对象的。`app`、`StateSnapshot` 等都是具有明确属性和方法的对象。熟悉这种访问方式是使用任何 Python 库的基础。
