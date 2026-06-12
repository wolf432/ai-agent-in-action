"""《老兵学 Agent》#1 配套代码:健壮的多工具 Function Calling 模板。

覆盖的坑:
1. assistant 消息必须在 tool_call 循环外追加(一对多)
2. 模型可能不调工具,tool_calls 为 None
3. arguments 是字符串且可能为畸形 JSON
4. 工具执行失败也要把错误作为 tool 消息返回
5. 不同厂商校验严格度不同,开发期建议用严格模型(如 DeepSeek)验证

公众号:回复 agent 获取本文完整讲解。
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
)
MODEL = os.getenv("MODEL")


# ---------- 示例工具 ----------

def get_weather(city: str) -> str:
    return f"{city} 晴,28°C"


def get_time(timezone: str = "Asia/Shanghai") -> str:
    from datetime import datetime
    return datetime.now().isoformat()


TOOL_REGISTRY = {
    "get_weather": get_weather,
    "get_time": get_time,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的当前天气",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "城市名"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取当前时间",
            "parameters": {
                "type": "object",
                "properties": {"timezone": {"type": "string", "description": "时区"}},
            },
        },
    },
]


# ---------- 核心模板 ----------

def execute_tool(tool_call) -> str:
    """解析参数并执行工具,任何失败都返回错误描述而非抛异常。"""
    # 坑 3:arguments 是字符串,可能是畸形 JSON
    try:
        args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        return "参数解析失败:模型返回了畸形 JSON"

    fn = TOOL_REGISTRY.get(tool_call.function.name)
    if fn is None:
        return f"未知工具: {tool_call.function.name}"

    # 坑 4:工具执行失败也要把错误返回给模型
    try:
        return str(fn(**args))
    except Exception as e:  # noqa: BLE001
        return f"工具执行失败: {e}"


def robust_tool_calling(user_query: str, max_rounds: int = 5) -> str:
    """支持多工具并行调用、多轮工具调用的健壮模板。"""
    messages = [{"role": "user", "content": user_query}]

    for _ in range(max_rounds):  # 防止模型无限循环调工具
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
        )
        message = response.choices[0].message

        # 坑 2:模型可能直接回答,tool_calls 为 None
        if not message.tool_calls:
            return message.content

        # 坑 1:assistant 消息在循环外只追加一次
        messages.append(message)

        for tool_call in message.tool_calls:
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": execute_tool(tool_call),
            })

    return "已达最大工具调用轮数,流程终止"


if __name__ == "__main__":
    print(robust_tool_calling("北京天气怎么样?现在几点了?"))
