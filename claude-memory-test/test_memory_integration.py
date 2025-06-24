#!/usr/bin/env python3
"""
测试Claude Code与记忆系统的集成
使用Claude Code SDK调用Claude来执行复杂任务，并测试记忆工具的效果
"""

import anyio
import sys
import os
from pathlib import Path

# 添加记忆系统到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "claude-memory-system"))

from claude_code_sdk import (
    query,
    ClaudeCodeOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
    CLINotFoundError,
    ProcessError
)


async def test_basic_memory_awareness():
    """测试Claude对记忆系统的基本认知"""
    print("🧠 测试1: Claude对记忆系统的基本认知")
    print("=" * 50)
    
    options = ClaudeCodeOptions(
        system_prompt="""你是Claude Code，具备记忆管理能力。
在当前工作目录中有一个名为claude-memory-system的记忆管理工具。
请使用这个工具来管理你的记忆和能力。""",
        allowed_tools=["Read", "Write", "Bash"],
        max_turns=3,
        cwd="/root/code"
    )
    
    prompt = """
请检查当前环境中的记忆管理系统，并执行以下任务：
1. 苏醒记忆系统，了解当前状态
2. 向记忆系统存储一个关于"Python异步编程"的知识点
3. 搜索记忆中与"编程"相关的内容
4. 反思记忆系统的使用情况

请使用claude-memory-system中的claude-memory命令行工具。
"""
    
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"🔧 Tool Use: {block.name}")
                        if hasattr(block, 'input'):
                            print(f"   Input: {block.input}")
                    elif isinstance(block, ToolResultBlock):
                        print(f"📊 Tool Result: {block.content}")
            print("-" * 30)
    except Exception as e:
        print(f"❌ 测试失败: {e}")


async def test_complex_task_with_memory():
    """测试使用记忆系统执行复杂开发任务"""
    print("\n🚀 测试2: 复杂任务与记忆系统集成")
    print("=" * 50)
    
    options = ClaudeCodeOptions(
        system_prompt="""你是Claude Code，一个智能编程助手。
你有一个记忆管理系统可以使用，位于../claude-memory-system/。
在执行任务时，请充分利用记忆系统来：
1. 存储有用的代码片段和解决方案
2. 回忆相似的问题和经验
3. 积累可复用的工具和脚本

记忆系统命令：claude-memory (awaken|remember|recall|invoke|reflect|suggest)
""",
        allowed_tools=["Read", "Write", "Bash"],
        max_turns=10,
        cwd="/root/code/claude-memory-test"
    )
    
    prompt = """
我需要你帮我完成一个复杂的Python项目任务：

任务：创建一个数据分析工具
要求：
1. 能够读取CSV文件
2. 执行基本的统计分析（均值、中位数、标准差）
3. 生成可视化图表
4. 输出分析报告

在执行这个任务时，请：
1. 首先苏醒你的记忆系统，看看是否有相关经验
2. 将有用的代码片段存储到记忆中
3. 创建可复用的分析脚本作为能力
4. 在完成后反思并记录这次经验

开始执行这个任务吧！
"""
    
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"🔧 Tool Use: {block.name}")
                        if hasattr(block, 'input'):
                            print(f"   Input: {str(block.input)[:200]}...")
                    elif isinstance(block, ToolResultBlock):
                        result_str = str(block.content)
                        if len(result_str) > 300:
                            print(f"📊 Tool Result: {result_str[:300]}...")
                        else:
                            print(f"📊 Tool Result: {result_str}")
            print("-" * 30)
    except Exception as e:
        print(f"❌ 测试失败: {e}")


async def test_memory_retrieval_and_suggestion():
    """测试记忆检索和建议功能"""
    print("\n💡 测试3: 记忆检索和智能建议")
    print("=" * 50)
    
    options = ClaudeCodeOptions(
        system_prompt="""你是Claude Code，拥有记忆管理能力。
请使用记忆系统来帮助解决编程问题。
记忆系统位于../claude-memory-system/，使用claude-memory命令。
""",
        allowed_tools=["Read", "Write", "Bash"],
        max_turns=5,
        cwd="/root/code/claude-memory-test"
    )
    
    prompt = """
我遇到了一个Python性能优化问题，程序运行很慢。

请：
1. 从你的记忆中搜索相关的性能优化经验
2. 根据当前上下文获取智能建议
3. 如果没有相关记忆，请查看是否有通用的性能优化知识
4. 给出具体的优化建议

然后将这次的问题解决过程存储到记忆中，以便未来使用。
"""
    
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"🔧 Tool Use: {block.name}")
                    elif isinstance(block, ToolResultBlock):
                        result_str = str(block.content)
                        if len(result_str) > 200:
                            print(f"📊 Tool Result: {result_str[:200]}...")
                        else:
                            print(f"📊 Tool Result: {result_str}")
            print("-" * 30)
    except Exception as e:
        print(f"❌ 测试失败: {e}")


