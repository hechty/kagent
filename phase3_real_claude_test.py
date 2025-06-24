#!/usr/bin/env python3
"""
Phase 3: 真实Claude Code主动性测试
使用实际的Claude Code来测试记忆工具的主动使用
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class RealClaudeProactivityTester:
    """
    真实Claude主动性测试器
    通过实际调用Claude Code来测试记忆工具的主动使用情况
    """
    
    def __init__(self):
        self.test_results = []
        self.memory_usage_patterns = []
        
        # 测试用例：设计为引导Claude主动使用记忆工具
        self.test_cases = [
            {
                "prompt": """我在开发一个Python Web应用时遇到了性能瓶颈。请帮我分析可能的原因并提供优化建议。

提示：请先搜索你的记忆中是否有类似的性能优化经验，然后基于这些经验给出建议。在提供建议后，请将这次的优化方案记录到记忆系统中。""",
                "expected_memory_actions": ["recall", "remember"],
                "scenario": "性能优化咨询"
            },
            {
                "prompt": """我想学习微服务架构的最佳实践。你之前是否讨论过相关话题？请先查看记忆中的相关内容，然后给我一个学习路线图。

请使用记忆工具搜索相关的架构设计经验，并在我们讨论后将重要的学习要点记录下来。""",
                "expected_memory_actions": ["recall", "remember"], 
                "scenario": "技术学习指导"
            },
            {
                "prompt": """我刚刚成功解决了一个复杂的数据库死锁问题，使用了锁等待超时和事务重试机制。这个解决方案很有效，我想将其记录下来供以后参考。

请帮我将这个解决方案整理并记录到记忆系统中，包括问题描述、解决方法和经验教训。""",
                "expected_memory_actions": ["remember"],
                "scenario": "经验记录"
            }
        ]

    def create_enhanced_system_prompt(self) -> str:
        """创建增强的系统提示"""
        return """你是Claude Code，具有强大的记忆能力。在每次对话中，你必须主动使用记忆工具来提供更好的服务。

🧠 记忆工具使用要求：

1. 在回答问题前，请使用memory.recall()搜索相关的历史经验和知识
2. 在提供帮助后，请使用memory.remember()记录重要的信息和解决方案
3. 主动询问用户是否需要记录对话中的重要内容

