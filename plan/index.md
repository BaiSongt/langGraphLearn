
# LangGraph 学习计划索引

欢迎来到 LangGraph 学习计划！本文档是所有学习资料的目录和导航页。请按照以下顺序进行学习，以获得最佳效果。

首先，请阅读我们的总纲，了解整个学习路径的规划：
-   [**学习计划细化大纲 (Master Plan)**](./detailed_learning_outline.md)

---

## 预备知识

在开始 LangGraph 之前，请确保你已掌握了必要的 Python 知识。

-   [**Python for LangGraph: 核心知识点**](./python_for_langgraph.md)

---

## 第一阶段：核心概念与基础构建

*本阶段将带你理解 LangGraph 的核心思想，并构建第一个简单的工作流。*

-   **理论学习:**
    1.  [LCEL vs. LangGraph](./phase1_1_lcel_vs_langgraph.md)
    2.  [“状态驱动”架构详解](./phase1_2_state_driven_architecture.md)
    3.  [详解核心组件：State](./phase1_2_1_state_deep_dive.md)
    4.  [详解核心组件：Nodes](./phase1_2_2_nodes_deep_dive.md)
    5.  [详解核心组件：Edges](./phase1_2_3_edges_deep_dive.md)
-   **实践项目:**
    -   [构建简单问答机器人](./phase1_3_1_project_simple_chatbot.md) (代码: `src/phase1_simple_chatbot.py`)

---

## 第二阶段：Agentic Loop 与状态管理

*本阶段将教你如何构建能够循环思考和行动的真正 Agent，并管理其对话历史。*

-   **理论学习:**
    1.  [构建循环](./phase2_4_1_building_loops.md)
    2.  [避免无限循环](./phase2_4_2_avoiding_infinite_loops.md)
    3.  [详解状态累积](./phase2_5_1_state_accumulation.md)
    4.  [Annotated 类型注解的背后机制](./phase2_5_2_annotated_deep_dive.md)
-   **实践项目:**
    -   [构建 Ollama 工具调用 Agent](./phase2_6_1_project_ollama_agent.md) (代码: `src/phase2_tool_agent.py`)

---

## 第三阶段：可靠性与产品化

*本阶段将学习如何通过持久化和人工干预，让你的 Agent 变得更健壮、更可靠。*

-   **理论学习:**
    1.  [Checkpointer 持久化概念](./phase3_7_1_checkpointing_concepts.md)
    2.  [thread_id 与并发会话管理](./phase3_7_2_thread_id_concepts.md)
    3.  [人工干预 (Human-in-the-Loop)](./phase3_8_1_human_in_the_loop_concepts.md)
    4.  [中断后的检查与恢复机制](./phase3_8_2_human_in_the_loop_mechanics.md)
-   **实践项目:**
    -   [构建带用户确认的 Agent](./phase3_9_1_project_agent_with_confirmation.md) (代码: `src/phase3_human_in_the_loop.py`)

---

## 第四阶段：高级技巧与生态集成

*本阶段将带你了解如何使用 LangSmith 等专业工具来调试和监控你的 Agent。*

-   **理论学习:**
    1.  [LangSmith 的核心价值](./phase4_10_1_langsmith_concepts.md)
    2.  [解读 LangSmith 执行轨迹](./phase4_10_2_interpreting_traces.md)
-   **实践项目:**
    -   [集成 LangSmith 调试](./phase4_11_1_project_langsmith_integration.md) (代码: `src/phase4_langsmith_integration.py`)

---

## 附录

-   [**LangChain 工具与集成推荐 (Agent's Arsenal)**](./popular_tools_and_integrations.md)
