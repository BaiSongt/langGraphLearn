
# 阶段四：高级技巧 | 10.2. 解读 LangSmith 执行轨迹

**目标：** 学习如何导航和解读 LangSmith 的可视化追踪（Trace）界面，能够从一个复杂的执行轨迹中快速定位到关键信息，如 Prompt 内容、工具输入输出和错误信息。

---

## LangSmith 轨迹 (Trace) 概览

当你的一次 Agent 执行被记录到 LangSmith 后，它会以一个“运行实例 (Run)”的形式出现在列表中。点击任何一个运行实例，你就会进入该次执行的详细“轨迹 (Trace)”视图。

这个视图的核心是一个**可折叠的树状结构**，它完美地映射了你代码中组件的调用层级。

### 一个典型的 Agent 执行轨迹结构

假设我们运行了第二阶段的“Ollama 工具调用 Agent”，其轨迹在 LangSmith 中看起来会是这样的层级结构：

```
- 🕵️‍♂️ Agent (Graph) - [总耗时: 5.2s]
  - ⛓️ Agent Node (Runnable) - [耗时: 2.1s]
    - 💬 LLM (ChatOllama) - [耗时: 2.0s]
      - ➡️ 输入 (Prompt)
      - ⬅️ 输出 (AIMessage with tool_calls)
  - 🛠️ Tool Node (Runnable) - [耗时: 3.1s]
    - ➡️ 输入 (AIMessage with tool_calls)
    - ⬅️ 输出 (List of ToolMessage)
      - 툴 simple_search (Tool) - [耗时: 3.0s]
        - ➡️ 输入 ({'query': '...'}) 
        - ⬅️ 输出 ("Search results...")
  - ⛓️ Agent Node (Runnable) - [耗时: 1.5s]
    - 💬 LLM (ChatOllama) - [耗时: 1.4s]
      - ➡️ 输入 (Prompt with tool results)
      - ⬅️ 输出 (Final AIMessage)
```

--- 

## 如何解读这个轨迹？

### 1. **顶层节点：整个图的执行**
-   树的根节点 (`🕵️‍♂️ Agent`) 代表了整个 `app.invoke()` 或 `app.stream()` 的调用。
-   这里显示的是总耗时和最终的输入/输出。

### 2. **子节点：图中的节点 (Nodes)**
-   根节点的下一层是你在图 `workflow` 中定义的节点，例如 `Agent Node` 和 `Tool Node`。
-   你可以清晰地看到它们的执行顺序。
-   每个节点都有自己的耗时，这可以帮助你快速定位性能瓶颈。

### 3. **深入 LLM 调用**
-   点击任何一个 `LLM (ChatOllama)` 节点，这是最有价值的部分。
-   **输入 (Input):** 在这里，你可以看到**最终被发送给 LLM API 的、完整格式化的 Prompt**。这对于调试 Prompt Engineering 问题至关重要。你不再需要猜测模板最终被渲染成了什么样。
-   **输出 (Output):** 这里显示了 LLM 返回的原始 `AIMessage`，包括它请求调用的工具名称和参数。

### 4. **深入工具调用**
-   点击 `Tool Node`，你可以看到它接收到的 `AIMessage`。
-   再点击其下的具体工具，如 `simple_search`，你可以精确地看到：
    -   **输入 (Input):** 传递给该工具函数的具体参数是什么（例如 `{"query": "LangGraph 和 LangChain 的关系"}`）。
    -   **输出 (Output):** 该工具函数返回的原始结果是什么（例如，Tavily 搜索返回的长字符串）。

### 5. **定位错误**
-   如果任何一个步骤（无论是 LLM 调用还是工具执行）失败了，该节点在树状图中会被标记为**红色**。
-   你可以直接点击这个红色节点，在其“错误 (Error)”标签页中看到完整的 Python 异常堆栈跟踪，快速定位问题根源。

--- 

## 调试场景示例

**场景1：Agent 没有按预期调用工具。**
1.  **怎么做？** 在 LangSmith 中找到这次运行，展开第一个 `Agent Node` -> `LLM` 调用。
2.  **看什么？** 检查“输入 (Prompt)”。很可能是你提供给 LLM 的工具描述不够清晰，或者你的对话历史让 LLM 产生了困惑。你可以直接复制这个 Prompt 到一个 Playground 中进行迭代优化。

**场景2：工具执行失败。**
1.  **怎么做？** 在轨迹中找到红色的 `Tool Node`。
2.  **看什么？** 
    -   首先，检查其下的具体工具节点的“输入”，看看是不是 LLM 给出了错误的参数（例如，一个不存在的文件名）。
    -   然后，检查该节点的“错误”标签，查看具体的异常信息（例如，“文件未找到”或“API Key 无效”）。

**场景3：Agent 陷入无限循环。**
1.  **怎么做？** 在 LangSmith 的运行列表中，你会看到一个持续时间很长，或者最终因 `RecursionError` 而失败的运行。
2.  **看什么？** 查看它的轨迹。你会看到 `Agent Node` 和 `Tool Node` 在交替重复出现。通过检查每一步 LLM 的输入和输出，你可以分析出 Agent 为何总是做出相同的、无法导向终点的决策。

--- 

## 总结

LangSmith 将 Agent 复杂的、黑箱式的执行过程，变成了一个清晰、透明、可交互的“飞行数据记录”。学会解读它的执行轨迹，是提升你调试效率、优化 Agent 性能和可靠性的关键技能。它让你能够从“猜测”和“祈祷”式的调试，转向“观察”和“分析”式的、更科学的开发模式。
