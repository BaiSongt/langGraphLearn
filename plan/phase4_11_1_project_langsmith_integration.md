
# 阶段四：实践项目 | 11.1. 集成 LangSmith 调试

**目标：** 将我们现有的 Agent 项目无缝对接到 LangSmith 平台，并实际演练如何在 LangSmith UI 中查找并解读一次完整的、带人工干预的执行轨迹。

**项目描述：** 我们将复用第三阶段构建的“会议纪要员” Agent（`main_v3.py`），它具有持久化和人工干预的能力。我们不会修改任何代码，仅仅通过设置环境变量，就能将其所有的运行细节记录到 LangSmith 中，体验其“零侵入式”集成的强大之处。

---

### 步骤 1: 注册并创建 LangSmith 项目

1.  访问 [LangSmith 官网](https://smith.langchain.com/) 并使用你的 Google 账户或邮箱注册。
2.  登录后，系统可能会引导你创建一个“组织 (Organization)”。
3.  进入你的组织后，点击 “Create Project” 按钮创建一个新项目。将项目命名为 `LangGraph Learning` 或任何你喜欢的名字。

### 步骤 2: 获取你的 API Key

1.  在 LangSmith 页面的左下角，点击你的头像或账户图标，然后选择 “Settings”。
2.  在设置页面中，向下滚动到 “API Keys” 部分。
3.  点击 “Create API Key” 按钮。你可以给这个 Key 一个备注，比如 `langgraph-dev-key`。
4.  **立即复制生成的 API Key** (它以 `ls__` 开头)。这个 Key 只会显示一次，请妥善保管。

### 步骤 3: 在你的本地环境中设置环境变量

在运行你的 Python 脚本**之前**，打开你的终端（Terminal），并设置以下三个环境变量。**请将引号内的内容替换为你自己的真实值。**

**对于 macOS / Linux (Bash/Zsh):**
```bash
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_API_KEY="YOUR_COPIED_API_KEY_HERE"
export LANGCHAIN_PROJECT="LangGraph Learning"
```

**对于 Windows (PowerShell):**
```powershell
$env:LANGCHAIN_TRACING_V2="true"
$env:LANGCHAIN_API_KEY="YOUR_COPIED_API_KEY_HERE"
$env:LANGCHAIN_PROJECT="LangGraph Learning"
```

**验证:** 你可以输入 `echo $env:LANGCHAIN_PROJECT` (PowerShell) 或 `echo $LANGCHAIN_PROJECT` (Bash) 来确认环境变量是否设置成功。

### 步骤 4: 运行你的 Agent 项目

**对应的代码示例文件是 `src/phase4_langsmith_integration.py`。**

在运行脚本之前，请确保将代码中 `YOUR_LANGSMITH_API_KEY` 替换为你的真实 API Key。

然后，在你的终端中运行脚本：
```bash
python src/phase4_langsmith_integration.py
```

### 步骤 5: 在 LangSmith 中找到并解读轨迹

1.  **打开 LangSmith:** 回到你的浏览器，刷新你的 `LangGraph Learning` 项目页面。
2.  **找到运行实例:** 你会看到一个新的运行实例出现在列表中，它的名称可能是一串随机字符，或者与你的 Agent 相关。它的延迟（Latency）应该对应你刚才运行程序的总耗时。
3.  **点击进入轨迹视图:** 点击这个运行实例，进入我们之前学习过的“轨迹视图”。
4.  **开始探索：**
    -   **顶层:** 你会看到整个 `StateGraph` 的运行。展开它。
    -   **第一次 Agent 调用:** 展开第一个 `agent_node`，再展开其下的 `ChatOllama`，点击“输入”，查看发送给模型的完整初始 Prompt。
    -   **中断点:** 你会发现轨迹在 `agent_node` 之后就结束了第一部分。这对应了我们代码中的第一次 `app.stream()` 调用，它在中断点暂停了。
    -   **第二次运行:** LangSmith 可能会将 `continue` 的部分显示为另一次运行，或者在同一次运行中用不同的颜色标记。找到代表 `app.stream(None, ...)` 的那部分调用。
    -   **工具调用:** 展开 `tools` 节点，你可以清晰地看到 `write_summary_to_file` 工具被调用，以及传递给它的 `filename` 和 `summary` 参数是什么。
    -   **最终结束:** 看到最后的 `__end__` 节点，标志着整个流程的完成。

---

### 总结

恭喜你！你已经完成了从零开始学习 LangGraph，到构建一个可靠、可调试的 Agent 的全过程。

通过本次实践，你应该深刻体会到 LangSmith 的价值：

-   **零侵入性:** 我们没有为了集成 LangSmith 而修改一行应用代码。
-   **无与伦比的透明度:** Agent 内部每一个复杂的步骤都被清晰地记录和可视化，让调试不再是“猜谜游戏”。

现在，你已经掌握了构建、强化和调试现代 LLM Agent 的全套核心技能。祝贺你，你的 LangGraph 学习之旅已成功完成！
