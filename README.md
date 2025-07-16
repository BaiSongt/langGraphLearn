
# LangGraph 学习项目

这是一个通过 AI 助手引导，从零开始创建的 LangGraph 学习项目。本项目包含了一整套由浅入深的 LangGraph 学习文档和配套的、可运行的 Python 代码示例。

---

## 项目目标

本项目的目标是系统性地、循序渐进地掌握 LangGraph 的核心概念与高级用法，最终能够独立构建出复杂的、可靠的、可调试的 LLM Agent 应用。

## 如何使用本项目

**最佳学习路径是先阅读文档，再运行对应的代码。**

1.  **从 `plan` 文件夹开始**: 打开 `plan/index.md` 文件。这是所有学习资料的目录和导航页。
2.  **遵循学习路径**: 按照 `index.md` 中规划的四个阶段，依次阅读每个阶段的理论文档。
3.  **运行实践代码**: 在每个阶段的理论学习结束后，找到对应的实践项目文档和代码（位于 `src` 文件夹），亲手运行并调试它们，以巩固所学知识。

## 项目结构

```
D:/mywork/langGraphLearn/
├── plan/                  # 所有的学习文档 (从这里开始)
│   ├── index.md           # 学习计划目录和导航页
│   ├── python_for_langgraph.md # Python 预备知识
│   ├── phase1_...         # 第一阶段文档
│   ├── phase2_...         # 第二阶段文档
│   ├── phase3_...         # 第三阶段文档
│   └── phase4_...         # 第四阶段文档
├── src/                   # 所有的 Python 实践代码
│   ├── phase1_simple_chatbot.py
│   ├── phase2_tool_agent.py
│   ├── phase3_human_in_the_loop.py
│   └── phase4_langsmith_integration.py
├── .gitignore
├── pyproject.toml         # 项目配置文件 (uv)
├── README.md              # 你正在阅读的文件
└── checkpoints.sqlite     # 第三方阶段实践生成的数据库文件
```

## 技术栈

-   **核心框架**: LangGraph, LangChain
-   **包管理与虚拟环境**: `uv`
-   **LLM**: Ollama (qwen3:4b), DeepSeek API, Google Gemini API
-   **工具**: Tavily Search API
-   **调试与追踪**: LangSmith

---

祝你学习愉快！
