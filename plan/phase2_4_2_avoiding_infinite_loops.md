
# 阶段二：Agentic Loop | 4.2. 避免无限循环

**目标：** 理解在构建循环时可能出现的无限循环风险，并掌握 LangGraph 提供的核心安全机制 `recursion_limit` 来防止程序失控。

---

## 无限循环：Agent 的“噩梦”

我们已经学会了如何创建 `tool -> agent` 的循环。但一个潜在的风险随之而来：如果 Agent 的决策逻辑有缺陷，或者工具总是返回无法让 Agent 得到最终答案的结果，程序就可能陷入“思考-行动”的无限循环中，永不停止。这会耗尽计算资源和 API 调用额度。

### 无限循环的可能成因

1.  **Agent 逻辑缺陷**: Agent 总是认为需要调用同一个工具，即使工具返回了结果。
2.  **工具结果无用**: 工具返回的信息不足以让 Agent 做出最终判断。
3.  **环境变化**: Agent 正在处理一个动态变化的数据源，导致它永远无法达到一个“完成”的状态。

### 可视化“失控”的循环

```mermaid
graph TD
    B{Agent Node: 思考};
    C[Tool Node: 执行];
    B -->|决策: 总是需要工具| C;
    C --> B;  // 循环往复，永不结束
```
*图1: 一个没有出口的循环会导致程序卡死。*

---

## `recursion_limit`: 你的安全阀

为了防止这种情况，LangGraph 在执行图时强制要求一个**递归限制** (`recursion_limit`)。这个参数就像一个安全阀，它定义了从图的入口点开始，可以连续执行多少步。

**工作原理:**
-   每次执行一个节点，内部的步数计数器就 `+1`。
-   在执行下一个节点之前，LangGraph 会检查计数器是否超过了 `recursion_limit`。
-   如果超过了，图会立即停止执行并抛出一个 `RecursionError`。

**API 用法:**

`recursion_limit` 是在**运行图**时，通过 `config` 参数传入的。

```python
# app = workflow.compile()

# 在调用 .invoke() 或 .stream() 时传入配置
# 这里我们设置最大步数为 5
config = {"recursion_limit": 5}

# app.invoke(inputs, config=config)
# for event in app.stream(inputs, config=config):
#     print(event)
```

### 如何选择 `recursion_limit` 的值？

-   **从一个合理的小数字开始**: 对于大多数 Agent 任务，`5` 到 `10` 步通常是一个合理的起点。
-   **根据任务复杂度调整**: 如果你的任务确实需要很多步骤（比如需要调用多个不同工具），你可以适当调高这个值。
-   **它是一个安全网**: 它的主要目的不是作为程序逻辑的一部分，而是作为防止意外错误的最后一道防线。

---

## LLM 相关知识：Agent 的“幻觉”与“固执”

无限循环往往与 LLM 的两个行为弱点有关：

1.  **幻觉 (Hallucination)**: LLM 可能会“幻想”出一个它认为有用的工具或参数，但这个工具实际上并不存在。如果你的 Agent 逻辑不够健壮，无法处理这种无效的工具调用，就可能导致循环。
2.  **固执 (Persistency)**: 有时 LLM 会陷入一种“思维定势”。即使工具返回了明确的信息，它仍然会固执地认为需要再次调用同一个工具。这在处理一些开放性问题或模糊指令时尤其常见。

**缓解策略:**
-   **清晰的 Prompt**: 在给 Agent 的系统指令（System Prompt）中，明确地告诉它在何种情况下应该结束任务，以及如何处理工具返回的错误或空结果。
-   **Few-shot 示例**: 在 Prompt 中提供几个完整的“思考-行动-观察-最终答案”的例子，可以有效地引导 LLM 遵循正确的行为模式。

---

## 相关 Python 语法详解

### 1. 函数/方法的关键字参数 (Keyword Arguments)

-   **语法**: 在调用函数时，使用 `parameter_name=value` 的形式来传递参数。例如 `app.invoke(inputs, config=config)`。
-   **优点**: 
    -   **清晰性**: 明确地指出了 `config` 这个值是赋给 `config` 这个参数的，比按位置传递参数更易读。
    -   **灵活性**: 不需要关心参数的顺序。
-   **与 LangGraph 的关系**: LangGraph 的 `.invoke`, `.stream` 等核心方法大量使用关键字参数来接收配置项，如 `config`。这使得 API 非常灵活，未来可以轻松添加更多配置项而不会破坏现有代码。

### 2. 异常处理 (Exception Handling)

-   **语法**: 使用 `try...except` 块来捕获和处理可能发生的错误（异常）。
-   **工作原理**: `try` 块中的代码会被执行。如果在此期间发生了 `except` 子句中指定的异常（如 `RecursionError`），程序会立即跳转到 `except` 块中执行，而不是直接崩溃。
-   **重要性**: 当你运行一个可能达到 `recursion_limit` 的图时，可以用 `try...except` 来优雅地捕获这个错误，并给用户一个友好的提示。

```python
config = {"recursion_limit": 3}

try:
    print("开始执行图...")
    # 假设这个调用会因为无限循环而触发 RecursionError
    app.invoke({"question": "一个会引发循环的问题"}, config=config)
except RecursionError:
    print("\n错误：图的执行步数超过了限制 (3 步)。")
    print("这可能是一个无限循环。请检查 Agent 的决策逻辑。")
except Exception as e:
    print(f"发生了未知错误: {e}")

print("程序继续执行...")
```

通过 `recursion_limit` 和 `try...except` 的结合，你可以构建出既能处理复杂循环任务，又不会因意外情况而崩溃的健壮 Agent.
