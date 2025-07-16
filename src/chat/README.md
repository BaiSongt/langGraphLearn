
# LangGraph AI 聊天应用

---

## 概述 (Overview)

这是一个基于 LangGraph 构建的、功能完备的命令行 AI 聊天应用。它旨在演示如何综合运用 LangGraph 的核心功能（状态、循环、持久化、工具调用）来创建一个有记忆、能行动、可交互的实用 Agent。

## 核心功能 (Core Features)

-   **多轮对话**: Agent 能够记住之前的对话上下文，进行连贯的交流。
-   **工具使用**: Agent 集成了 Tavily 网页搜索工具，当遇到其知识库之外或需要最新信息的问题时，能够自主决定并执行搜索。
-   **持久化记忆**: 所有的对话历史都会被自动保存到一个 SQLite 数据库文件 (`chat_history.sqlite`) 中。
-   **会话管理**: 应用启动时，可以加载并继续之前的对话，或者开启一个全新的对话。

## 文件结构 (File Structure)

本应用被拆分为两个核心文件，以实现逻辑与交互的分离：

-   `app.py`: **AI 的大脑**。此文件定义了 Agent 的所有核心逻辑，包括：
    -   `AgentState`: 对话记忆的结构。
    -   `search_tool`: Agent 可以使用的工具。
    -   `agent_node`, `tool_node`, `router`: LangGraph 图的节点和边，定义了 Agent 的“思考-行动”工作流。
    -   `chatapp`: 经过编译的、带有持久化功能的 LangGraph 可执行应用。

-   `main.py`: **用户交互界面 (CLI)**。此文件是应用的入口点，负责：
    -   处理用户的命令行输入。
    -   实现会话管理（加载历史或创建新会话）。
    -   在一个循环中调用 `chatapp`，并将 AI 的回复打印到屏幕上。

## 安装与配置 (Setup and Configuration)

### 1. 安装依赖 (Install Dependencies)

本项目使用 `uv` 进行包管理。在项目根目录下，运行以下命令来安装所有必要的依赖：

```bash
uv sync
```

或者，你也可以使用 `pip` 和 `requirements.txt` 文件：

```bash
pip install -r requirements.txt
```

### 2. 设置环境变量 (Set Environment Variables)

为了让 Agent 能够正常调用外部 API，你**必须**在你的操作系统中设置以下环境变量：

cp .env.example .env

# .env
DEEPSEEK_API_KEY=YOUR_DEEPSEEK_API_KEY
TAVILY_API_KEY=YOUR_TAVILY_API_KEY

## 如何运行 (How to Run)

1.  确保你的终端位于项目的根目录 (`langGraphLearn/`)下。
2.  使用以下命令启动应用。`-m` 标志告诉 Python 将 `src.chat` 作为一个模块来运行。

    ```bash
    python -m src.chat.main
    ```

## 使用说明 (How to Use)

1.  **选择会话**: 程序启动后，会列出所有可用的历史对话。输入数字选择一个继续，或输入 `N` 开始一个新对话。
2.  **聊天**: 在 `You:` 提示符后输入你的问题或指令，然后按回车。
3.  **等待回复**: AI Agent 会进行思考，可能会调用工具（你会看到相应的日志），然后打印出它的最终回复。
4.  **退出**: 在任何时候，输入 `/exit` 并按回车，即可退出应用。
