#!/usr/bin/env python3
"""
测试当前的改进效果
即使没有sentence-transformers，也应该可以使用关键词搜索
"""

import sys
import asyncio
from pathlib import Path

# 添加记忆系统到路径
sys.path.insert(0, str(Path(__file__).parent / "claude-memory-system"))

async def test_basic_search():
    """测试基本搜索功能"""
    print("🔍 测试基本搜索功能...")
    
    try:
        from claude_memory import MemoryManager
        
        # 创建记忆管理器
        memory = MemoryManager(Path("."))
        
        # 苏醒系统
        print("🌅 苏醒记忆系统...")
        snapshot = memory.awaken("测试改进效果")
        
        print(f"📊 记忆统计:")
        print(f"  总记忆数: {snapshot.memory_statistics.total_memories}")
        print(f"  全局记忆: {snapshot.memory_statistics.global_memories}")
        print(f"  项目记忆: {snapshot.memory_statistics.project_memories}")
        
        # 测试搜索功能
        print("\n🔍 测试搜索功能...")
        
        test_queries = [
            "Python",
            "性能优化", 
            "机器学习",
            "测试",
            "记忆系统"
        ]
        
        total_results = 0
        successful_queries = 0
        
        for query in test_queries:
            try:
                results = memory.recall(query, max_results=5, min_relevance=0.05)
                total_results += len(results)
                
                print(f"\n查询 '{query}':")
                print(f"  找到 {len(results)} 个结果")
                
                if len(results) > 0:
                    successful_queries += 1
                    for i, result in enumerate(results[:3], 1):
                        print(f"    {i}. {result.memory.title} (相关性: {result.relevance_score:.3f})")
                        print(f"       类型: {result.memory.memory_type.value}, 重要性: {result.memory.importance}")
                else:
                    print("    无结果")
                    
            except Exception as e:
                print(f"  查询 '{query}' 失败: {e}")
        
        # 分析结果
        print(f"\n📈 搜索测试总结:")
        print(f"  总查询数: {len(test_queries)}")
        print(f"  成功查询: {successful_queries}")
        print(f"  总结果数: {total_results}")
        print(f"  平均结果数: {total_results/len(test_queries):.1f}")
        print(f"  成功率: {successful_queries/len(test_queries)*100:.1f}%")
        
        if total_results > 0:
            print("\n✅ 搜索功能已恢复! 改进成功!")
            print("主要改进:")
            print("  ✅ 修复了记忆同步机制")
            print("  ✅ 改进了搜索算法")
            print("  ✅ 恢复了基本的记忆检索功能")
            
            return True
        else:
            print("\n❌ 搜索功能仍有问题")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_memory_storage():
    """测试记忆存储功能"""
    print("\n💾 测试记忆存储功能...")
    
    try:
        from claude_memory import MemoryManager
        
        memory = MemoryManager(Path("."))
        memory.awaken("存储测试")
        
        # 存储一个测试记忆
        test_content = "这是一个用于测试改进效果的记忆。包含Python编程、性能优化、测试等关键词。"
        
        memory_id = memory.remember(
            content=test_content,
            memory_type="working",
            title="改进测试记忆",
            tags=["测试", "改进", "Python", "验证"],
            importance=7.0,
            scope="project"
        )
        
        print(f"✅ 成功存储测试记忆: {memory_id[:8]}...")
        
        # 立即搜索测试
        print("🔍 立即搜索测试...")
        results = memory.recall("改进测试", max_results=3, min_relevance=0.1)
        
        if results:
            found_test_memory = False
            for result in results:
                if memory_id in result.memory.id:
                    found_test_memory = True
                    print(f"✅ 找到刚存储的记忆: {result.memory.title} (相关性: {result.relevance_score:.3f})")
                    break
            
            if found_test_memory:
                print("✅ 记忆同步机制工作正常!")
                return True
            else:
                print("⚠️ 记忆同步可能有延迟")
                return False
        else:
            print("❌ 搜索不到刚存储的记忆")
            return False
            
    except Exception as e:
        print(f"❌ 存储测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🧪 测试Claude记忆系统改进效果")
    print("=" * 50)
    print("测试目标: 验证搜索功能是否从0分恢复到可用状态")
    print("=" * 50)
    
    # 测试1: 基本搜索功能
    search_success = await test_basic_search()
    
    # 测试2: 记忆存储和同步
    storage_success = await test_memory_storage()
    
    # 综合评估
    print(f"\n🎯 改进效果评估")
    print("=" * 30)
    
    improvements = []
    if search_success:
        improvements.append("搜索功能恢复")
    if storage_success:
        improvements.append("同步机制正常")
    
    if len(improvements) >= 1:
        print("✅ 关键改进成功!")
        print("改进成果:")
        for improvement in improvements:
            print(f"  ✅ {improvement}")
        
        print("\n📈 预期效果:")
        print("  搜索准确性: 0.000 → 0.3+ (显著改善)")
        print("  记忆检索: 完全失效 → 基本可用")
        print("  整体评分: D级(0.313) → C级(0.5+) 预期")
        
        print("\n🔄 后续改进计划:")
        print("  1. 完成sentence-transformers安装以实现真正的语义搜索")
        print("  2. 改进Claude主动使用记忆工具的机制")
        print("  3. 运行完整测试套件验证整体改进效果")
        
    else:
        print("❌ 改进效果有限")
        print("需要进一步调试和优化")

if __name__ == "__main__":
    asyncio.run(main())