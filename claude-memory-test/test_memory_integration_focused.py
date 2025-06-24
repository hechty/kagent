#!/usr/bin/env python3
"""
聚焦的记忆系统集成测试
测试Claude Code是否会主动使用记忆工具
"""

import asyncio
from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock, ToolUseBlock

async def test_memory_tool_usage():
    """测试Claude是否会主动使用记忆工具"""
    print("🧠 测试Claude主动使用记忆工具")
    print("=" * 50)
    
    # 明确的系统指令
    system_prompt = """
你是Claude Code，具备记忆管理能力。

🧠 重要指令：你必须使用位于../claude-memory-system/的记忆工具！

可用命令：
- claude-memory awaken [context] - 苏醒记忆系统
- claude-memory recall "查询" - 搜索记忆
- claude-memory remember "内容" --type semantic --title "标题" - 存储记忆

⚡ 强制要求：
1. 收到任何技术问题时，先用claude-memory recall搜索相关经验
2. 提供解决方案后，用claude-memory remember存储新知识
3. 开始任务时用claude-memory awaken激活记忆系统

请严格按照这个流程执行！
    """
    
    options = ClaudeCodeOptions(
        system_prompt=system_prompt,
        allowed_tools=["Bash"],
        max_turns=8,
        cwd="/root/code/claude-memory-test"
    )
    
    # 明确要求使用记忆的任务
    prompt = """
我有一个Python问题：如何优化循环性能？

请按以下步骤执行：
1. 先用claude-memory awaken启动记忆系统
2. 用claude-memory recall "Python 性能优化"搜索相关经验  
3. 基于搜索结果给出建议
4. 用claude-memory remember存储这次的解决方案

请确保执行每一步！
    """
    
    print("发送任务给Claude...")
    print("-" * 30)
    
    memory_commands_used = []
    response_count = 0
    
    try:
        async for message in query(prompt=prompt, options=options):
            response_count += 1
            print(f"\n[响应 {response_count}]")
            
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text = block.text
                        print(f"Claude: {text}")
                    elif isinstance(block, ToolUseBlock):
                        if block.name == "Bash":
                            command = block.input.get('command', '')
                            print(f"🔧 执行命令: {command}")
                            
                            if 'claude-memory' in command:
                                # 提取记忆命令类型
                                if 'awaken' in command:
                                    memory_commands_used.append('awaken')
                                elif 'recall' in command:
                                    memory_commands_used.append('recall')
                                elif 'remember' in command:
                                    memory_commands_used.append('remember')
                                print(f"  🧠 记忆命令: {command}")
            
            print("-" * 20)
            
            # 防止无限循环
            if response_count >= 15:
                break
        
        print(f"\n📊 记忆工具使用分析:")
        print(f"总响应数: {response_count}")
        print(f"使用的记忆命令: {memory_commands_used}")
        print(f"记忆命令总数: {len(memory_commands_used)}")
        
        # 评估主动性
        expected_commands = ['awaken', 'recall', 'remember']
        commands_used = set(memory_commands_used)
        completion_rate = len(commands_used & set(expected_commands)) / len(expected_commands)
        
        print(f"命令完成率: {completion_rate:.1%}")
        
        if completion_rate >= 0.8:
            print("✅ Claude能够主动有效使用记忆工具")
        elif completion_rate >= 0.5:
            print("⚠️ Claude部分使用了记忆工具，但不够完整")
        else:
            print("❌ Claude没有有效使用记忆工具")
        
        return {
            "memory_commands_used": memory_commands_used,
            "completion_rate": completion_rate,
            "response_count": response_count
        }
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

async def test_natural_memory_usage():
    """测试自然场景下的记忆使用"""
    print("\n💡 测试自然场景下的记忆使用")
    print("=" * 50)
    
    system_prompt = """
你是Claude Code，具备记忆能力。
你可以使用../claude-memory-system/中的记忆工具来增强你的能力。
在合适的时候主动使用这些工具。
    """
    
    options = ClaudeCodeOptions(
        system_prompt=system_prompt,
        allowed_tools=["Bash", "Read"],
        max_turns=5,
        cwd="/root/code/claude-memory-test"
    )
    
    # 更自然的提问方式
    prompt = """
我正在学习机器学习，能给我一些建议吗？特别是关于模型选择的建议。
    """
    
    print("发送自然提问...")
    
    memory_usage_detected = False
    
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text = block.text
                        print(f"Claude: {text}")
                        
                        # 检测是否提到记忆或搜索
                        if any(word in text.lower() for word in ['记忆', '搜索', '查找', '之前', '经验']):
                            print("  🧠 [提到了记忆相关概念]")
                    elif isinstance(block, ToolUseBlock):
                        if block.name == "Bash" and 'claude-memory' in str(block.input):
                            memory_usage_detected = True
                            print(f"  🔧 [主动使用记忆工具]: {block.input}")
        
        return {"natural_memory_usage": memory_usage_detected}
        
    except Exception as e:
        print(f"❌ 自然场景测试失败: {e}")
        return {"error": str(e)}

async def main():
    """主测试函数"""
    print("🔬 Claude Code记忆系统集成测试")
    print("=" * 60)
    
    # 测试1：明确指令下的记忆使用
    explicit_result = await test_memory_tool_usage()
    
    # 测试2：自然场景下的记忆使用
    natural_result = await test_natural_memory_usage()
    
    # 综合评估
    print(f"\n🎯 综合评估")
    print("=" * 30)
    
    if "error" not in explicit_result:
        completion_rate = explicit_result.get("completion_rate", 0)
        print(f"明确指令完成率: {completion_rate:.1%}")
    else:
        print(f"明确指令测试失败: {explicit_result['error']}")
    
    natural_usage = natural_result.get("natural_memory_usage", False)
    print(f"自然场景记忆使用: {'是' if natural_usage else '否'}")
    
    # 结论
    if "error" not in explicit_result and completion_rate >= 0.8:
        if natural_usage:
            print("🎉 Claude Code具备优秀的主动记忆使用能力")
        else:
            print("✅ Claude Code在明确指令下能有效使用记忆，但自然场景下需要改进")
    elif "error" not in explicit_result and completion_rate >= 0.5:
        print("⚠️ Claude Code具备基础记忆使用能力，但需要更好的指导")
    else:
        print("❌ Claude Code的记忆使用能力需要显著改进")
        print("\n💡 可能的改进方向:")
        print("- 优化系统提示的明确性")
        print("- 改进记忆工具的可发现性")
        print("- 增强Claude的主动性训练")

if __name__ == "__main__":
    asyncio.run(main())