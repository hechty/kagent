#!/usr/bin/env python3
"""
Phase 3: Claude主动性记忆系统优化
通过Python SDK实现智能的记忆工具主动调用机制
"""

import asyncio
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

try:
    from claude_code_sdk import (
        query, 
        ClaudeCodeOptions,
        AssistantMessage,
        TextBlock,
        ToolUseBlock,
        ResultMessage
    )
    SDK_AVAILABLE = True
except ImportError:
    print("⚠️ Claude Code SDK not available, creating simulation mode")
    SDK_AVAILABLE = False

class ProactiveMemoryController:
    """
    主动记忆控制器
    通过分析用户输入和上下文，智能引导Claude主动使用记忆工具
    """
    
    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path or Path.cwd()
        self.memory_usage_log = []
        self.conversation_context = []
        
        # 记忆触发关键词映射
        self.recall_triggers = {
            "问题解决": ["问题", "错误", "bug", "issue", "如何", "怎么", "解决", "修复"],
            "技术学习": ["学习", "了解", "什么是", "原理", "概念", "技术"],
            "代码相关": ["代码", "编程", "函数", "类", "算法", "实现"],
            "项目开发": ["项目", "开发", "架构", "设计", "框架", "工具"],
            "经验查找": ["经验", "经历", "之前", "以前", "类似", "相关"]
        }
        
        self.remember_triggers = {
            "知识获得": ["学到", "发现", "了解到", "明白了", "原来"],
            "问题解决": ["解决了", "修复了", "成功", "完成"],
            "重要信息": ["重要", "关键", "核心", "必须", "注意"],
            "最佳实践": ["最佳", "推荐", "建议", "优化", "改进"],
            "经验总结": ["总结", "经验", "教训", "心得", "体会"]
        }

    def analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """分析用户输入，确定记忆操作建议"""
        analysis = {
            "should_recall": False,
            "should_remember": False,
            "recall_reasons": [],
            "remember_reasons": [],
            "suggested_queries": [],
            "suggested_memory_content": None
        }
        
        input_lower = user_input.lower()
        
        # 分析是否应该回忆
        for category, keywords in self.recall_triggers.items():
            if any(keyword in input_lower for keyword in keywords):
                analysis["should_recall"] = True
                analysis["recall_reasons"].append(category)
                
                # 生成建议的搜索查询
                if category == "问题解决":
                    analysis["suggested_queries"].append(f"类似问题的解决方案")
                elif category == "技术学习":
                    analysis["suggested_queries"].append(f"相关技术概念和资料")
                elif category == "代码相关":
                    analysis["suggested_queries"].append(f"相关代码示例和实现")
        
        # 分析是否应该记忆
        for category, keywords in self.remember_triggers.items():
            if any(keyword in input_lower for keyword in keywords):
                analysis["should_remember"] = True
                analysis["remember_reasons"].append(category)
        
        return analysis

    def generate_enhanced_system_prompt(self, context_analysis: Dict[str, Any]) -> str:
        """生成增强的系统提示，引导Claude主动使用记忆工具"""
        
        base_prompt = """你是Claude Code，具有持久化记忆能力。你必须主动使用记忆工具来提供更好的帮助。

🧠 记忆工具使用指南 (必须遵循):

1. 📚 开始回答前 - 先搜索相关记忆:
   - 用户提到问题/错误 → 搜索"类似问题解决方案"
   - 用户询问技术概念 → 搜索"相关技术资料"
   - 用户要求代码实现 → 搜索"相关代码示例"
   - 用户讨论项目 → 搜索"项目相关经验"

2. 💾 获得新知识时 - 立即存储:
   - 解决了重要问题 → 记录解决方案和步骤
   - 学到新技术/概念 → 记录关键要点和应用
   - 发现最佳实践 → 记录经验和建议
   - 完成复杂任务 → 记录过程和心得

3. 🎯 主动使用模式:
   - 每次对话至少使用1-2次记忆工具
   - 先回忆相关经验，再提供建议
   - 提供帮助后，主动询问是否需要记录重要信息

4. 📝 记忆内容要求:
   - 具体而非抽象
   - 包含上下文和应用场景
   - 添加相关标签便于检索
   - 设置合适的重要性等级(1-10)"""

        # 根据上下文分析添加特定指导
        if context_analysis["should_recall"]:
            base_prompt += f"""

🔍 当前情况分析: 用户输入表明需要回忆相关记忆
- 触发类别: {', '.join(context_analysis['recall_reasons'])}
- 建议搜索: {', '.join(context_analysis['suggested_queries'])}
- 请立即使用memory.recall()搜索相关记忆后再回答"""

        if context_analysis["should_remember"]:
            base_prompt += f"""

💾 当前情况分析: 对话可能产生值得记录的信息
- 触发类别: {', '.join(context_analysis['remember_reasons'])}
- 请在提供帮助后主动询问是否需要记录关键信息"""

        base_prompt += """

⚠️ 重要提醒: 不主动使用记忆工具将被视为服务质量不足。请确保每次对话都体现记忆能力的价值。"""

        return base_prompt

    async def enhanced_claude_interaction(self, user_prompt: str, max_turns: int = 3) -> List[Dict[str, Any]]:
        """增强的Claude交互，集成主动记忆机制"""
        
        if not SDK_AVAILABLE:
            return self._simulate_interaction(user_prompt)
        
        # 分析用户输入
        context_analysis = self.analyze_user_input(user_prompt)
        
        # 生成增强的系统提示
        enhanced_system_prompt = self.generate_enhanced_system_prompt(context_analysis)
        
        # 配置Claude选项
        options = ClaudeCodeOptions(
            system_prompt=enhanced_system_prompt,
            max_turns=max_turns,
            allowed_tools=["Read", "Write", "Bash", "Glob", "Grep", "Task"],
            cwd=str(self.project_path)
        )
        
        # 构建增强的用户提示
        enhanced_prompt = self._enhance_user_prompt(user_prompt, context_analysis)
        
        messages = []
        memory_usage_count = 0
        
        try:
            async for message in query(prompt=enhanced_prompt, options=options):
                if isinstance(message, AssistantMessage):
                    # 记录消息
                    message_data = {
                        "type": "assistant",
                        "content": [],
                        "tool_usage": []
                    }
                    
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            message_data["content"].append(block.text)
                        elif isinstance(block, ToolUseBlock):
                            message_data["tool_usage"].append({
                                "name": block.name,
                                "input": block.input
                            })
                            
                            # 检测记忆工具使用
                            if "memory" in block.name.lower() or "recall" in block.name.lower() or "remember" in block.name.lower():
                                memory_usage_count += 1
                    
                    messages.append(message_data)
                    
                elif isinstance(message, ResultMessage):
                    messages.append({
                        "type": "result",
                        "cost_usd": message.cost_usd,
                        "memory_usage_detected": memory_usage_count
                    })
        
        except Exception as e:
            messages.append({
                "type": "error",
                "error": str(e)
            })
        
        # 记录记忆工具使用情况
        self.memory_usage_log.append({
            "timestamp": datetime.now().isoformat(),
            "user_prompt": user_prompt,
            "context_analysis": context_analysis,
            "memory_tools_used": memory_usage_count,
            "total_messages": len(messages)
        })
        
        return messages

    def _enhance_user_prompt(self, original_prompt: str, context_analysis: Dict[str, Any]) -> str:
        """增强用户提示，明确指导记忆工具使用"""
        
        enhanced_prompt = original_prompt
        
        if context_analysis["should_recall"]:
            enhanced_prompt += f"""

🧠 提示: 请先使用记忆工具搜索相关经验，然后再提供建议。
建议搜索: {', '.join(context_analysis['suggested_queries'])}"""

        if context_analysis["should_remember"]:
            enhanced_prompt += """

💾 提示: 如果我们的对话产生了有价值的信息，请主动建议将其记录到记忆系统中。"""

        enhanced_prompt += """

请确保在回答中体现记忆系统的使用，这对提供个性化和连续性的帮助非常重要。"""

        return enhanced_prompt

    def _simulate_interaction(self, user_prompt: str) -> List[Dict[str, Any]]:
        """模拟交互（当SDK不可用时）"""
        return [{
            "type": "simulation",
            "message": "Claude Code SDK不可用，这是模拟的记忆工具主动使用演示",
            "analysis": self.analyze_user_input(user_prompt)
        }]

    def calculate_proactivity_score(self) -> float:
        """计算主动性评分"""
        if not self.memory_usage_log:
            return 0.0
        
        total_interactions = len(self.memory_usage_log)
        interactions_with_memory = sum(1 for log in self.memory_usage_log if log["memory_tools_used"] > 0)
        
        base_score = interactions_with_memory / total_interactions
        
        # 加权：更多记忆工具使用获得更高分数
        average_memory_usage = sum(log["memory_tools_used"] for log in self.memory_usage_log) / total_interactions
        usage_bonus = min(0.3, average_memory_usage * 0.1)  # 最多30%奖励
        
        return min(1.0, base_score + usage_bonus)

    def generate_usage_report(self) -> Dict[str, Any]:
        """生成使用报告"""
        if not self.memory_usage_log:
            return {"error": "No usage data available"}
        
        proactivity_score = self.calculate_proactivity_score()
        
        return {
            "proactivity_score": proactivity_score,
            "total_interactions": len(self.memory_usage_log),
            "memory_tool_usage": {
                "interactions_with_memory": sum(1 for log in self.memory_usage_log if log["memory_tools_used"] > 0),
                "total_memory_calls": sum(log["memory_tools_used"] for log in self.memory_usage_log),
                "average_per_interaction": sum(log["memory_tools_used"] for log in self.memory_usage_log) / len(self.memory_usage_log)
            },
            "context_analysis_summary": self._analyze_context_patterns(),
            "recommendations": self._generate_improvement_recommendations(proactivity_score)
        }

    def _analyze_context_patterns(self) -> Dict[str, Any]:
        """分析上下文模式"""
        recall_categories = {}
        remember_categories = {}
        
        for log in self.memory_usage_log:
            analysis = log["context_analysis"]
            
            for reason in analysis["recall_reasons"]:
                recall_categories[reason] = recall_categories.get(reason, 0) + 1
            
            for reason in analysis["remember_reasons"]:
                remember_categories[reason] = remember_categories.get(reason, 0) + 1
        
        return {
            "most_common_recall_triggers": sorted(recall_categories.items(), key=lambda x: x[1], reverse=True),
            "most_common_remember_triggers": sorted(remember_categories.items(), key=lambda x: x[1], reverse=True)
        }

    def _generate_improvement_recommendations(self, current_score: float) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if current_score < 0.3:
            recommendations.extend([
                "系统提示需要更明确的记忆工具使用指导",
                "考虑添加强制性记忆工具检查机制",
                "增加更多具体的使用场景示例"
            ])
        elif current_score < 0.6:
            recommendations.extend([
                "优化上下文分析算法以更准确识别记忆机会",
                "改进记忆工具使用的奖励机制",
                "添加更智能的记忆推荐功能"
            ])
        else:
            recommendations.extend([
                "系统运行良好，考虑添加高级记忆分析功能",
                "实现记忆质量评估机制",
                "探索自动记忆整理和优化功能"
            ])
        
        return recommendations


