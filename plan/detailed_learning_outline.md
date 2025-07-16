
# LangGraph 学习计划细化大纲 (Master Plan)

本文档是我们后续创建详细学习资料的“总目录”和“路线图”。我们将根据这个大纲，逐一将每个知识点扩充为详细的 Markdown 文件。

---

## 一、LangGraph 学习路线细化 (`learning_plan.md`)

### 第一阶段：核心概念与基础构建

1.  **深入 LangGraph 思想**
    *   1.1. 与 LCEL (LangChain Expression Language) 的详细对比：为何 LCEL 不够用？
    *   1.2. “状态驱动”架构详解：数据如何在图中流动和变化。
2.  **详解三大核心组件**
    *   2.1. **State**: `TypedDict` vs. 普通 `dict` 的优劣；State 的初始化。
    *   2.2. **Nodes**: 节点的输入/输出契约；如何设计幂等的节点。
    *   2.3. **Edges**: `add_edge` vs. `add_conditional_edges` 的内部机制；`router` 函数的设计模式。
3.  **实践项目 Plan**
    *   3.1. "简单问答机器人" 的分步实现指南。

### 第二阶段：Agentic Loop 与状态管理

4.  **深入 Agentic Loop**
    *   4.1. 循环的构建方式：`tool -> agent` 边的意义。
    *   4.2. 如何避免无限循环：`recursion_limit` 的作用和调试技巧。
5.  **详解状态累积**
    *   5.1. `operator.add` 的工作原理：图解默认更新与追加更新的区别。
    *   5.2. `Annotated` 类型注解的背后机制。
6.  **实践项目 Plan**
    *   6.1. "Ollama 工具调用 Agent" 的分步实现指南，包括如何与本地 Ollama 模型交互。

### 第三阶段：可靠性与产品化

7.  **深入持久化与 Checkpointing**
    *   7.1. `Checkpointer` 的概念：`MemorySaver` vs. `SqliteSaver` 的选择。
    *   7.2. `thread_id` 的重要性：如何管理多用户会话。
8.  **详解人工干预**
    *   8.1. `interrupt_before` 的工作流程图。
    *   8.2. 如何在中断后检查 (`get_state`) 和恢复 (`continue`) 执行。
9.  **实践项目 Plan**
    *   9.1. "带用户确认的 Agent" 的分步实现指南。

### 第四阶段：高级技巧与生态集成

10. **深入 LangSmith 集成**
    *   10.1. LangSmith 的核心价值：可视化调试、追踪与评估。
    *   10.2. 如何解读 LangSmith 中的图执行轨迹。
11. **实践项目 Plan**
    *   11.1. "集成 LangSmith 调试" 的分步操作指南。

---

## 二、Python 知识专题 (`python_for_langgraph.md`) 内容大纲

此部分内容将独立成篇，作为学习 LangGraph 必备的 Python 前置知识。

1.  **Python 基础回顾**
    *   1.1. **函数是一等公民**: 核心概念，解释为何函数可以作为参数传递。
    *   1.2. **字典 (dict) 操作**: `.get()`、`.update()` 等常用方法。
2.  **Python 类型提示 (Type Hinting)**
    *   2.1. **`typing` 模块**: `List`, `Dict`, `Any`, `Literal`。
    *   2.2. **`TypedDict`**: 定义结构化字典，LangGraph State 的最佳实践。
    *   2.3. **`Annotated`**: Python 3.9+ 的高级类型，用于附加元数据，是 LangGraph 状态累积的关键。
3.  **Python 中高级编程**
    *   3.1. **装饰器 (Decorators)**: 概念与基本用法。
    *   3.2. **闭包 (Closures)**: 理解函数如何“记住”其创建时的环境。
    *   3.3. **类与对象 (Classes and Objects)**: 封装工具和逻辑的最佳实践。
4.  **常用标准库**
    *   4.1. **`operator` 模块**: 重点讲解 `operator.add` 和 `operator.itemgetter`。
    *   4.2. **`functools` 模块**: `partial` 的用法，可用于简化节点函数的定义。
