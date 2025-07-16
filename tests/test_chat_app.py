
import os
import pytest
from unittest.mock import patch, MagicMock

# 在导入 app 模块之前设置环境变量
os.environ["DEEPSEEK_API_KEY"] = "test_key"
os.environ["TAVILY_API_KEY"] = "test_key"

from src.chat.app import get_compiled_app, router, AgentState

@patch('src.chat.app.ChatDeepSeek')
@patch('src.chat.app.TavilySearch')
def test_get_compiled_app_initialization(mock_tavily, mock_deepseek):
    """测试 get_compiled_app 是否可以被成功调用并返回一个已编译的应用。"""
    app = get_compiled_app()
    assert app is not None

def test_router_with_tool_calls():
    """测试当最后一条消息包含工具调用时，路由器返回 'tools'。"""
    mock_message = MagicMock()
    mock_message.tool_calls = [MagicMock()]
    state = AgentState(messages=[mock_message])
    result = router(state)
    assert result == "tools"

def test_router_without_tool_calls():
    """测试当最后一条消息不包含工具调用时，路由器返回 '__end__'。"""
    mock_message = MagicMock()
    mock_message.tool_calls = []
    state = AgentState(messages=[mock_message])
    result = router(state)
    assert result == "__end__"