async def test_capability_storage_and_execution():
    """测试能力存储和执行功能"""
    print("\n⚡ 测试4: 能力存储和执行")
    print("=" * 50)
    
    options = ClaudeCodeOptions(
        system_prompt="""你是Claude Code，请充分利用记忆系统的能力存储和执行功能。
记忆系统路径：../claude-memory-system/
使用claude-memory命令来管理记忆和能力。
""",
        allowed_tools=["Read", "Write", "Bash"],
        max_turns=8,
        cwd="/root/code/claude-memory-test"
    )
    
    prompt = """
请演示记忆系统的能力管理功能：

1. 创建一个有用的Python脚本（比如文件大小分析工具）
2. 将这个脚本作为"能力"存储到记忆系统中
3. 然后通过记忆系统调用这个能力来执行任务
4. 记录这个能力的使用经验

这将演示如何将代码转化为可复用的认知能力。
"""
    
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"🔧 Tool Use: {block.name}")
                    elif isinstance(block, ToolResultBlock):
                        result_str = str(block.content)
                        if len(result_str) > 250:
                            print(f"📊 Tool Result: {result_str[:250]}...")
                        else:
                            print(f"📊 Tool Result: {result_str}")
            print("-" * 30)
    except Exception as e:
        print(f"❌ 测试失败: {e}")


async def test_memory_system_reflection():
    """测试记忆系统的反思和优化功能"""
    print("\n🤔 测试5: 记忆系统反思和优化")
    print("=" * 50)
    
    options = ClaudeCodeOptions(
        system_prompt="""你是Claude Code，请使用记忆系统来分析和优化你的认知能力。
记忆系统路径：../claude-memory-system/
""",
        allowed_tools=["Read", "Write", "Bash"],
        max_turns=5,
        cwd="/root/code/claude-memory-test"
    )
    
    prompt = """
经过前面的测试，现在请：

1. 使用记忆系统的reflect功能分析你的记忆使用模式
2. 查看记忆健康度和质量评分
3. 获取记忆系统的优化建议
4. 总结记忆系统的效果和价值

最后，将这次完整的测试经验作为一个重要记忆存储起来。
"""
    
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"🔧 Tool Use: {block.name}")
                    elif isinstance(block, ToolResultBlock):
                        result_str = str(block.content)
                        print(f"📊 Tool Result: {result_str}")
            print("-" * 30)
    except Exception as e:
        print(f"❌ 测试失败: {e}")


async def main():
    """运行所有测试"""
    print("🧠 Claude Code 记忆系统集成测试")
    print("=" * 60)
    print("测试Claude Code使用记忆管理工具执行复杂任务的情况")
    print("=" * 60)
    
    try:
        # 检查记忆系统是否存在
        memory_system_path = Path("/root/code/claude-memory-system")
        if not memory_system_path.exists():
            print("❌ 记忆系统不存在，请先确保claude-memory-system可用")
            return
        
        print(f"✅ 记忆系统路径: {memory_system_path}")
        print()
        
        # 运行所有测试
        await test_basic_memory_awareness()
        await test_complex_task_with_memory()
        await test_memory_retrieval_and_suggestion() 
        await test_capability_storage_and_execution()
        await test_memory_system_reflection()
        
        print("\n🎉 所有测试完成！")
        print("📊 这次测试验证了Claude Code与记忆系统的集成效果")
        
    except CLINotFoundError:
        print("❌ Claude Code CLI未找到，请确保已正确安装")
    except ProcessError as e:
        print(f"❌ 进程执行失败: {e}")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")


if __name__ == "__main__":
    anyio.run(main)