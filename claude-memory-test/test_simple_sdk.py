#!/usr/bin/env python3
"""
最简单的Claude Code SDK测试
"""

import asyncio
from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock

async def simple_test():
    print("🤖 简单SDK测试")
    
    options = ClaudeCodeOptions(
        system_prompt="你是Claude Code。请简短回答问题。",
        max_turns=1,
        cwd="/root/code/claude-memory-test"
    )
    
    try:
        print("发送简单查询...")
        async for message in query(prompt="说'hello world'", options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude回复: {block.text}")
        print("✅ SDK基础功能正常")
        return True
    except Exception as e:
        print(f"❌ SDK测试失败: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(simple_test())
    if result:
        print("SDK测试成功，可以继续进行记忆系统测试")
    else:
        print("SDK测试失败，需要检查配置")