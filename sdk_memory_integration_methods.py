#!/usr/bin/env python3
"""
Claude Code SDK 记忆工具集成的三种方法
替代CLAUDE.md文件的程序化配置方案
"""

from claude_code_sdk import query, ClaudeCodeOptions
from pathlib import Path
import os

# 方法1: 系统提示注入
def method1_system_prompt_injection():
    """通过system_prompt直接注入记忆工具使用指令"""
    
    memory_system_prompt = """🧠 你是具备记忆能力的Claude Code，必须主动使用记忆工具：

🔍 强制回忆场景：
- 用户提到"问题/错误/bug" → 立即执行: memory.recall("问题解决方案", max_results=3)
- 用户询问"如何/方法" → 立即执行: memory.recall("技术方案", max_results=3)  
- 用户提到"学习/了解" → 立即执行: memory.recall("学习资源", max_results=3)

💾 强制记录场景：
- 解决问题后 → memory.remember(解决方案)
- 分享知识后 → memory.remember(重要概念)
- 完成任务后 → memory.remember(经验总结)

⚡ 执行规则：
1. 每次对话开始前必须搜索相关记忆
2. 每次对话至少使用1次记忆工具
3. 主动询问是否需要记录重要信息

这不是建议，而是强制要求。记忆工具是你的核心能力。"""

    options = ClaudeCodeOptions(
        system_prompt=memory_system_prompt,
        allowed_tools=["Bash", "Read", "Write", "Edit", "Grep", "Glob"],
        max_turns=20,
        cwd=Path("/root/code")
    )
    
    return options

# 方法2: 动态上下文感知
def method2_context_aware_prompting(user_input: str):
    """基于用户输入动态生成记忆增强的系统提示"""
    
    # 分析用户输入，决定记忆工具使用策略
    trigger_words = {
        "问题": "你遇到了问题求助，必须先用memory.recall()搜索类似问题的解决方案",
        "如何": "你被询问方法，必须先用memory.recall()搜索相关技术方案",
        "学习": "用户想学习，必须先用memory.recall()搜索学习资源和经验",
        "项目": "涉及项目开发，必须先用memory.recall()搜索项目经验和模式"
    }
    
    # 检测触发词
    triggered_behaviors = []
    for word, behavior in trigger_words.items():
        if word in user_input:
            triggered_behaviors.append(behavior)
    
    if triggered_behaviors:
        context_prompt = f"""🧠 记忆工具使用指令：
        
根据用户输入，你必须：
{chr(10).join(f"• {behavior}" for behavior in triggered_behaviors)}

然后在回答最后，必须用memory.remember()记录重要信息。

这是强制性要求，不是建议。"""
    else:
        context_prompt = "🧠 默认必须在对话中至少使用1次记忆工具（recall或remember）。"
    
    options = ClaudeCodeOptions(
        system_prompt="你是Claude Code，具备记忆管理能力。",
        append_system_prompt=context_prompt,
        allowed_tools=["Bash", "Read", "Write", "Edit"],
        max_turns=15
    )
    
    return options

# 方法3: 环境变量 + 会话管理
def method3_environment_session_control():
    """通过环境变量和会话管理控制记忆工具使用"""
    
    # 设置环境变量强制记忆工具行为
    os.environ["CLAUDE_MEMORY_MANDATORY"] = "true"
    os.environ["CLAUDE_MEMORY_MIN_USAGE"] = "1"  # 每次对话最少使用次数
    os.environ["CLAUDE_MEMORY_PATH"] = "/root/code/claude-memory-system"
    
    # 构建包含记忆工具路径的系统提示
    memory_path_prompt = f"""🧠 记忆系统配置：

记忆工具位置: {os.environ['CLAUDE_MEMORY_PATH']}
强制使用: {os.environ['CLAUDE_MEMORY_MANDATORY']}
最少使用次数: {os.environ['CLAUDE_MEMORY_MIN_USAGE']}

你必须在每次对话中：
1. 开始前使用 `memory.recall()` 搜索相关记忆
2. 结束前询问是否需要 `memory.remember()` 记录信息
3. 至少使用 {os.environ['CLAUDE_MEMORY_MIN_USAGE']} 次记忆工具

记忆工具命令：
- memory.recall("搜索词", max_results=3)
- memory.remember(content="内容", title="标题", importance=7.0)"""

    options = ClaudeCodeOptions(
        system_prompt=memory_path_prompt,
        cwd=Path("/root/code"),
        continue_conversation=True,
        max_turns=25
    )
    
    return options

# 完整使用示例
async def main():
    """演示三种方法的使用"""
    
    user_input = "我在Python开发中遇到性能问题，请帮助解决"
    
    print("🔥 方法1: 系统提示注入")
    options1 = method1_system_prompt_injection()
    async for message in query(user_input, options1):
        print(f"回复: {message.content}")
        break
    
    print("\n🔥 方法2: 动态上下文感知")
    options2 = method2_context_aware_prompting(user_input)
    async for message in query(user_input, options2):
        print(f"回复: {message.content}")
        break
    
    print("\n🔥 方法3: 环境变量控制")
    options3 = method3_environment_session_control()
    async for message in query(user_input, options3):
        print(f"回复: {message.content}")
        break

# 推荐配置组合
def recommended_memory_enhanced_options(task_context: str = "general"):
    """推荐的记忆增强配置组合"""
    
    base_memory_prompt = """🧠 Claude Code 记忆增强模式

你必须主动使用记忆工具。对于每个用户请求：

1. 🔍 立即搜索: memory.recall("相关关键词", max_resources=3)
2. 💡 基于记忆提供回答
3. 💾 询问记录: "需要我记录这个解决方案吗？"

最低要求: 每次对话使�1次记忆工具
目标: A级主动性 (2+次使用)

这是服务质量标准，必须遵守。"""

    return ClaudeCodeOptions(
        system_prompt=base_memory_prompt,
        allowed_tools=["Bash", "Read", "Write", "Edit", "Grep", "Glob"],
        permission_mode="acceptEdits",
        max_turns=20,
        cwd=Path("/root/code"),
        continue_conversation=True
    )

if __name__ == "__main__":
    import asyncio
    
    print("🧠 Claude Code SDK 记忆工具集成方法演示")
    print("=" * 50)
    
    # 显示配置选项
    print("推荐配置:")
    options = recommended_memory_enhanced_options()
    print(f"系统提示: {options.system_prompt[:100]}...")
    print(f"允许工具: {options.allowed_tools}")
    print(f"最大轮次: {options.max_turns}")
    
    # 可以取消注释以下行来运行实际测试
    # asyncio.run(main())