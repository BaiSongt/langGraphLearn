

# -----------------------------------------------------------------------------
# AI 聊天应用 - 用户交互主程序
#
# 本文件负责处理用户输入、管理对话会话，并调用在 app.py 中定义的 LangGraph 应用。
# -----------------------------------------------------------------------------

# --- 核心库导入 ---
import uuid
import sqlite3
from .app import chatapp, memory # 从同一个文件夹下的 app.py 文件中导入 chatapp 和 memory
from langchain_core.messages import HumanMessage

# --- Python 语法详解: `from .app import ...` ---
# `.` 在 import 语句中代表“当前文件夹”。
# 这条语句的意思是：“从当前文件夹下的 `app.py` 模块中，导入 `chatapp` 和 `memory` 这两个变量。”
# 这种相对导入是组织一个包内多个文件之间关系的标准方式。


def get_session_history(session_id: str):
    """获取指定会话 ID 的历史记录。"""
    # `memory` 是我们在 app.py 中创建的 SqliteSaver 实例。
    # 我们可以用它来直接与数据库交互。
    return memory.get_tuple(config={"configurable": {"thread_id": session_id}})

def get_all_sessions():
    """通过直接查询数据库来获取所有唯一的会话 ID。"""
    try:
        conn = sqlite3.connect("chat_history.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
        sessions = cursor.fetchall()
        conn.close()
        return [{ "configurable": { "thread_id": session[0] } } for session in sessions]
    except sqlite3.OperationalError:
        # 如果表不存在，说明还没有任何会话被保存。
        return []

def main_loop():
    """应用的主交互循环。"""
    print("欢迎来到 LangGraph AI 聊天应用！")
    print("------------------------------------")

    # --- 会话管理 ---
    sessions = get_all_sessions()
    session_id = None

    if not sessions:
        print("未找到历史对话。将开始一个新对话。")
        # --- Python 语法详解: `uuid.uuid4()` ---
        # `uuid.uuid4()` 生成一个全球唯一的随机标识符。
        # 我们用它来作为新对话的 `thread_id`，以保证每个对话都是独立、不冲突的。
        session_id = str(uuid.uuid4())
    else:
        print("找到以下历史对话:")
        for i, config in enumerate(sessions):
            print(f"  {i + 1}: {config['configurable']['thread_id']}")
        
        print("  N: 开始一个新对话")

        while True:
            choice = input("请选择一个对话继续，或输入 'N' 开始新对话: ")
            if choice.lower() == 'n':
                session_id = str(uuid.uuid4())
                break
            try:
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(sessions):
                    session_id = sessions[choice_index]['configurable']['thread_id']
                    print("\n--- 继续历史对话 --- ")
                    history = get_session_history(session_id)
                    for message in history.messages:
                        message.pretty_print()
                    print("--- 对话已加载 ---\n")
                    break
                else:
                    print("无效的选择，请输入列表中的数字。")
            except ValueError:
                print("无效的输入，请输入一个数字或 'N'。")

    # --- Python 语法详解: `f-string` ---
    # f"..." 是一种现代的、易读的格式化字符串的方式。
    # 你可以直接在字符串中用 `{}` 包裹变量名，Python 会自动将变量的值替换进去。
    print(f"\n当前会话 ID: {session_id}")
    print("输入 '/exit' 退出程序。")
    print("------------------------------------")

    # 为当前会话创建一个配置字典
    config = {"configurable": {"thread_id": session_id}}

    # --- 主聊天循环 ---
    # --- Python 语法详解: `while True` ---
    # `while True:` 创建了一个无限循环。这个循环会一直执行下去，
    # 直到遇到一个 `break` 语句。
    while True:
        try:
            # --- Python 语法详解: `input()` ---
            # `input()` 函数会暂停程序，等待用户在命令行中输入一些文本，
            # 然后按回车。用户输入的文本会以字符串的形式返回。
            user_input = input("You: ")
            if user_input.lower() == '/exit':
                print("感谢使用，再见！")
                break # 跳出无限循环

            # 将用户的输入封装成 HumanMessage 对象
            inputs = {"messages": [HumanMessage(content=user_input)]}
            
            # --- 调用 LangGraph 应用 ---
            # `chatapp.stream()` 是我们与 Agent 交互的核心。
            # 我们传入用户的输入和当前会话的配置。
            # Agent 会自动加载这个会话的历史记录，并在此基础上进行思考。
            final_response = None
            print("AI: ", end="", flush=True)
            for event in chatapp.stream(inputs, config, stream_mode="values"):
                # `stream` 会返回每一步的状态更新。我们只关心最终的回复。
                # AIMessage 类型的消息就是 AI 的回复。
                ai_messages = [msg for msg in event["messages"] if isinstance(msg, AIMessage)]
                if ai_messages:
                    final_response = ai_messages[-1]
            
            # 打印最终回复
            if final_response:
                print(final_response.content)

        except KeyboardInterrupt:
            # --- Python 语法详解: `KeyboardInterrupt` ---
            # 当用户在命令行中按下 Ctrl+C 时，Python 会抛出这个异常。
            # 我们在这里捕获它，以实现优雅地退出程序。
            print("\n检测到 Ctrl+C，程序退出。感谢使用！")
            break
        except Exception as e:
            print(f"\n发生了一个意料之外的错误: {e}")
            print("程序将退出。")
            break

# --- Python 语法详解: `if __name__ == "__main__":` ---
# 这是一个 Python 的标准写法。
# 它的含义是：“只有当这个文件是作为主程序直接被运行时，才执行下面的代码。”
# 如果这个文件被其他文件作为模块 `import`，那么 `if` 下面的代码就**不会**被执行。
# 这使得我们可以安全地从其他文件中导入 `main_loop` 函数，而不用担心它会自动运行。
if __name__ == "__main__":
    main_loop()
