#!/usr/bin/env python3
"""
综合记忆系统测试总结和压力测试
汇总所有测试结果并进行最终评估
"""

import sys
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any

# 添加记忆系统到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "claude-memory-system"))

from claude_memory import MemoryManager

class ComprehensiveMemoryTestSummary:
    """综合记忆系统测试总结"""
    
    def __init__(self):
        self.memory = MemoryManager(project_path=Path("/root/code/claude-memory-test"))
        self.test_summary = {}
        
    async def run_stress_test(self):
        """运行记忆系统压力测试"""
        print("🔥 记忆系统压力测试")
        print("=" * 50)
        
        # 确保记忆同步
        await self.ensure_memory_sync()
        
        # 压力测试参数
        stress_tests = [
            {"name": "大量记忆存储", "operation": "bulk_store", "count": 50},
            {"name": "高频搜索查询", "operation": "bulk_search", "count": 100},
            {"name": "并发记忆操作", "operation": "concurrent_ops", "count": 20},
            {"name": "长文本记忆处理", "operation": "long_content", "count": 10}
        ]
        
        stress_results = []
        
        for test_config in stress_tests:
            print(f"\n🧪 {test_config['name']} (数量: {test_config['count']})")
            start_time = time.time()
            
            try:
                if test_config['operation'] == 'bulk_store':
                    result = await self.test_bulk_storage(test_config['count'])
                elif test_config['operation'] == 'bulk_search':
                    result = await self.test_bulk_search(test_config['count'])
                elif test_config['operation'] == 'concurrent_ops':
                    result = await self.test_concurrent_operations(test_config['count'])
                elif test_config['operation'] == 'long_content':
                    result = await self.test_long_content_handling(test_config['count'])
                
                duration = time.time() - start_time
                
                stress_results.append({
                    "test_name": test_config['name'],
                    "operation": test_config['operation'],
                    "count": test_config['count'],
                    "duration": duration,
                    "success": result.get('success', False),
                    "details": result
                })
                
                print(f"   耗时: {duration:.2f}秒")
                print(f"   结果: {'✅ 成功' if result.get('success', False) else '❌ 失败'}")
                
            except Exception as e:
                print(f"   ❌ 测试失败: {e}")
                stress_results.append({
                    "test_name": test_config['name'],
                    "error": str(e),
                    "duration": time.time() - start_time
                })
        
        return stress_results
    
    async def ensure_memory_sync(self):
        """确保记忆系统同步"""
        snapshot = self.memory.awaken("压力测试")
        all_memories = self.memory._file_store.load_all_memories()
        
        for mem in all_memories:
            if mem.id not in self.memory._vector_store._memory_cache:
                self.memory._vector_store.store_memory(mem)
        
        print(f"✅ 记忆系统同步完成，总记忆数: {len(all_memories)}")
        return len(all_memories)
    
    async def test_bulk_storage(self, count: int):
        """测试批量存储"""
        print(f"   批量存储 {count} 个记忆...")
        
        stored_ids = []
        failed_count = 0
        
        for i in range(count):
            try:
                content = f"""
压力测试记忆 #{i+1}

这是一个用于压力测试的记忆内容。包含以下信息：
- 记忆编号: {i+1}
- 创建时间: {time.time()}
- 测试类型: 批量存储压力测试
- 重要性: {5.0 + (i % 5)}

内容描述：
这个记忆包含了测试数据，用于验证记忆系统在大量数据存储时的性能表现。
我们测试系统的存储速度、检索效率以及内存使用情况。
                """
                
                memory_id = self.memory.remember(
                    content=content,
                    memory_type="working",
                    title=f"压力测试记忆-{i+1}",
                    tags=["压力测试", "批量存储", f"batch_{i//10}"],
                    importance=5.0 + (i % 5),
                    scope="project"
                )
                
                stored_ids.append(memory_id)
                
            except Exception as e:
                failed_count += 1
                print(f"     存储失败 #{i+1}: {e}")
        
        success_rate = (count - failed_count) / count
        
        return {
            "success": success_rate > 0.8,
            "stored_count": len(stored_ids),
            "failed_count": failed_count,
            "success_rate": success_rate
        }
    
    async def test_bulk_search(self, count: int):
        """测试批量搜索"""
        print(f"   执行 {count} 次搜索查询...")
        
        search_queries = [
            "Python编程", "性能优化", "数据库设计", "机器学习", "web开发",
            "算法实现", "系统架构", "容器化部署", "测试策略", "代码质量",
            "分布式系统", "微服务", "API设计", "前端开发", "后端优化",
            "安全策略", "监控告警", "日志分析", "故障处理", "用户体验"
        ]
        
        total_time = 0
        successful_searches = 0
        total_results = 0
        
        for i in range(count):
            query = search_queries[i % len(search_queries)]
            
            try:
                start_time = time.time()
                results = self.memory.recall(query, max_results=5, min_relevance=0.1)
                search_time = time.time() - start_time
                
                total_time += search_time
                total_results += len(results)
                successful_searches += 1
                
            except Exception as e:
                print(f"     搜索失败 #{i+1}: {e}")
        
        avg_search_time = total_time / successful_searches if successful_searches > 0 else 0
        avg_results_per_search = total_results / successful_searches if successful_searches > 0 else 0
        
        return {
            "success": successful_searches / count > 0.9,
            "successful_searches": successful_searches,
            "avg_search_time": avg_search_time,
            "avg_results_per_search": avg_results_per_search,
            "total_results": total_results
        }
    
    async def test_concurrent_operations(self, count: int):
        """测试并发操作"""
        print(f"   模拟 {count} 个并发操作...")
        
        async def concurrent_operation(op_id: int):
            """单个并发操作"""
            try:
                # 交替进行存储和搜索操作
                if op_id % 2 == 0:
                    # 存储操作
                    content = f"并发测试记忆 #{op_id}"
                    memory_id = self.memory.remember(
                        content=content,
                        memory_type="working",
                        title=f"并发测试-{op_id}",
                        tags=["并发测试"],
                        importance=5.0
                    )
                    return {"type": "store", "success": True, "id": memory_id}
                else:
                    # 搜索操作
                    results = self.memory.recall("测试", max_results=3)
                    return {"type": "search", "success": True, "count": len(results)}
                    
            except Exception as e:
                return {"type": "error", "success": False, "error": str(e)}
        
        # 创建并发任务
        tasks = [concurrent_operation(i) for i in range(count)]
        
        # 执行并发操作
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_ops = sum(1 for r in results if isinstance(r, dict) and r.get('success', False))
            store_ops = sum(1 for r in results if isinstance(r, dict) and r.get('type') == 'store')
            search_ops = sum(1 for r in results if isinstance(r, dict) and r.get('type') == 'search')
            
            return {
                "success": successful_ops / count > 0.8,
                "successful_operations": successful_ops,
                "store_operations": store_ops,
                "search_operations": search_ops,
                "success_rate": successful_ops / count
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_long_content_handling(self, count: int):
        """测试长文本处理"""
        print(f"   处理 {count} 个长文本记忆...")
        
        successful_ops = 0
        total_content_length = 0
        
        for i in range(count):
            try:
                # 生成长文本内容
                long_content = f"""
大型记忆测试 #{i+1}

这是一个非常长的记忆内容，用于测试记忆系统处理大型文本的能力。

{"这是重复的测试内容。" * 100}

技术栈信息：
- 编程语言: Python, JavaScript, TypeScript, Kotlin, Rust, Go
- 框架: React, Vue, Angular, Spring Boot, Django, FastAPI
- 数据库: PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch
- 工具: Docker, Kubernetes, Git, Jenkins, Nginx, Apache

详细描述：
{"在这个部分，我们详细描述了各种技术的使用场景和最佳实践。" * 50}

代码示例：
```python
def example_function():
    \"\"\"这是一个示例函数\"\"\"
    data = [i for i in range(1000)]
    return sum(data)
    
class ExampleClass:
    def __init__(self):
        self.value = 42
        
    def process_data(self, input_data):
        return [x * 2 for x in input_data]
```

{"更多的测试内容填充以增加文本长度。" * 200}
                """
                
                memory_id = self.memory.remember(
                    content=long_content,
                    memory_type="semantic",
                    title=f"长文本测试-{i+1}",
                    tags=["长文本", "压力测试"],
                    importance=6.0
                )
                
                successful_ops += 1
                total_content_length += len(long_content)
                
            except Exception as e:
                print(f"     长文本处理失败 #{i+1}: {e}")
        
        avg_content_length = total_content_length / successful_ops if successful_ops > 0 else 0
        
        return {
            "success": successful_ops / count > 0.8,
            "successful_operations": successful_ops,
            "avg_content_length": avg_content_length,
            "total_content_length": total_content_length
        }
    
    def load_previous_test_results(self):
        """加载之前的测试结果"""
        test_files = [
            "long_context_test_results.json",
            "complex_scenarios_test_results.json", 
            "proactive_memory_test_results.json"
        ]
        
        all_results = {}
        
        for file_name in test_files:
            file_path = Path(f"/root/code/claude-memory-test/{file_name}")
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_results[file_name.replace('.json', '')] = data
                except Exception as e:
                    print(f"⚠️ 无法加载 {file_name}: {e}")
        
        return all_results
    
    async def generate_final_assessment(self, stress_results: List[Dict], previous_results: Dict):
        """生成最终评估报告"""
        print("\n📊 综合记忆系统评估报告")
        print("=" * 60)
        
        # 压力测试评分
        stress_scores = []
        for result in stress_results:
            if 'success' in result:
                stress_scores.append(1.0 if result['success'] else 0.0)
        
        stress_score = sum(stress_scores) / len(stress_scores) if stress_scores else 0
        
        print(f"压力测试评分: {stress_score:.3f}")
        
        # 之前测试的评分
        long_context_score = 0
        complex_scenario_score = 0
        proactive_score = 0
        
        if 'long_context_test_results' in previous_results:
            long_context_score = previous_results['long_context_test_results'].get('overall_accuracy', 0)
        
        if 'complex_scenarios_test_results' in previous_results:
            complex_scenario_score = previous_results['complex_scenarios_test_results'].get('overall_score', 0)
        
        if 'proactive_memory_test_results' in previous_results:
            proactive_score = previous_results['proactive_memory_test_results'].get('overall_score', 0)
        
        print(f"长上下文准确性: {long_context_score:.3f}")
        print(f"复杂场景表现: {complex_scenario_score:.3f}")
        print(f"主动使用能力: {proactive_score:.3f}")
        
        # 计算综合评分
        overall_score = (
            stress_score * 0.25 +
            long_context_score * 0.25 +
            complex_scenario_score * 0.25 +
            proactive_score * 0.25
        )
        
        print(f"\n🎯 综合评分: {overall_score:.3f}/1.0")
        
        # 评级和建议
        if overall_score >= 0.8:
            rating = "优秀 (A级)"
            recommendation = "记忆系统表现优秀，可以投入生产使用"
        elif overall_score >= 0.6:
            rating = "良好 (B级)"
            recommendation = "记忆系统表现良好，建议优化后投入使用"
        elif overall_score >= 0.4:
            rating = "及格 (C级)"
            recommendation = "记忆系统基本可用，需要显著改进"
        else:
            rating = "需要改进 (D级)"
            recommendation = "记忆系统需要重大改进才能实用"
        
        print(f"系统评级: {rating}")
        print(f"使用建议: {recommendation}")
        
        # 详细分析
        print(f"\n📋 详细分析:")
        
        # 优势分析
        strengths = []
        if stress_score >= 0.7:
            strengths.append("优秀的压力测试表现")
        if long_context_score >= 0.7:
            strengths.append("良好的长上下文处理能力")
        if complex_scenario_score >= 0.7:
            strengths.append("强大的复杂场景适应性")
        if proactive_score >= 0.7:
            strengths.append("Claude主动使用记忆的能力")
        
        if strengths:
            print("✅ 系统优势:")
            for strength in strengths:
                print(f"   • {strength}")
        
        # 改进建议
        improvements = []
        if stress_score < 0.7:
            improvements.append("提升系统在高负载下的稳定性")
        if long_context_score < 0.7:
            improvements.append("改进长上下文和复杂查询的处理")
        if complex_scenario_score < 0.7:
            improvements.append("增强多步骤任务的记忆连贯性")
        if proactive_score < 0.7:
            improvements.append("优化Claude主动使用记忆的引导机制")
        
        if improvements:
            print("\n⚠️ 改进建议:")
            for improvement in improvements:
                print(f"   • {improvement}")
        
        # 技术建议
        print(f"\n🔧 技术优化建议:")
        print("   • 实现真正的语义搜索（如使用sentence-transformers）")
        print("   • 集成向量数据库（如ChromaDB）提升搜索性能")
        print("   • 优化记忆自动同步机制")
        print("   • 增强系统提示，提高Claude主动性")
        print("   • 实现记忆压缩和归档功能")
        
        return {
            "overall_score": overall_score,
            "rating": rating,
            "recommendation": recommendation,
            "individual_scores": {
                "stress_test": stress_score,
                "long_context": long_context_score,
                "complex_scenario": complex_scenario_score,
                "proactive_usage": proactive_score
            },
            "strengths": strengths,
            "improvements": improvements
        }
    
    async def run_comprehensive_test_summary(self):
        """运行综合测试总结"""
        print("🧠 Claude Code记忆系统综合测试总结")
        print("=" * 60)
        print("汇总所有测试结果，生成最终评估报告")
        print("=" * 60)
        
        # 运行压力测试
        stress_results = await self.run_stress_test()
        
        # 加载之前的测试结果
        previous_results = self.load_previous_test_results()
        
        # 生成最终评估
        final_assessment = await self.generate_final_assessment(stress_results, previous_results)
        
        # 保存完整测试报告
        complete_report = {
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "stress_test_results": stress_results,
            "previous_test_results": previous_results,
            "final_assessment": final_assessment,
            "summary": {
                "total_tests_conducted": len(stress_results) + len(previous_results),
                "overall_score": final_assessment["overall_score"],
                "rating": final_assessment["rating"],
                "ready_for_production": final_assessment["overall_score"] >= 0.7
            }
        }
        
        # 保存报告
        report_file = Path("/root/code/claude-memory-test/comprehensive_memory_test_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(complete_report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n📁 完整测试报告已保存到: {report_file}")
        
        # 将测试总结存储到记忆系统
        await self.store_test_summary_to_memory(complete_report)
        
        return complete_report
    
    async def store_test_summary_to_memory(self, report: Dict):
        """将测试总结存储到记忆系统"""
        
        summary_content = f"""
Claude Code记忆系统综合测试总结报告

测试日期: {report['test_date']}
综合评分: {report['final_assessment']['overall_score']:.3f}/1.0
系统评级: {report['final_assessment']['rating']}

各项测试评分:
- 压力测试: {report['final_assessment']['individual_scores']['stress_test']:.3f}
- 长上下文处理: {report['final_assessment']['individual_scores']['long_context']:.3f}
- 复杂场景适应: {report['final_assessment']['individual_scores']['complex_scenario']:.3f}
- 主动使用能力: {report['final_assessment']['individual_scores']['proactive_usage']:.3f}

系统优势:
{chr(10).join(f'• {s}' for s in report['final_assessment']['strengths'])}

改进建议:
{chr(10).join(f'• {i}' for i in report['final_assessment']['improvements'])}

使用建议: {report['final_assessment']['recommendation']}

结论: 记忆系统{'已准备好投入生产使用' if report['summary']['ready_for_production'] else '需要进一步优化后才能投入使用'}。
这是一个创新的AI记忆管理系统，为Claude Code提供了持久化认知能力。
        """
        
        self.memory.remember(
            content=summary_content,
            memory_type="episodic",
            title="Claude Code记忆系统综合测试总结",
            tags=["测试总结", "综合评估", "记忆系统", "性能测试", "最终报告"],
            importance=9.8,
            scope="global"
        )
        
        print("✅ 测试总结已存储到记忆系统")

async def main():
    """主函数"""
    tester = ComprehensiveMemoryTestSummary()
    
    try:
        report = await tester.run_comprehensive_test_summary()
        
        print(f"\n🎉 测试完成!")
        print(f"综合评分: {report['summary']['overall_score']:.3f}")
        print(f"是否可投产: {'是' if report['summary']['ready_for_production'] else '否'}")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())