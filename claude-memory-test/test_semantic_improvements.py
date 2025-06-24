
import sys
import asyncio
from pathlib import Path

# 添加记忆系统到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "claude-memory-system"))

from claude_memory import MemoryManager

async def test_semantic_search():
    """测试语义搜索改进"""
    print("🔍 测试语义搜索改进...")
    
    memory = MemoryManager(Path("."))
    
    # 苏醒系统
    snapshot = memory.awaken("测试语义搜索改进")
    print(f"总记忆数: {snapshot.memory_statistics.total_memories}")
    
    # 测试搜索
    test_queries = [
        "Python编程",
        "性能优化", 
        "机器学习",
        "数据库设计",
        "分布式系统"
    ]
    
    total_results = 0
    for query in test_queries:
        results = memory.recall(query, max_results=5, min_relevance=0.1)
        total_results += len(results)
        print(f"查询'{query}': 找到 {len(results)} 个结果")
        
        for i, result in enumerate(results[:2], 1):
            print(f"  {i}. {result.memory.title} (相关性: {result.relevance_score:.3f})")
    
    print(f"\n📊 搜索测试总结:")
    print(f"总查询数: {len(test_queries)}")
    print(f"总结果数: {total_results}")
    print(f"平均结果数: {total_results/len(test_queries):.1f}")
    
    if total_results > 0:
        print("✅ 语义搜索改进成功！搜索功能已恢复")
        return True
    else:
        print("❌ 搜索功能仍有问题")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_semantic_search())
    exit(0 if success else 1)
