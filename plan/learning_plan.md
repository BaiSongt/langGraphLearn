
# LangGraph 由浅入深学习方案

本方案旨在提供一个结构化的 LangGraph 学习路径，从基础概念到高级应用，并结合实际代码项目进行巩固。同时，本方案也会指出每个阶段所需要掌握的 Python 知识点。

---

## 第一阶段：核心概念与基础构建

**目标：** 理解 LangGraph 为何存在，并掌握构建最基本工作流所需的三大核心组件。

### 1. 理论学习

-   **LangGraph 的思想与架构**
    -   **是什么？** LangChain 的一个扩展，用于构建有状态、可循环的图（Graph）。
    -   **为什么需要图？** 因为 Agent 的“思考-行动”本质上是循环的，而传统的 LangChain 表达式语言（LCEL）是无环的（DAG）。
    -   **核心架构：状态、节点、边**
        -   **State (状态)**: 整个图的共享内存，通常是一个字典或 `TypedDict`。
        -   **Nodes (节点)**: 执行具体任务的函数，接收状态并返回对状态的更新。
        -   **Edges (边)**: 连接节点，控制工作流的方向。

-   **Python 语法与技巧**
    -   **`TypedDict`**: 用于定义状态的数据结构，提供类型提示和代码健壮性。(`from typing import TypedDict`)
    -   **函数作为一等公民**: 理解可以将函数像变量一样传递，这是 `add_node` 和 `add_conditional_edges` 的基础。
    -   **Python 字典操作**: 节点的返回值是一个字典，它会通过 `.update()` 方法合并到主状态中。

### 2. 实践项目：简单问答机器人

-   **项目描述**: 创建一个图，接收一个问题。一个“思考”节点根据问题内容（例如是否包含特定关键词）决定是直接回答，还是将任务路由到另一个“工具”节点。
-   **涉及的 LangGraph API**:
    -   `StateGraph(GraphState)`: 创建图实例。
    -   `workflow.add_node(name, function)`: 添加节点。
    -   `workflow.set_entry_point(name)`: 设置入口。
    -   `workflow.add_edge(start_node, end_node)`: 添加常规边。
    -   `workflow.add_conditional_edges(start_node, router_function, path_map)`: 添加条件边。
    -   `workflow.compile()`: 编译图为可执行应用。

---

## 第二阶段：Agentic Loop 与状态管理

**目标：** 构建一个能够进行多步推理、可以自我循环的真正 Agent，并学会管理复杂的状态（如对话历史）。

### 1. 理论学习

-   **LangGraph 的思想与架构**
    -   **循环 (Cycles)**: 理解如何通过 `add_edge` 将下游节点指向上游节点（例如 `tool_node` -> `agent_node`）来创建循环，这是实现 Agentic Loop 的关键。
    -   **状态的累积**: 默认的状态更新是“替换”。学习如何通过 `Annotated` 和 `operator.add` 将其变为“追加”，这对于管理消息列表至关重要。

-   **Python 语法与技巧**
    -   **`typing.Annotated`**: Python 3.9+ 的功能，用于给类型附加额外的元数据。LangGraph 用它来改变状态的更新行为。
    -   **`operator.add`**: `operator` 模块中的函数，对于列表，`add` 等同于 `extend`。是实现状态累积的“魔法”所在。
    -   **LangChain Core Messages**: 熟悉 `HumanMessage`, `AIMessage`, `ToolMessage` 等消息对象，它们是构建 Agent 状态的标准方式。

### 2. 实践项目：集成 Ollama 的工具调用 Agent

-   **项目描述**: 创建一个 Agent，使用 `Ollama (qwen3:4b)` 作为大脑。Agent 接收用户问题，LLM 决定是否需要调用一个（或多个）你定义的 Python 工具。如果需要，则执行工具，将结果返回给 LLM，LLM 再进行下一轮思考，直到问题解决。
-   **涉及的 LangGraph API**:
    -   `StateGraph` 中使用 `Annotated` 定义的状态。
    -   `AIMessage` 对象中的 `tool_calls` 属性的解析。
    -   `ToolMessage` 的创建和使用。

---

## 第三阶段：可靠性与产品化

**目标：** 学习如何让你的 LangGraph 应用更健壮、更可靠，并为部署到生产环境做准备。

### 1. 理论学习

-   **LangGraph 的思想与架构**
    -   **持久化 (Persistence)**: Agent 的执行过程（状态）默认是存在内存中的。学习使用 `Checkpointer` (如 `MemorySaver`, `SqliteSaver`) 将每一步的状态保存下来，这样即使程序中断也可以恢复。
    -   **人工干预 (Human-in-the-Loop)**: 学习如何通过 `interrupt_before` 在关键节点（如执行危险工具前）暂停图的执行，等待用户确认后再继续。
    -   **流式输出 (Streaming)**: 理解如何通过 `.stream()` 方法实时获取并展示图在每个节点执行后的状态更新，提升用户体验。

-   **Python 语法与技巧**
    -   **上下文管理器 (`with` 语句)**: 虽然 LangGraph 的 API 很好地封装了它，但理解其工作原理有助于更好地使用 `Checkpointer`。
    -   **多线程/异步配置 (`configurable`)**: 理解 `app.stream` 和 `app.invoke` 中的 `config` 参数，特别是 `{"configurable": {"thread_id": "..."}}`，它是区分不同用户会话的关键。

### 2. 实践项目：带用户确认的 Agent

-   **项目描述**: 在第二阶段的 Agent 基础上进行升级。当 Agent 决定要调用一个工具时，不立即执行，而是暂停执行并打印出它想做什么。等待用户在命令行输入“yes”后，再继续执行工具调用。
-   **涉及的 LangGraph API**:
    -   `MemorySaver` 或 `SqliteSaver` 作为 `checkpointer`。
    -   `workflow.compile(checkpointer=..., interrupt_before=[...])`: 在编译时设置中断点。
    -   `app.get_state(config)`: 获取某个会话的当前状态。
    -   `app.update_state(config, new_state)`: (可选) 在暂停时手动修改状态。
    -   `app.continue_in_thread(config)`: (在旧版本中) 或在新版本中继续使用 `app.stream(None, config)` 来恢复执行。

---

## 第四阶段：高级技巧与生态集成

**目标：** 探索 LangGraph 的高级用法，并学习如何将其与 LangChain 生态中的其他组件（如 LangSmith）无缝集成。

### 1. 理论学习

-   **并行执行 (Parallel Execution)**: 学习如何配置图来并行执行多个独立的节点，以提高效率。
-   **动态修改图 (Dynamic Graph Modification)**: 探索在运行时动态添加或修改节点和边的可能性（高级主题）。
-   **LangSmith 集成**: 如何配置环境变量，让 LangGraph 的每一次执行轨迹都自动记录在 LangSmith 中，极大地方便调试和监控。

### 2. 实践项目：集成 LangSmith 调试

-   **项目描述**: 前往 [LangSmith 官网](https://smith.langchain.com/) 创建一个项目，获取 API Key。在你的 Agent 项目中设置相应的环境变量，然后运行你的 Agent。观察 LangSmith UI 中完整的、可视化的执行轨迹，检查每一步的输入输出。

通过以上四个阶段的学习和实践，你将能够熟练掌握 LangGraph，并有能力用它来构建复杂、可靠且可维护的 LLM 应用。
