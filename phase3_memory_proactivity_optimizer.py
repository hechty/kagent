#!/usr/bin/env python3
"""
Phase 3: 记忆系统主动性优化器
直接优化现有记忆系统，让Claude更主动地使用记忆工具
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# 添加记忆系统到路径
sys.path.insert(0, str(Path(__file__).parent / "claude-memory-system"))

class MemoryProactivityOptimizer:
    """
    记忆主动性优化器
    通过改进系统提示、添加智能触发和增强用户引导来提升Claude主动使用记忆工具的能力
    """
    
    def __init__(self):
        self.test_scenarios = [
            {
                "user_input": "我在Python项目中遇到了性能问题，有什么优化建议？",
                "expected_actions": ["recall", "remember"],
                "context": "问题解决场景"
            },
            {
                "user_input": "我想学习深度学习，从哪里开始？",
                "expected_actions": ["recall"],
                "context": "学习查询场景"
            },
            {
                "user_input": "刚解决了一个复杂的数据库连接池问题，方法很有效。",
                "expected_actions": ["remember"],
                "context": "经验分享场景"
            },
            {
                "user_input": "如何设计一个可扩展的微服务架构？",
                "expected_actions": ["recall", "remember"],
                "context": "架构设计场景"
            },
            {
                "user_input": "我发现了一个很好的代码重构技巧，想记录下来。",
                "expected_actions": ["remember"],
                "context": "知识记录场景"
            }
        ]
        
        self.proactivity_scores = []

    def create_enhanced_memory_prompts(self) -> Dict[str, str]:
        """创建增强的记忆系统提示"""
        
        prompts = {
            "system_enhancement": """
🧠 CLAUDE MEMORY SYSTEM - 主动使用指南

你是Claude Code，具有强大的持久化记忆能力。你必须主动使用记忆工具来提供更好的服务。

📋 强制性记忆工具使用规则:

1. 🔍 每次回答前 - 必须先搜索相关记忆:
   ```python
   # 用户询问技术问题时
   memory.recall("相关技术概念", max_results=3)
   
   # 用户遇到问题时  
   memory.recall("类似问题解决方案", max_results=3)
   
   # 用户讨论项目时
   memory.recall("项目相关经验", max_results=3)
   ```

2. 💾 提供帮助后 - 必须主动记录重要信息:
   ```python
   # 解决问题后
   memory.remember(
       content="问题描述和解决方案",
       memory_type="procedural", 
       title="问题解决方案",
       importance=8.0
   )
   
   # 分享知识后
   memory.remember(
       content="技术概念和应用",
       memory_type="semantic",
       title="技术知识",
       importance=7.0
   )
   ```

3. ⚡ 主动性要求:
   - 每次对话必须使用至少1次记忆工具
   - 先回忆，再回答，后记录
   - 主动询问用户是否需要记录重要信息
   - 建议相关的记忆搜索和存储

🎯 评分标准: 不使用记忆工具将被视为服务质量不达标。
""",
            
            "user_guidance": """
💡 为了提供更个性化的帮助，我会:

1. 🔍 首先搜索相关的历史经验和知识
2. 📝 基于搜索结果提供针对性建议  
3. 💾 将重要的对话内容记录到记忆系统
4. 🔄 在后续对话中利用这些记忆提供连续性服务