请确保在每次对话中至少使用一次记忆工具，这对提供连续性和个性化服务至关重要。"""

    async def run_claude_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个Claude测试"""
        
        print(f"\n🧠 测试场景: {test_case['scenario']}")
        print(f"期望记忆操作: {', '.join(test_case['expected_memory_actions'])}")
        print("-" * 60)
        
        # 构建Claude命令
        system_prompt = self.create_enhanced_system_prompt()
        
        # 创建临时配置文件
        config = {
            "systemPrompt": system_prompt,
            "maxTurns": 3,
            "allowedTools": ["Read", "Write", "Bash", "Glob", "Grep", "Task"]
        }
        
        config_path = Path("temp_claude_config.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        try:
            # 运行Claude命令
            print("🤖 启动Claude Code交互...")
            
            cmd = [
                "claude",
                "--config", str(config_path),
                "--prompt", test_case['prompt']
            ]
            
            # 执行命令并捕获输出
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2分钟超时
                cwd=str(Path.cwd())
            )
            
            # 分析输出
            result = self.analyze_claude_output(
                process.stdout, 
                process.stderr,
                test_case
            )
            
            print(f"📊 测试结果: {result['summary']}")
            
            return result
            
        except subprocess.TimeoutExpired:
            print("⏰ Claude执行超时")
            return {
                "scenario": test_case['scenario'],
                "success": False,
                "error": "Timeout",
                "memory_actions_detected": 0,
                "summary": "执行超时"
            }
        except Exception as e:
            print(f"❌ 执行出错: {e}")
            return {
                "scenario": test_case['scenario'],
                "success": False, 
                "error": str(e),
                "memory_actions_detected": 0,
                "summary": f"执行错误: {e}"
            }
        finally:
            # 清理临时文件
            if config_path.exists():
                config_path.unlink()

    def analyze_claude_output(self, stdout: str, stderr: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """分析Claude的输出，检测记忆工具使用"""
        
        memory_actions_detected = 0
        recall_detected = False
        remember_detected = False
        
        # 分析stdout中的记忆工具使用
        if stdout:
            # 检测recall操作
            if any(keyword in stdout.lower() for keyword in 
                   ["memory.recall", "搜索记忆", "查找记忆", "recall memory", "searching memory"]):
                recall_detected = True
                memory_actions_detected += 1
            
            # 检测remember操作  
            if any(keyword in stdout.lower() for keyword in
                   ["memory.remember", "记录记忆", "存储记忆", "remember", "storing memory"]):
                remember_detected = True
                memory_actions_detected += 1
        
        # 评估成功程度
        expected_actions = test_case['expected_memory_actions']
        success_score = 0.0
        
        if "recall" in expected_actions and recall_detected:
            success_score += 0.5
        if "remember" in expected_actions and remember_detected:
            success_score += 0.5
        
        success = success_score >= 0.5  # 至少50%的期望操作被执行
        
        return {
            "scenario": test_case['scenario'],
            "success": success,
            "success_score": success_score,
            "memory_actions_detected": memory_actions_detected,
            "recall_detected": recall_detected,
            "remember_detected": remember_detected,
            "expected_actions": expected_actions,
            "claude_output_length": len(stdout),
            "has_errors": bool(stderr),
            "summary": f"检测到{memory_actions_detected}个记忆操作，成功率{success_score:.1%}"
        }

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """运行综合测试"""
        
        print("🚀 Phase 3: 真实Claude Code主动性测试")
        print("=" * 70)
        print("目标: 通过实际Claude Code交互验证记忆工具主动使用能力")
        print("=" * 70)
        
        # 检查Claude Code是否可用
        try:
            subprocess.run(["claude", "--version"], capture_output=True, check=True)
            print("✅ Claude Code CLI 可用")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Claude Code CLI 不可用，请确保已正确安装")
            return {"error": "Claude Code CLI not available"}
        
        # 运行所有测试用例
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n📋 执行测试 {i}/{len(self.test_cases)}")
            result = await self.run_claude_test(test_case)
            self.test_results.append(result)
        
        # 计算综合评分
        successful_tests = sum(1 for r in self.test_results if r.get("success", False))
        total_memory_actions = sum(r.get("memory_actions_detected", 0) for r in self.test_results)
        average_success_score = sum(r.get("success_score", 0) for r in self.test_results) / len(self.test_results)
        
        # 生成最终报告
        final_report = {
            "timestamp": datetime.now().isoformat(),
            "test_summary": {
                "total_tests": len(self.test_results),
                "successful_tests": successful_tests,
                "success_rate": successful_tests / len(self.test_results),
                "average_success_score": average_success_score,
                "total_memory_actions": total_memory_actions,
                "memory_actions_per_test": total_memory_actions / len(self.test_results)
            },
            "detailed_results": self.test_results,
            "proactivity_grade": self.calculate_proactivity_grade(average_success_score),
            "recommendations": self.generate_recommendations(average_success_score, self.test_results)
        }
        
        self.print_final_report(final_report)
        
        # 保存报告
        report_path = Path("phase3_real_claude_test_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细报告已保存到: {report_path}")
        
        return final_report

    def calculate_proactivity_grade(self, average_score: float) -> str:
        """计算主动性评级"""
        if average_score >= 0.8:
            return "A级 - 优秀主动性"
        elif average_score >= 0.6:
            return "B级 - 良好主动性"
        elif average_score >= 0.4:
            return "C级 - 基础主动性"
        else:
            return "D级 - 主动性不足"

    def generate_recommendations(self, score: float, results: List[Dict]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if score < 0.5:
            recommendations.extend([
                "需要加强系统提示中关于记忆工具使用的指导",
                "考虑在用户提示中更明确地要求使用记忆工具",
                "实现记忆工具使用的强制检查机制"
            ])
        
        # 分析具体问题
        recall_failures = sum(1 for r in results if not r.get("recall_detected", False) and "recall" in r.get("expected_actions", []))
        remember_failures = sum(1 for r in results if not r.get("remember_detected", False) and "remember" in r.get("expected_actions", []))
        
        if recall_failures > 0:
            recommendations.append("改进记忆搜索的触发机制和提示策略")
        
        if remember_failures > 0:
            recommendations.append("优化记忆存储的引导和自动化程度")
        
        if score >= 0.7:
            recommendations.append("主动性表现良好，可以专注于优化记忆内容质量")
        
        return recommendations

    def print_final_report(self, report: Dict[str, Any]):
        """打印最终报告"""
        summary = report["test_summary"]
        
        print(f"\n📊 Phase 3 真实Claude测试最终报告")
        print("=" * 60)
        
        print(f"🎯 测试结果:")
        print(f"   总测试数: {summary['total_tests']}")
        print(f"   成功测试: {summary['successful_tests']}")
        print(f"   成功率: {summary['success_rate']:.1%}")
        print(f"   平均成功评分: {summary['average_success_score']:.3f}")
        print(f"   记忆操作总数: {summary['total_memory_actions']}")
        print(f"   平均每测试记忆操作: {summary['memory_actions_per_test']:.1f}")
        print(f"   主动性评级: {report['proactivity_grade']}")
        
        print(f"\n📋 详细测试结果:")
        for i, result in enumerate(report["detailed_results"], 1):
            status = "✅ 成功" if result.get("success", False) else "❌ 失败"
            print(f"   {i}. {result['scenario']}: {status}")
            print(f"      {result['summary']}")
        
        print(f"\n💡 改进建议:")
        for rec in report["recommendations"]:
            print(f"   • {rec}")
        
        # 对整体系统影响的预测
        current_proactivity = summary['average_success_score']
        estimated_overall = (1.0 * 0.25 + 0.778 * 0.25 + 1.0 * 0.25 + current_proactivity * 0.25)
        
        print(f"\n📈 对整体系统影响预测:")
        print(f"   实测主动性评分: {current_proactivity:.3f}")
        print(f"   预计整体评分: {estimated_overall:.3f}")
        
        if estimated_overall >= 0.8:
            print(f"   🌟 已达到A级系统标准!")
        elif estimated_overall >= 0.75:
            print(f"   ⚡ 接近A级，继续优化可达到优秀水平")
        else:
            print(f"   💡 需要进一步优化主动性以提升整体等级")

async def main():
    """主函数"""
    tester = RealClaudeProactivityTester()
    
    print("🧠 准备启动Phase 3真实Claude Code主动性测试...")
    print("此测试将直接与Claude Code交互，验证记忆工具的实际使用情况")
    
    # 运行综合测试
    report = await tester.run_comprehensive_test()
    
    if "error" not in report:
        print(f"\n🎉 Phase 3 真实测试完成!")
        print(f"主要发现: {report['proactivity_grade']}")

if __name__ == "__main__":
    asyncio.run(main())