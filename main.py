from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
import random

# 1. 定义状态 (State)
# 使用 TypedDict 可以让状态的结构更清晰，也方便IDE进行类型提示。
class GraphState(TypedDict):
    question: str  # 用户问题
    answer: str | None  # 模型的最终回答
    # "next" 字段用于条件路由，决定下一步走向
    next: Literal["agent", "tool", "end"] 

# 2. 定义节点 (Nodes)
# 节点是执行核心逻辑的函数。它们接收当前状态，返回对状态的更新。

def agent_node(state: GraphState):
    """
    模拟 Agent 思考的节点。
    它会接收问题，并决定是直接回答还是需要使用工具。
    """
    print(f"--- 正在执行 Agent 节点 ---")
    question = state['question']
    print(f"思考问题: {question}")

    # 模拟决策逻辑
    if "langgraph" in question.lower():
        # 如果问题包含 "langgraph"，模拟需要调用工具
        print("决策: 问题比较复杂，需要使用搜索工具。")
        return {"next": "tool"}
    else:
        # 否则，直接回答
        print("决策: 问题很简单，直接回答。")
        answer = f"这是一个简单的回答：'{question}' 的答案是 {random.randint(1, 100)}。"
        return {"answer": answer, "next": "end"}

def tool_node(state: GraphState):
    """
    模拟调用工具的节点。
    """
    print(f"--- 正在执行 Tool 节点 ---")
    print("正在使用搜索工具查找 'LangGraph' 的资料...")
    tool_result = "LangGraph 是一个强大的库，用于构建有状态的 LLM 应用。"
    
    # 这里的回答是基于工具结果的
    answer = f"通过搜索工具找到了答案：{tool_result}"
    return {"answer": answer, "next": "end"}

# 3. 定义条件边 (Conditional Edge)
# 这是一个函数，它根据当前状态决定下一个要执行的节点。
def router(state: GraphState) -> Literal["agent", "tool", "end"]:
    """
    根据 state['next'] 的值来决定路由方向。
    """
    print(f"--- 正在执行 Router ---")
    next_step = state['next']
    print(f"路由决策: 下一步是 -> {next_step}")
    return next_step

# 4. 构建图 (Graph)
workflow = StateGraph(GraphState)

# 添加节点
workflow.add_node("agent", agent_node)
workflow.add_node("tool", tool_node)

# 设置入口点
workflow.set_entry_point("agent")

# 添加条件边
# 从 "agent" 节点出来后，调用 router 函数来决定去哪里
workflow.add_conditional_edges(
    "agent",
    router,
    {
        "tool": "tool", # 如果 router 返回 "tool", 则去 "tool" 节点
        "end": END      # 如果 router 返回 "end", 则结束
    }
)

# 添加普通边
# 从 "tool" 节点出来后，固定结束
workflow.add_edge("tool", END)

# 编译图，生成可执行的应用
app = workflow.compile()

# 5. 运行图
print("=========================================")
print("案例1: 简单问题，不使用工具")
inputs1 = {"question": "你好吗？", "next": "agent"}
# .stream() 可以流式返回每一步的状态
for s in app.stream(inputs1, {"recursion_limit": 5}):
    print(s)
    print("--------------------")

print("\n=========================================")
print("案例2: 复杂问题，使用工具")
inputs2 = {"question": "请介绍一下 LangGraph", "next": "agent"}
for s in app.stream(inputs2, {"recursion_limit": 5}):
    print(s)
    print("--------------------")

# 你也可以使用 .invoke() 一次性获取最终结果
print("\n=========================================")
print("使用 invoke() 获取最终结果:")
final_state = app.invoke(inputs2, {"recursion_limit": 5})
print(f"最终答案: {final_state['answer']}")
