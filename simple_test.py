#!/usr/bin/env python3
"""
简单测试记忆工具集成
"""

import sys
import asyncio
from pathlib import Path

# 添加SDK路径
sys.path.insert(0, str(Path(__file__).parent / "claude-code-sdk-python" / "src"))

def test_memory_system():
    """测试记忆系统"""
    print("🧠 测试记忆系统...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "claude-memory-system"))
        from claude_memory import MemoryManager
        
        memory = MemoryManager(Path("."))
        snapshot = memory.awaken("测试")
        
        print(f"✅ 记忆系统正常，记忆数: {snapshot.memory_statistics.total_memories}")
        return True
        
    except Exception as e:
        print(f"❌ 记忆系统失败: {e}")
        return False

async def test_claude_code():
    """测试Claude Code"""
    print("🤖 测试Claude Code...")
    
    try:
        from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock
        
        options = ClaudeCodeOptions(
            system_prompt="简短回答",
            max_turns=1
        )
        
        async for message in query(prompt="你好", options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"✅ Claude正常: {block.text}")
                        return True
        
        return False
        
    except Exception as e:
        print(f"❌ Claude失败: {e}")
        return False

async def test_integration():
    """测试集成"""
    print("🔧 测试记忆集成...")
    
    try:
        from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock
        
        prompt = """你必须说"我正在搜索记忆"然后回答问题。"""
        
        options = ClaudeCodeOptions(
            system_prompt=prompt,
            max_turns=2
        )
        
        response = ""
        async for message in query(prompt="Python有什么特点？", options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response += block.text
                        print(f"回复: {block.text}")
        
        if "搜索" in response or "记忆" in response:
            print("✅ 检测到记忆相关内容")
            return True
        else:
            print("❌ 未检测到记忆使用")
            return False
            
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 记忆工具测试")
    print("=" * 30)
    
    # 运行测试
    memory_ok = test_memory_system()
    claude_ok = await test_claude_code()
    integration_ok = await test_integration()
    
    print("\n" + "=" * 30)
    print("📊 结果:")
    print(f"记忆系统: {'✅' if memory_ok else '❌'}")
    print(f"Claude Code: {'✅' if claude_ok else '❌'}")
    print(f"集成测试: {'✅' if integration_ok else '❌'}")
    
    if all([memory_ok, claude_ok, integration_ok]):
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️ 部分测试失败")

if __name__ == "__main__":
    asyncio.run(main())