
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "claude-memory-system"))

try:
    from claude_memory import MemoryManager
    
    async def test():
        memory = MemoryManager(Path("."))
        snapshot = memory.awaken("测试语义搜索")
        print(f"记忆总数: {snapshot.memory_statistics.total_memories}")
        
        # 测试基础搜索
        results = memory.recall("Python", max_results=3, min_relevance=0.1)
        print(f"搜索Python: {len(results)} 个结果")
        
        for result in results:
            print(f"  - {result.memory.title} (相关性: {result.relevance_score:.3f})")
        
        return len(results) > 0
    
    success = asyncio.run(test())
    print("✅ 搜索功能正常" if success else "❌ 搜索功能异常")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
