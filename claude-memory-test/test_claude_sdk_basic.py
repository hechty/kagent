#!/usr/bin/env python3
"""
基础的Claude Code SDK测试
验证SDK是否能正常工作以及Claude是否会主动使用记忆工具
"""

import sys
import asyncio
from pathlib import Path

try:
    from claude_code_sdk import query, ClaudeCodeOptions
    print("✅ Claude Code SDK导入成功")
except ImportError as e:
    print(f"❌ Claude Code SDK导入失败: {e}")
    sys.exit(1)

async def test_basic_claude_interaction():
    """测试基础的Claude交互"""
    print("🤖 测试基础Claude交互")
    print("-" * 30)
    
    # 配置Claude，指导其使用记忆系统
    options = ClaudeCodeOptions(
        system_prompt="""
你是Claude Code，具备记忆管理能力。

🧠 重要提示：在当前目录../claude-memory-system/中有一个完整的记忆管理工具。
你可以通过以下命令使用它：

1. claude-memory awaken - 苏醒记忆系统
2. claude-memory recall "查询内容" - 搜索相关记忆  
3. claude-memory remember "内容" --type semantic --title "标题" - 存储新记忆

请在回答问题时主动使用这些记忆工具来：
- 查找相关的历史经验
- 存储有价值的新知识
- 提供更好的解决方案

重要：请确保在适当的时候使用记忆系统！
        """,
        allowed_tools=["Bash", "Read"],
        max_turns=5,
        cwd="/root/code/claude-memory-test"
    )
    
    # 简单的测试任务
    prompt = """
请帮我解决一个Python编程问题：

我想写一个函数来计算列表中数字的平均值，但要处理空列表的情况。

在回答之前，请：
1. 先使用记忆系统查看是否有相关的Python编程经验
2. 然后提供解决方案
3. 最后将这个解决方案存储到记忆中

请主动使用../claude-memory-system/中的记忆工具。
    """
    
    print("发送提示给Claude...")
    print("=" * 50)
    
    try:
        response_count = 0
        memory_usage_detected = False
        
        async for message in query(prompt=prompt, options=options):
            response_count += 1
            print(f"\n[响应 {response_count}]")
            
            # 检查消息类型和内容
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        text = block.text
                        print(f"Claude: {text}")
                        
                        # 检测是否提到了记忆系统
                        if any(keyword in text.lower() for keyword in ['记忆', 'claude-memory', '搜索', '存储']):
                            memory_usage_detected = True
                            print("  🧠 [检测到记忆相关活动]")
                    
                    elif hasattr(block, 'name') and block.name == 'Bash':
                        if hasattr(block, 'input') and 'claude-memory' in str(block.input):
                            memory_usage_detected = True
                            print(f"  🔧 [记忆工具调用]: {block.input}")
            
            print("-" * 30)
            
            # 限制响应数量防止无限循环
            if response_count >= 10:
                print("达到最大响应限制，停止测试")
                break
        
        print(f"\n📊 测试结果:")
        print(f"总响应数: {response_count}")
        print(f"检测到记忆使用: {'是' if memory_usage_detected else '否'}")
        
        if memory_usage_detected:
            print("✅ Claude主动使用了记忆系统")
        else:
            print("⚠️ Claude没有主动使用记忆系统")
        
        return memory_usage_detected
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_memory_system_awareness():
    """测试Claude对记忆系统的认知"""
    print("\n🧠 测试Claude对记忆系统的认知")
    print("-" * 30)
    
    options = ClaudeCodeOptions(
        system_prompt="""
你是Claude Code。请注意：在../claude-memory-system/目录中有一个记忆管理工具。
请主动检查并使用这个工具。
        """,
        allowed_tools=["Bash", "LS", "Read"],
        max_turns=3,
        cwd="/root/code/claude-memory-test"
    )
    
    prompt = """请检查并告诉我当前环境中是否有记忆管理工具可用，如果有，请尝试使用它。"""
    
    try:
        async for message in query(prompt=prompt, options=options):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(f"Claude: {block.text}")
                    elif hasattr(block, 'name'):
                        print(f"工具使用: {block.name}")
                        if hasattr(block, 'input'):
                            print(f"  输入: {block.input}")
            print("-" * 20)
        
        return True
        
    except Exception as e:
        print(f"❌ 认知测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🔬 Claude Code主动记忆使用基础测试")
    print("=" * 60)
    
    # 测试1：基础交互中的记忆使用
    memory_used = await test_basic_claude_interaction()
    
    # 测试2：记忆系统认知
    awareness_test = await test_memory_system_awareness()
    
    # 总结
    print(f"\n🎯 测试总结")
    print("=" * 30)
    print(f"记忆主动使用: {'✅' if memory_used else '❌'}")
    print(f"系统认知能力: {'✅' if awareness_test else '❌'}")
    
    if memory_used and awareness_test:
        print("🎉 Claude Code具备主动记忆使用能力")
    else:
        print("⚠️ Claude Code的主动记忆使用能力需要改进")
        print("\n💡 可能的原因:")
        print("- 系统提示不够明确")
        print("- 记忆工具路径不正确")  
        print("- 需要更明确的使用指导")

if __name__ == "__main__":
    asyncio.run(main())