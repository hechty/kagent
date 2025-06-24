#!/usr/bin/env python3
"""
实际测试Claude Code记忆工具集成
提供完整的测试流程和验证方法
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加SDK路径
sys.path.insert(0, str(Path(__file__).parent / "claude-code-sdk-python" / "src"))

try:
    from claude_code_sdk import query, ClaudeCodeOptions
except ImportError:
    print("❌ Claude Code SDK未安装或路径不正确")
    print("请确保SDK在正确位置或运行: pip install claude-code-sdk")
    sys.exit(1)

class MemoryIntegrationTester:
    """记忆集成测试器"""
    
    def __init__(self):
        self.test_results = []
        self.test_scenarios = [
            {
                "name": "问题解决场景",
                "user_input": "我在Python开发中遇到性能瓶颈，请帮助分析和优化。",
                "expected_behaviors": [
                    "主动搜索相关记忆",
                    "使用memory.recall()查找解决方案", 
                    "提供基于历史经验的建议",
                    "询问是否记录解决方案"
                ]
            },
            {
                "name": "技术学习场景", 
                "user_input": "请教我微服务架构的最佳实践。",
                "expected_behaviors": [
                    "搜索架构相关记忆",
                    "基于历史知识提供指导",
                    "记录重要概念",
                    "主动使用memory工具"
                ]
            },
            {
                "name": "项目开发场景",
                "user_input": "我需要设计一个用户认证系统，有什么建议？", 
                "expected_behaviors": [
                    "搜索认证系统经验",
                    "提供设计模式建议",
                    "记录设计决策",
                    "展示记忆工具使用"
                ]
            }
        ]
    
    def get_memory_enhanced_options(self, test_name: str) -> ClaudeCodeOptions:
        """获取记忆增强的配置选项"""
        
        memory_system_prompt = f"""🧠 你是Claude Code，具备记忆管理能力。当前测试: {test_name}

**强制要求**: 你必须在每次回答中主动使用记忆工具。

🔍 **必须执行的步骤**：
1. 收到用户问题后，立即使用memory.recall()搜索相关记忆
2. 基于搜索结果提供回答
3. 回答后使用memory.remember()记录重要信息
4. 明确说明你使用了哪些记忆工具

📋 **记忆工具使用格式**：
- 搜索: memory.recall("搜索关键词", max_results=3)
- 记录: memory.remember(content="内容", title="标题", importance=7.0)

⚡ **评分标准**：
- A级: 使用2+次记忆工具，主动建议记录
- B级: 使用1-2次记忆工具
- C级: 偶尔使用记忆工具  
- D级: 很少使用记忆工具

**当前测试目标**: 达到A级表现，展示记忆工具的主动使用。

