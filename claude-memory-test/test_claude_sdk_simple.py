#!/usr/bin/env python3
"""
简化的Claude Code SDK测试
测试Claude使用记忆系统的基本功能
"""

import anyio
from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock

async def test_claude_with_memory():
    """测试Claude使用记忆系统的基本交互"""
    
    print("🤖 测试Claude Code SDK与记忆系统集成")
    print("=" * 50)
    
    # 配置Claude使用记忆系统
    options = ClaudeCodeOptions(
        system_prompt="""你是Claude Code，拥有记忆管理能力。
你可以使用位于../claude-memory-system/目录中的记忆管理工具。
该工具通过claude-memory命令提供以下功能：
- awaken: 苏醒记忆系统
- remember: 存储记忆
- recall: 搜索记忆  
- invoke: 执行能力
- reflect: 分析记忆
- suggest: 获取建议

请在适当的时候使用这些工具来管理你的记忆。""",
        allowed_tools=["Bash", "Read", "Write"],
        max_turns=3,
        cwd="/root/code/claude-memory-test"
    )
    
    prompt = """
请帮我测试记忆系统的功能：

1. 首先苏醒记忆系统，查看当前状态
2. 存储一个关于"机器学习基础概念"的知识
3. 搜索记忆中与"学习"相关的内容

请使用../claude-memory-system/中的claude-memory工具。
"""
    
    print("发送提示给Claude...")
    print("-" * 30)
    
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
            print("-" * 20)
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主测试函数"""
    await test_claude_with_memory()

if __name__ == "__main__":
    anyio.run(main)