#!/usr/bin/env python3
"""
主动性测试脚本
用于验证Claude Code是否主动使用记忆工具
"""

import sys
from pathlib import Path

# 添加记忆系统路径
sys.path.insert(0, str(Path(__file__).parent / "claude-memory-system"))

def test_memory_functionality():
    """测试记忆系统基础功能"""
    print("🧠 测试记忆系统基础功能...")
    
    try:
        from claude_memory import MemoryManager
        
        memory = MemoryManager(Path("."))
        snapshot = memory.awaken("主动性测试")
        
        print(f"✅ 记忆系统正常，共 {snapshot.memory_statistics.total_memories} 个记忆")
        
        # 测试搜索
        results = memory.recall("测试", max_results=3, min_relevance=0.1)
        print(f"✅ 搜索功能正常，找到 {len(results)} 个结果")
        
        # 测试存储
        memory_id = memory.remember(
            content="主动性测试记忆内容",
            memory_type="working",
            title="主动性测试",
            importance=5.0
        )
        print(f"✅ 存储功能正常，记忆ID: {memory_id[:8]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 记忆系统测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 主动性增强验证测试")
    print("=" * 40)
    
    # 检查配置文件
    claude_md = Path("CLAUDE.md")
    if claude_md.exists():
        print("✅ CLAUDE.md 配置文件存在")
    else:
        print("❌ CLAUDE.md 配置文件缺失")
    
    triggers_json = Path("memory_triggers.json") 
    if triggers_json.exists():
        print("✅ 记忆触发器配置存在")
    else:
        print("❌ 记忆触发器配置缺失")
    
    # 测试记忆系统
    memory_ok = test_memory_functionality()
    
    print(f"\n📊 测试结果:")
    if memory_ok:
        print("✅ 记忆系统已准备就绪，可以进行主动性测试")
        print("💡 建议: 使用 'claude' 命令启动并测试记忆工具的主动使用")
    else:
        print("❌ 记忆系统存在问题，需要修复后再进行主动性测试")

if __name__ == "__main__":
    main()