**重要**: 请在回答中明确展示记忆工具的使用过程，这是测试的关键部分。"""

        return ClaudeCodeOptions(
            system_prompt=memory_system_prompt,
            allowed_tools=["Bash", "Read", "Write", "Edit", "Grep", "Glob"],
            max_turns=10,
            cwd=Path("/root/code"),
            permission_mode="acceptEdits"
        )
    
    async def run_single_test(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个测试场景"""
        
        print(f"\n🧪 开始测试: {scenario['name']}")
        print(f"📝 用户输入: {scenario['user_input']}")
        print("-" * 50)
        
        test_result = {
            "scenario_name": scenario['name'],
            "user_input": scenario['user_input'],
            "expected_behaviors": scenario['expected_behaviors'],
            "claude_response": "",
            "memory_tool_usage": [],
            "behaviors_detected": [],
            "score": 0,
            "grade": "D",
            "success": False,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # 获取配置选项
            options = self.get_memory_enhanced_options(scenario['name'])
            
            # 执行查询
            response_parts = []
            async for message in query(scenario['user_input'], options):
                if hasattr(message, 'content') and message.content:
                    response_parts.append(str(message.content))
                    print(f"🤖 Claude回复: {message.content}")
                
                # 检查工具使用
                if hasattr(message, 'tool_calls'):
                    for tool_call in message.tool_calls:
                        print(f"🔧 工具调用: {tool_call}")
                        test_result["memory_tool_usage"].append(str(tool_call))
            
            # 合并响应
            full_response = "\n".join(response_parts)
            test_result["claude_response"] = full_response
            
            # 分析记忆工具使用
            memory_usage_score = self.analyze_memory_usage(full_response)
            test_result.update(memory_usage_score)
            
            print(f"📊 测试结果: {test_result['grade']} ({test_result['score']}/10)")
            print(f"✅ 检测到的行为: {', '.join(test_result['behaviors_detected'])}")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            test_result["error"] = str(e)
        
        return test_result
    
    def analyze_memory_usage(self, response: str) -> Dict[str, Any]:
        """分析记忆工具使用情况"""
        
        memory_indicators = {
            "recall_usage": ["memory.recall", "搜索记忆", "查找相关", "回忆中"],
            "remember_usage": ["memory.remember", "记录", "存储", "保存到记忆"],
            "proactive_behavior": ["让我先搜索", "我来查找", "需要记录", "是否保存"],
            "memory_reference": ["基于记忆", "从记忆中", "历史经验", "之前遇到过"]
        }
        
        detected_behaviors = []
        usage_count = 0
        
        response_lower = response.lower()
        
        for behavior, indicators in memory_indicators.items():
            for indicator in indicators:
                if indicator.lower() in response_lower:
                    detected_behaviors.append(behavior)
                    usage_count += 1
                    break
        
        # 评分逻辑
        if usage_count >= 3:
            grade = "A"
            score = 9 + min(usage_count - 3, 1)  # 9-10分
        elif usage_count >= 2:
            grade = "B" 
            score = 7 + (usage_count - 2)  # 7-8分
        elif usage_count >= 1:
            grade = "C"
            score = 5 + (usage_count - 1)  # 5-6分
        else:
            grade = "D"
            score = max(0, len(detected_behaviors))  # 0-4分
        
        return {
            "behaviors_detected": detected_behaviors,
            "memory_usage_count": usage_count,
            "score": score,
            "grade": grade,
            "success": grade in ["A", "B"]
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试场景"""
        
        print("🚀 开始Claude Code记忆工具集成测试")
        print("=" * 60)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试场景数: {len(self.test_scenarios)}")
        print("=" * 60)
        
        # 执行所有测试
        for scenario in self.test_scenarios:
            result = await self.run_single_test(scenario)
            self.test_results.append(result)
            
            # 测试间隔
            await asyncio.sleep(2)
        
        # 生成总结报告
        return self.generate_test_report()
    
    def generate_test_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        average_score = sum(r["score"] for r in self.test_results) / total_tests if total_tests > 0 else 0
        
        grade_distribution = {}
        for result in self.test_results:
            grade = result["grade"]
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
                "average_score": average_score,
                "overall_grade": self.calculate_overall_grade(average_score)
            },
            "grade_distribution": grade_distribution,
            "detailed_results": self.test_results,
            "recommendations": self.generate_recommendations(),
            "timestamp": datetime.now().isoformat()
        }
        
        # 打印报告摘要
        print("\n" + "=" * 60)
        print("📋 测试报告摘要")
        print("=" * 60)
        print(f"总测试数: {total_tests}")
        print(f"成功测试: {successful_tests}")
        print(f"成功率: {report['test_summary']['success_rate']:.1%}")
        print(f"平均分数: {average_score:.1f}/10")
        print(f"整体评级: {report['test_summary']['overall_grade']}")
        
        print(f"\n📊 评级分布:")
        for grade, count in grade_distribution.items():
            print(f"   {grade}级: {count} 个测试")
        
        print(f"\n💡 改进建议:")
        for rec in report["recommendations"]:
            print(f"   • {rec}")
        
        return report
    
    def calculate_overall_grade(self, average_score: float) -> str:
        """计算整体评级"""
        if average_score >= 8.5:
            return "A级 (优秀)"
        elif average_score >= 7.0:
            return "B级 (良好)"
        elif average_score >= 5.0:
            return "C级 (及格)" 
        else:
            return "D级 (需改进)"
    
    def generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        
        recommendations = []
        
        # 分析失败的测试
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            recommendations.append(f"有{len(failed_tests)}个测试未达到预期，需要加强系统提示")
        
        # 分析记忆工具使用情况
        total_usage = sum(r["memory_usage_count"] for r in self.test_results)
        if total_usage < len(self.test_results) * 2:
            recommendations.append("记忆工具使用频率偏低，建议强化提示语言")
        
        # 分析评级分布
        d_grade_count = sum(1 for r in self.test_results if r["grade"] == "D")
        if d_grade_count > 0:
            recommendations.append("存在D级表现，建议检查系统提示的强制性表述")
        
        if not recommendations:
            recommendations.append("测试表现良好，建议继续保持当前配置")
        
        return recommendations

# 简化测试函数
async def quick_test():
    """快速测试函数"""
    print("🚀 快速记忆工具测试")
    
    # 简单的测试配置
    simple_prompt = """🧠 你必须使用记忆工具！

对于用户的每个问题：
1. 先用memory.recall()搜索相关记忆
2. 基于记忆结果回答
3. 用memory.remember()记录重要信息

请在回答中明确说明使用了哪些记忆工具。"""

    options = ClaudeCodeOptions(
        system_prompt=simple_prompt,
        max_turns=5,
        cwd=Path("/root/code")
    )
    
    test_question = "Python代码性能优化有什么技巧？"
    print(f"❓ 测试问题: {test_question}")
    print("-" * 40)
    
    try:
        async for message in query(test_question, options):
            if hasattr(message, 'content') and message.content:
                print(f"🤖 回复: {message.content}")
                
                # 简单分析
                response = str(message.content).lower()
                memory_used = any(keyword in response for keyword in [
                    "memory.recall", "memory.remember", "搜索记忆", "记录"
                ])
                
                print(f"📊 记忆工具使用: {'✅ 是' if memory_used else '❌ 否'}")
                break
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")

# 主函数
async def main():
    """主测试函数"""
    print("🧠 Claude Code 记忆工具集成测试")
    print("选择测试模式:")
    print("1. 完整测试 (推荐)")
    print("2. 快速测试")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "2":
        await quick_test()
    else:
        # 完整测试
        tester = MemoryIntegrationTester()
        report = await tester.run_all_tests()
        
        # 保存报告
        report_path = Path("memory_integration_test_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 完整测试报告已保存到: {report_path}")

if __name__ == "__main__":
    asyncio.run(main())