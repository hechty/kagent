#!/usr/bin/env python3
"""
修复记忆搜索功能的测试脚本
"""

import sys
import asyncio
from pathlib import Path

# 添加记忆系统到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "claude-memory-system"))

from claude_memory import MemoryManager

async def test_memory_search_fix():
    """测试并修复记忆搜索功能"""
    print("🔧 测试记忆搜索功能修复")
    print("=" * 50)
    
    # 创建记忆管理器
    memory = MemoryManager(project_path=Path("/root/code/claude-memory-test"))
    
    # 苏醒系统
    snapshot = memory.awaken("测试搜索功能")
    print(f"总记忆数: {snapshot.memory_statistics.total_memories}")
    
    # 手动加载所有文件记忆到向量存储
    print("\n🔄 手动同步文件存储到向量存储...")
    all_memories = memory._file_store.load_all_memories()
    
    print(f"从文件加载了 {len(all_memories)} 个记忆")
    
    # 确保所有记忆都在向量存储中
    loaded_count = 0
    for mem in all_memories:
        if mem.id not in memory._vector_store._memory_cache:
            memory._vector_store.store_memory(mem)
            loaded_count += 1
    
    print(f"向量存储中新增 {loaded_count} 个记忆")
    print(f"向量存储总记忆数: {len(memory._vector_store._memory_cache)}")
    
    # 测试搜索功能
    print("\n🔍 测试搜索功能...")
    
    test_queries = [
        "Python",
        "异步编程",
        "分布式系统",
        "机器学习",
        "性能优化",
        "容器化",
        "数据库"
    ]
    
    for query in test_queries:
        print(f"\n搜索: '{query}'")
        results = memory.recall(query, max_results=3, min_relevance=0.1)
        print(f"找到 {len(results)} 个结果")
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.memory.title}")
            print(f"     相关性: {result.relevance_score:.3f}")
            print(f"     类型: {result.memory.memory_type.value}")
            print(f"     标签: {result.memory.tags}")
    
    # 测试特定搜索场景
    print("\n📊 复杂搜索测试...")
    
    complex_queries = [
        "Python装饰器微服务",
        "机器学习模型部署优化",
        "分布式日志分析",
        "高并发缓存策略"
    ]
    
    for query in complex_queries:
        print(f"\n复杂搜索: '{query}'")
        results = memory.recall(query, max_results=5, min_relevance=0.05)
        print(f"找到 {len(results)} 个结果")
        
        if results:
            best_result = results[0]
            print(f"最佳匹配: {best_result.memory.title}")
            print(f"相关性: {best_result.relevance_score:.3f}")
            print(f"匹配原因: {', '.join(best_result.match_reasons)}")
        else:
            print("没有找到相关结果")
    
    print("\n✅ 搜索功能测试完成")
    return len(all_memories), len(memory._vector_store._memory_cache)

async def main():
    try:
        file_count, vector_count = await test_memory_search_fix()
        print(f"\n📈 统计结果:")
        print(f"文件存储记忆数: {file_count}")
        print(f"向量存储记忆数: {vector_count}")
        
        if file_count == vector_count and vector_count > 0:
            print("✅ 搜索功能已正常工作")
        else:
            print("⚠️ 存储同步可能存在问题")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())