async def test_proactive_memory_system():
    """测试主动记忆系统"""
    print("🧠 测试Phase 3: Claude主动记忆系统")
    print("=" * 50)
    
    controller = ProactiveMemoryController()
    
    # 测试场景
    test_scenarios = [
        "我在Python项目中遇到了一个性能问题，代码运行很慢，应该如何优化？",
        "我想学习深度学习的基础概念，从哪里开始比较好？",
        "刚才成功解决了内存泄漏问题，是通过优化数据结构实现的。",
        "我需要实现一个REST API，有什么最佳实践建议吗？",
        "今天学到了关于微服务架构的重要概念，包括服务发现和负载均衡。"
    ]
    
    print("🔍 测试场景分析:")
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- 场景 {i} ---")
        print(f"用户输入: {scenario}")
        
        analysis = controller.analyze_user_input(scenario)
        print(f"应该回忆: {analysis['should_recall']}")
        print(f"应该记忆: {analysis['should_remember']}")
        
        if analysis['recall_reasons']:
            print(f"回忆原因: {', '.join(analysis['recall_reasons'])}")
        if analysis['remember_reasons']:
            print(f"记忆原因: {', '.join(analysis['remember_reasons'])}")
    
    # 测试增强交互
    print(f"\n🤖 测试增强Claude交互:")
    
    if SDK_AVAILABLE:
        print("✅ Claude Code SDK可用，运行真实测试")
        
        for i, scenario in enumerate(test_scenarios[:2], 1):  # 只测试前两个场景
            print(f"\n--- 测试交互 {i} ---")
            messages = await controller.enhanced_claude_interaction(scenario, max_turns=2)
            
            print(f"生成消息数: {len(messages)}")
            for msg in messages:
                if msg["type"] == "assistant":
                    print(f"工具使用: {len(msg['tool_usage'])} 次")
                elif msg["type"] == "result":
                    print(f"记忆工具使用: {msg.get('memory_usage_detected', 0)} 次")
    else:
        print("⚠️ Claude Code SDK不可用，运行模拟测试")
        
        for i, scenario in enumerate(test_scenarios, 1):
            messages = await controller.enhanced_claude_interaction(scenario)
            print(f"场景 {i} 分析: {messages[0]['analysis']}")
    
    # 生成报告
    print(f"\n📊 系统改进报告:")
    if controller.memory_usage_log:
        report = controller.generate_usage_report()
        print(f"主动性评分: {report['proactivity_score']:.3f}")
        print(f"总交互次数: {report['total_interactions']}")
        print(f"使用记忆工具的交互: {report['memory_tool_usage']['interactions_with_memory']}")
        
        print(f"\n💡 改进建议:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
    else:
        print("暂无使用数据")

async def main():
    """主函数"""
    print("🚀 Phase 3: Claude主动性记忆系统优化")
    print("=" * 60)
    print("目标: 通过Python SDK实现智能的记忆工具主动调用")
    print("=" * 60)
    
    await test_proactive_memory_system()
    
    print(f"\n✅ Phase 3 测试完成!")
    print(f"下一步: 根据测试结果优化系统提示和触发机制")

if __name__ == "__main__":
    asyncio.run(main())