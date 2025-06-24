#!/usr/bin/env python3
"""
测试Claude Code主动调用记忆工具的机制
研究如何让Claude自动在适当时机使用记忆系统
"""

import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any

# 添加记忆系统到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "claude-memory-system"))

from claude_memory import MemoryManager
from claude_code_sdk import (
    query,
    ClaudeCodeOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock
)

class ProactiveMemoryTester:
    """主动记忆使用测试器"""
    
    def __init__(self):
        self.test_results = []
        self.memory_usage_patterns = []
        
    async def create_memory_enhanced_prompt_system(self):
        """创建增强记忆功能的提示系统"""
        
        # 创建增强的系统提示，指导Claude主动使用记忆
        memory_enhanced_system = """
你是Claude Code，一个智能编程助手，具备记忆管理能力。

🧠 记忆系统使用指南：
你可以使用位于../claude-memory-system/的记忆管理工具，通过以下命令：

1. claude-memory awaken [context] - 苏醒记忆系统，获取当前状态
2. claude-memory remember [content] --type [semantic|episodic|procedural|working] --title [title] --tags [tags] --importance [0-10]
3. claude-memory recall [query] --max-results [num] --min-relevance [0-1]
4. claude-memory invoke [capability] --params [json]
5. claude-memory reflect - 分析记忆使用模式
6. claude-memory suggest [context] - 获取智能建议

⚡ 主动使用时机：
- 任务开始时：使用awaken了解相关记忆
- 遇到技术问题时：使用recall搜索相关解决方案
- 学到新知识时：使用remember存储重要信息
- 需要执行重复任务时：使用invoke调用已有能力
- 需要建议时：使用suggest获取智能推荐
- 完成复杂任务后：使用reflect分析经验

🎯 记忆使用原则：
1. 主动思考：遇到问题先搜索记忆中的相关经验
2. 及时存储：学到有价值的知识立即记住
3. 经验复用：优先使用已有的工具和解决方案
4. 持续学习：定期反思和优化记忆结构

请在执行任务时主动、频繁地使用记忆系统来：
- 提高工作效率
- 积累知识经验
- 避免重复劳动
- 提供更好的解决方案
        """
        
        return memory_enhanced_system
    
    async def test_proactive_problem_solving(self):
        """测试主动问题解决场景"""
        print("🧠 测试场景1: 主动问题解决")
        print("=" * 50)
        
        system_prompt = await self.create_memory_enhanced_prompt_system()
        
        options = ClaudeCodeOptions(
            system_prompt=system_prompt,
            allowed_tools=["Bash", "Read", "Write", "Edit"],
            max_turns=15,
            cwd="/root/code/claude-memory-test"
        )
        
        # 测试任务：需要Claude主动使用记忆来解决编程问题
        test_prompt = """
我遇到了一个Python性能问题：

问题描述：
我有一个Python脚本需要处理大量数据，但运行很慢。脚本需要：
1. 读取一个10GB的CSV文件
2. 对数据进行清洗和转换
3. 计算统计指标
4. 生成可视化图表
5. 输出结果到文件

请帮我优化这个脚本的性能。在解决这个问题时，请：
1. 首先查看你的记忆中是否有相关的性能优化经验
2. 如果找到相关经验，应用这些解决方案
3. 如果没有找到，创建新的解决方案并存储到记忆中
4. 最后反思这次问题解决的过程

请主动使用记忆系统来帮助解决这个问题。
        """
        
        print("发送任务给Claude...")
        print("-" * 30)
        
        memory_usage_count = 0
        tool_usage_pattern = []
        
        try:
            async for message in query(prompt=test_prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(f"Claude: {block.text}")
                        elif isinstance(block, ToolUseBlock):
                            tool_name = block.name
                            print(f"🔧 工具使用: {tool_name}")
                            
                            # 检查是否使用了记忆相关命令
                            if tool_name == "Bash" and hasattr(block, 'input'):
                                command = block.input.get('command', '')
                                if 'claude-memory' in command:
                                    memory_usage_count += 1
                                    memory_cmd = command.split('claude-memory')[1].strip().split()[0] if 'claude-memory' in command else 'unknown'
                                    tool_usage_pattern.append(f"memory_{memory_cmd}")
                                    print(f"   📚 记忆操作: {memory_cmd}")
                                else:
                                    tool_usage_pattern.append(f"tool_{tool_name}")
                        elif isinstance(block, ToolResultBlock):
                            result_preview = str(block.content)[:200]
                            print(f"📊 工具结果: {result_preview}...")
                print("-" * 20)
            
            print(f"\n📊 记忆使用统计:")
            print(f"记忆操作次数: {memory_usage_count}")
            print(f"工具使用模式: {' -> '.join(tool_usage_pattern[:10])}")
            
            return {
                "scenario": "主动问题解决",
                "memory_usage_count": memory_usage_count,
                "tool_pattern": tool_usage_pattern,
                "proactive_score": min(1.0, memory_usage_count / 5.0)  # 期望至少5次记忆操作
            }
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return {"scenario": "主动问题解决", "error": str(e)}
    
    async def test_knowledge_accumulation_workflow(self):
        """测试知识积累工作流"""
        print("\n📚 测试场景2: 知识积累工作流")
        print("=" * 50)
        
        system_prompt = await self.create_memory_enhanced_prompt_system()
        
        options = ClaudeCodeOptions(
            system_prompt=system_prompt,
            allowed_tools=["Bash", "Read", "Write", "Edit"],
            max_turns=12,
            cwd="/root/code/claude-memory-test"
        )
        
        # 测试学习新技术并积累知识的场景
        test_prompt = """
我想学习Rust编程语言，请帮我制定一个学习计划并开始实践。

要求：
1. 首先检查你的记忆中是否有关于Rust的知识
2. 如果有，总结现有知识；如果没有，从头开始学习
3. 创建一个Rust学习计划
4. 写一个简单的Rust Hello World程序
5. 学习Rust的所有权系统
6. 将学到的重要概念存储到记忆中
7. 反思学习过程并提出后续建议

请在整个过程中主动使用记忆系统来管理知识。
        """
        
        print("发送学习任务给Claude...")
        print("-" * 30)
        
        knowledge_operations = 0
        learning_pattern = []
        
        try:
            async for message in query(prompt=test_prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            text = block.text
                            print(f"Claude: {text}")
                            
                            # 分析文本中的学习行为
                            if any(keyword in text.lower() for keyword in ['学习', '理解', '掌握', '记住']):
                                learning_pattern.append("learning")
                            elif any(keyword in text.lower() for keyword in ['存储', '记忆', '保存']):
                                learning_pattern.append("storing")
                        elif isinstance(block, ToolUseBlock):
                            tool_name = block.name
                            if tool_name == "Bash" and hasattr(block, 'input'):
                                command = block.input.get('command', '')
                                if 'claude-memory' in command:
                                    knowledge_operations += 1
                                    if 'remember' in command:
                                        learning_pattern.append("remember")
                                    elif 'recall' in command:
                                        learning_pattern.append("recall")
                                    elif 'awaken' in command:
                                        learning_pattern.append("awaken")
                        elif isinstance(block, ToolResultBlock):
                            print(f"📊 工具结果: {str(block.content)[:150]}...")
                print("-" * 20)
            
            print(f"\n📚 知识积累统计:")
            print(f"知识操作次数: {knowledge_operations}")
            print(f"学习模式: {' -> '.join(learning_pattern[:8])}")
            
            return {
                "scenario": "知识积累工作流",
                "knowledge_operations": knowledge_operations,
                "learning_pattern": learning_pattern,
                "accumulation_score": min(1.0, knowledge_operations / 4.0)  # 期望至少4次知识操作
            }
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return {"scenario": "知识积累工作流", "error": str(e)}
    
    async def test_capability_reuse_scenario(self):
        """测试能力复用场景"""
        print("\n⚡ 测试场景3: 能力复用场景")
        print("=" * 50)
        
        system_prompt = await self.create_memory_enhanced_prompt_system()
        
        options = ClaudeCodeOptions(
            system_prompt=system_prompt,
            allowed_tools=["Bash", "Read", "Write", "Edit"],
            max_turns=10,
            cwd="/root/code/claude-memory-test"
        )
        
        # 测试重复任务中的能力复用
        test_prompt = """
我需要分析三个不同项目的代码质量。每个项目都需要：
1. 统计代码行数和文件数量
2. 分析代码复杂度
3. 检查代码规范
4. 生成质量报告

项目路径：
- /root/code/claude-memory-system
- /root/code/claude-memory-test  
- /root/code

请帮我完成这个任务。在执行过程中：
1. 首先检查是否有现有的代码分析工具或脚本
2. 如果有，直接使用；如果没有，创建新的分析工具
3. 将有用的工具存储为可复用的能力
4. 对每个项目执行分析
5. 总结分析结果

请充分利用记忆系统的能力复用功能。
        """
        
        print("发送代码分析任务给Claude...")
        print("-" * 30)
        
        capability_operations = 0
        reuse_pattern = []
        
        try:
            async for message in query(prompt=test_prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            text = block.text
                            print(f"Claude: {text}")
                            
                            # 检测复用行为
                            if any(keyword in text.lower() for keyword in ['复用', '重用', '调用', '使用现有']):
                                reuse_pattern.append("reuse")
                            elif any(keyword in text.lower() for keyword in ['创建', '新建', '开发']):
                                reuse_pattern.append("create")
                        elif isinstance(block, ToolUseBlock):
                            tool_name = block.name
                            if tool_name == "Bash" and hasattr(block, 'input'):
                                command = block.input.get('command', '')
                                if 'claude-memory' in command:
                                    capability_operations += 1
                                    if 'invoke' in command:
                                        reuse_pattern.append("invoke")
                                    elif 'recall' in command:
                                        reuse_pattern.append("search")
                                    elif 'remember' in command and 'procedural' in command:
                                        reuse_pattern.append("store_capability")
                        elif isinstance(block, ToolResultBlock):
                            print(f"📊 工具结果: {str(block.content)[:150]}...")
                print("-" * 20)
            
            print(f"\n⚡ 能力复用统计:")
            print(f"能力操作次数: {capability_operations}")
            print(f"复用模式: {' -> '.join(reuse_pattern[:8])}")
            
            return {
                "scenario": "能力复用场景",
                "capability_operations": capability_operations,
                "reuse_pattern": reuse_pattern,
                "reuse_score": min(1.0, capability_operations / 3.0)  # 期望至少3次能力操作
            }
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return {"scenario": "能力复用场景", "error": str(e)}
    
    async def analyze_memory_usage_patterns(self, test_results: List[Dict]):
        """分析记忆使用模式"""
        print("\n🔍 记忆使用模式分析")
        print("=" * 50)
        
        total_memory_ops = sum(r.get("memory_usage_count", 0) + r.get("knowledge_operations", 0) + r.get("capability_operations", 0) for r in test_results if "error" not in r)
        total_scenarios = len([r for r in test_results if "error" not in r])
        
        if total_scenarios == 0:
            print("❌ 没有成功的测试场景")
            return {"error": "No successful scenarios"}
        
        avg_memory_usage = total_memory_ops / total_scenarios
        
        # 分析使用模式
        all_patterns = []
        for result in test_results:
            if "error" not in result:
                if "tool_pattern" in result:
                    all_patterns.extend(result["tool_pattern"])
                if "learning_pattern" in result:
                    all_patterns.extend(result["learning_pattern"])
                if "reuse_pattern" in result:
                    all_patterns.extend(result["reuse_pattern"])
        
        # 统计模式频率
        pattern_frequency = {}
        for pattern in all_patterns:
            pattern_frequency[pattern] = pattern_frequency.get(pattern, 0) + 1
        
        print(f"总记忆操作次数: {total_memory_ops}")
        print(f"平均每场景操作次数: {avg_memory_usage:.1f}")
        print(f"使用模式频率: {pattern_frequency}")
        
        # 评估主动性评分
        memory_patterns = [p for p in all_patterns if p.startswith("memory_")]
        proactive_score = len(memory_patterns) / max(1, len(all_patterns))
        
        print(f"主动记忆使用评分: {proactive_score:.3f}")
        
        return {
            "total_memory_operations": total_memory_ops,
            "avg_operations_per_scenario": avg_memory_usage,
            "pattern_frequency": pattern_frequency,
            "proactive_score": proactive_score,
            "successful_scenarios": total_scenarios
        }
    
    async def run_proactive_memory_tests(self):
        """运行主动记忆使用测试"""
        print("🧠 开始Claude Code主动记忆调用机制测试")
        print("=" * 60)
        
        # 运行各个测试场景
        test_results = []
        
        # 场景1：主动问题解决
        result1 = await self.test_proactive_problem_solving()
        test_results.append(result1)
        
        # 场景2：知识积累工作流
        result2 = await self.test_knowledge_accumulation_workflow()
        test_results.append(result2)
        
        # 场景3：能力复用场景  
        result3 = await self.test_capability_reuse_scenario()
        test_results.append(result3)
        
        # 分析记忆使用模式
        usage_analysis = await self.analyze_memory_usage_patterns(test_results)
        
        # 综合评估
        print("\n🎯 主动记忆使用综合评估")
        print("=" * 50)
        
        successful_tests = [r for r in test_results if "error" not in r]
        if successful_tests:
            # 计算各个评分
            proactive_scores = [r.get("proactive_score", 0) for r in successful_tests]
            accumulation_scores = [r.get("accumulation_score", 0) for r in successful_tests]
            reuse_scores = [r.get("reuse_score", 0) for r in successful_tests]
            
            avg_proactive = sum(proactive_scores) / len(proactive_scores) if proactive_scores else 0
            avg_accumulation = sum(accumulation_scores) / len(accumulation_scores) if accumulation_scores else 0
            avg_reuse = sum(reuse_scores) / len(reuse_scores) if reuse_scores else 0
            
            overall_score = (avg_proactive + avg_accumulation + avg_reuse) / 3
            
            print(f"主动问题解决能力: {avg_proactive:.3f}")
            print(f"知识积累能力: {avg_accumulation:.3f}")  
            print(f"能力复用能力: {avg_reuse:.3f}")
            print(f"整体主动性评分: {overall_score:.3f}")
            
            if overall_score >= 0.7:
                print("✅ Claude Code具备优秀的主动记忆使用能力")
            elif overall_score >= 0.4:
                print("⚠️ Claude Code具备基本的主动记忆使用能力，但需要改进")
            else:
                print("❌ Claude Code的主动记忆使用能力需要显著提升")
        else:
            print("❌ 所有测试场景都失败了")
            overall_score = 0
        
        return {
            "overall_score": overall_score,
            "test_results": test_results,
            "usage_analysis": usage_analysis,
            "recommendations": self.generate_improvement_recommendations(test_results, usage_analysis)
        }
    
    def generate_improvement_recommendations(self, test_results: List[Dict], usage_analysis: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if usage_analysis.get("proactive_score", 0) < 0.5:
            recommendations.append("增强系统提示，更明确地指导Claude主动使用记忆工具")
        
        if usage_analysis.get("avg_operations_per_scenario", 0) < 3:
            recommendations.append("优化记忆工具的易用性，降低使用门槛")
        
        memory_patterns = [p for p in usage_analysis.get("pattern_frequency", {}).keys() if p.startswith("memory_")]
        if len(memory_patterns) < 3:
            recommendations.append("扩展记忆操作类型，提供更多样化的记忆功能")
        
        if any("error" in r for r in test_results):
            recommendations.append("改进错误处理和用户引导，确保记忆工具可靠性")
        
        return recommendations

async def main():
    """主测试函数"""
    tester = ProactiveMemoryTester()
    
    try:
        results = await tester.run_proactive_memory_tests()
        
        # 保存测试结果
        results_file = Path("/root/code/claude-memory-test/proactive_memory_test_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n📁 详细测试结果已保存到: {results_file}")
        
        # 输出改进建议
        if results.get("recommendations"):
            print(f"\n💡 改进建议:")
            for i, rec in enumerate(results["recommendations"], 1):
                print(f"{i}. {rec}")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())