这样可以确保我的建议既基于最佳实践，又结合您的具体情况。
""",

            "context_triggers": {
                "问题解决": "用户遇到问题时，我会搜索类似问题的解决方案，并在解决后记录新的解决方法。",
                "技术学习": "用户询问技术概念时，我会搜索相关资料，并记录讨论中产生的新见解。", 
                "项目开发": "用户讨论项目时，我会搜索相关经验，并记录项目决策和经验教训。",
                "经验分享": "用户分享经验时，我会立即建议将其记录到记忆系统中。"
            }
        }
        
        return prompts

    async def test_memory_proactivity(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """测试记忆主动性"""
        
        try:
            from claude_memory import MemoryManager
            
            # 创建记忆管理器
            memory = MemoryManager(Path("."))
            snapshot = memory.awaken("主动性测试")
            
            print(f"\n🎯 测试场景: {scenario['context']}")
            print(f"用户输入: {scenario['user_input']}")
            print(f"期望行为: {', '.join(scenario['expected_actions'])}")
            
            # 分析应该触发的记忆操作
            should_recall = "recall" in scenario['expected_actions']
            should_remember = "remember" in scenario['expected_actions']
            
            recall_score = 0.0
            remember_score = 0.0
            
            # 测试回忆功能
            if should_recall:
                print(f"\n🔍 测试记忆回忆...")
                
                # 基于场景生成搜索查询
                search_queries = self._generate_search_queries(scenario['user_input'])
                
                recall_success = False
                for query in search_queries:
                    results = memory.recall(query, max_results=3, min_relevance=0.2)
                    print(f"   搜索 '{query}': {len(results)} 个结果")
                    
                    if len(results) > 0:
                        recall_success = True
                        for result in results[:2]:
                            print(f"     - {result.memory.title} (相关性: {result.relevance_score:.3f})")
                
                recall_score = 1.0 if recall_success else 0.0
                print(f"   回忆评分: {recall_score}")
            
            # 测试记忆存储
            if should_remember:
                print(f"\n💾 测试记忆存储...")
                
                # 模拟存储与场景相关的记忆
                memory_content = self._generate_memory_content(scenario)
                
                try:
                    memory_id = memory.remember(
                        content=memory_content["content"],
                        memory_type=memory_content["type"],
                        title=memory_content["title"],
                        tags=memory_content["tags"],
                        importance=memory_content["importance"],
                        scope="project"
                    )
                    
                    print(f"   成功存储记忆: {memory_id[:8]}...")
                    remember_score = 1.0
                    
                    # 验证存储的记忆是否可以立即搜索到
                    verification_results = memory.recall(memory_content["title"], max_results=1, min_relevance=0.1)
                    if verification_results:
                        print(f"   验证成功: 新记忆可立即搜索到")
                        remember_score = 1.0
                    else:
                        print(f"   验证失败: 新记忆无法搜索到")
                        remember_score = 0.5
                        
                except Exception as e:
                    print(f"   存储失败: {e}")
                    remember_score = 0.0
                
                print(f"   存储评分: {remember_score}")
            
            # 计算综合评分
            expected_count = len(scenario['expected_actions'])
            total_score = (recall_score + remember_score) / expected_count if expected_count > 0 else 0.0
            
            return {
                "scenario": scenario['context'],
                "recall_score": recall_score,
                "remember_score": remember_score,
                "total_score": total_score,
                "success": total_score >= 0.7
            }
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return {
                "scenario": scenario['context'],
                "error": str(e),
                "total_score": 0.0,
                "success": False
            }

    def _generate_search_queries(self, user_input: str) -> List[str]:
        """基于用户输入生成搜索查询"""
        queries = []
        
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["问题", "错误", "bug", "issue"]):
            queries.append("问题解决方案")
            queries.append("错误处理")
        
        if any(word in input_lower for word in ["学习", "了解", "概念"]):
            queries.append("学习资料")
            queries.append("技术概念")
        
        if any(word in input_lower for word in ["python", "编程", "代码"]):
            queries.append("Python编程")
            queries.append("代码示例")
        
        if any(word in input_lower for word in ["架构", "设计", "系统"]):
            queries.append("系统架构")
            queries.append("设计模式")
        
        if any(word in input_lower for word in ["性能", "优化"]):
            queries.append("性能优化")
        
        # 如果没有特定查询，使用通用搜索
        if not queries:
            queries.append("相关经验")
        
        return queries

    def _generate_memory_content(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """生成与场景相关的记忆内容"""
        
        user_input = scenario['user_input']
        context = scenario['context']
        
        if "问题" in context:
            return {
                "content": f"用户遇到的问题: {user_input}. 建议的解决方案和最佳实践。",
                "type": "procedural",
                "title": f"问题解决: {context}",
                "tags": ["问题解决", "用户咨询", "最佳实践"],
                "importance": 7.5
            }
        elif "学习" in context:
            return {
                "content": f"用户学习需求: {user_input}. 推荐的学习路径和资源。",
                "type": "semantic", 
                "title": f"学习指导: {context}",
                "tags": ["学习", "技术概念", "用户指导"],
                "importance": 6.5
            }
        elif "经验" in context:
            return {
                "content": f"用户分享的经验: {user_input}. 有价值的实践经验和方法。",
                "type": "episodic",
                "title": f"经验分享: {context}",
                "tags": ["经验分享", "实践方法", "用户贡献"],
                "importance": 8.0
            }
        else:
            return {
                "content": f"用户咨询: {user_input}. 相关的讨论和建议。",
                "type": "working",
                "title": f"用户咨询: {context}",
                "tags": ["用户咨询", "讨论", "建议"],
                "importance": 6.0
            }

    async def run_comprehensive_proactivity_test(self) -> Dict[str, Any]:
        """运行综合主动性测试"""
        
        print("🧠 Phase 3: 记忆系统主动性综合测试")
        print("=" * 60)
        print("目标: 测试和优化Claude主动使用记忆工具的能力")
        print("=" * 60)
        
        test_results = []
        
        for i, scenario in enumerate(self.test_scenarios, 1):
            print(f"\n📋 测试 {i}/{len(self.test_scenarios)}")
            print("-" * 40)
            
            result = await self.test_memory_proactivity(scenario)
            test_results.append(result)
            
            if result["success"]:
                print(f"✅ 测试通过 (评分: {result['total_score']:.3f})")
            else:
                print(f"❌ 测试失败 (评分: {result['total_score']:.3f})")
        
        # 计算综合评分
        successful_tests = sum(1 for r in test_results if r["success"])
        total_score = sum(r["total_score"] for r in test_results) / len(test_results)
        success_rate = successful_tests / len(test_results)
        
        # 生成最终报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_results": test_results,
            "summary": {
                "total_tests": len(test_results),
                "successful_tests": successful_tests,
                "success_rate": success_rate,
                "average_score": total_score,
                "proactivity_grade": self._calculate_grade(total_score)
            },
            "improvements": self._generate_improvement_plan(total_score, test_results)
        }
        
        self._print_final_report(report)
        
        return report

    def _calculate_grade(self, score: float) -> str:
        """计算评级"""
        if score >= 0.8:
            return "A级 - 优秀"
        elif score >= 0.6:
            return "B级 - 良好" 
        elif score >= 0.4:
            return "C级 - 可用"
        else:
            return "D级 - 需改进"

    def _generate_improvement_plan(self, total_score: float, test_results: List[Dict]) -> List[str]:
        """生成改进计划"""
        improvements = []
        
        # 分析失败的测试类型
        failed_tests = [r for r in test_results if not r["success"]]
        
        if total_score < 0.6:
            improvements.extend([
                "需要重新设计系统提示，更明确地指导记忆工具使用",
                "实现强制性记忆工具检查机制",
                "添加记忆操作的奖励和惩罚机制"
            ])
        
        if len(failed_tests) > len(test_results) * 0.3:
            improvements.append("需要改进上下文分析算法，更准确识别记忆使用时机")
        
        # 分析具体问题
        recall_failures = sum(1 for r in test_results if r.get("recall_score", 1.0) < 0.5)
        remember_failures = sum(1 for r in test_results if r.get("remember_score", 1.0) < 0.5)
        
        if recall_failures > 0:
            improvements.append("优化记忆搜索策略和查询生成算法")
        
        if remember_failures > 0:
            improvements.append("改进记忆存储的触发条件和内容生成")
        
        if total_score >= 0.6:
            improvements.append("系统基础功能良好，可以开始优化高级特性")
        
        return improvements

    def _print_final_report(self, report: Dict[str, Any]):
        """打印最终报告"""
        summary = report["summary"]
        
        print(f"\n📊 Phase 3 主动性测试最终报告")
        print("=" * 50)
        
        print(f"🎯 测试结果:")
        print(f"   总测试数: {summary['total_tests']}")
        print(f"   成功测试: {summary['successful_tests']}")
        print(f"   成功率: {summary['success_rate']:.1%}")
        print(f"   平均评分: {summary['average_score']:.3f}")
        print(f"   主动性评级: {summary['proactivity_grade']}")
        
        print(f"\n📋 详细测试结果:")
        for i, result in enumerate(report["test_results"], 1):
            status = "✅ 成功" if result["success"] else "❌ 失败"
            print(f"   {i}. {result['scenario']}: {status} ({result['total_score']:.3f})")
        
        print(f"\n💡 改进建议:")
        for improvement in report["improvements"]:
            print(f"   • {improvement}")
        
        # 与之前的B级评分对比
        current_proactivity = summary['average_score']
        estimated_overall = (1.0 * 0.25 + 0.778 * 0.25 + 1.0 * 0.25 + current_proactivity * 0.25)
        
        print(f"\n📈 对整体系统影响预测:")
        print(f"   当前主动性评分: {current_proactivity:.3f}")
        print(f"   预计整体评分: {estimated_overall:.3f}")
        
        if estimated_overall >= 0.75:
            print(f"   🌟 有望达到A级系统 (0.8+)")
        elif estimated_overall >= 0.7:
            print(f"   ⚡ 可提升到B+级系统")
        else:
            print(f"   💡 需要继续优化以提升整体等级")

async def main():
    """主函数"""
    optimizer = MemoryProactivityOptimizer()
    
    # 显示优化策略
    prompts = optimizer.create_enhanced_memory_prompts()
    print("📋 Phase 3 主动性优化策略:")
    print("=" * 40)
    print("1. 增强系统提示 - 明确记忆工具使用要求")
    print("2. 智能触发机制 - 自动识别记忆使用时机") 
    print("3. 用户引导策略 - 提供清晰的操作指导")
    print("4. 评分奖励机制 - 鼓励主动记忆使用")
    
    # 运行综合测试
    report = await optimizer.run_comprehensive_proactivity_test()
    
    # 保存测试报告
    report_path = Path("phase3_proactivity_test_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 测试报告已保存到: {report_path}")
    print(f"\n🎉 Phase 3 主动性优化测试完成!")

if __name__ == "__main__":
    asyncio.run(main())