#!/usr/bin/env python3
"""
修复memory_manager.py的语法错误
"""

from pathlib import Path
import shutil

def fix_memory_manager():
    """修复memory_manager.py的语法错误"""
    print("🔧 修复memory_manager.py语法错误...")
    
    manager_path = Path("claude-memory-system/claude_memory/core/memory_manager.py")
    backup_path = Path("claude-memory-system/claude_memory/core/memory_manager.py.backup")
    
    if backup_path.exists():
        print("📦 从备份文件恢复...")
        shutil.copy2(backup_path, manager_path)
        print("✅ 已从备份恢复")
    else:
        print("❌ 备份文件不存在")
        return False
    
    # 读取原始内容
    with open(manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到awaken方法并正确替换
    import re
    
    # 查找awaken方法的完整定义
    awaken_pattern = r'(    def awaken\(self.*?)(\n            # Update statistics)'
    
    improved_awaken = '''    def awaken(self, context: Optional[str] = None) -> MemorySnapshot:
        """
        🌅 Awaken - Activate core memories and establish context
        
        This is the first method to call in any session. It:
        1. Loads essential project and global memories
        2. Analyzes current context and environment
        3. Prepares frequently-used capabilities
        4. Ensures all memories are loaded into vector store for search
        5. Returns a comprehensive snapshot of the memory state
        
        Args:
            context: Optional context description for this session
            
        Returns:
            MemorySnapshot: Complete overview of activated memories
        """
        logger.info(f"Awakening memory system with context: {context}")
        start_time = datetime.now()
        
        try:
            # Set session context
            if context:
                self._session_context = context
            
            # Load all memories from file storage
            all_memories = self._file_store.load_all_memories()
            logger.info(f"Loaded {len(all_memories)} memories from file storage")
            
            # CRITICAL: Ensure all memories are in vector store for search
            synced_count = 0
            for memory in all_memories:
                if memory.id not in self._vector_store._memory_cache:
                    self._vector_store.store_memory(memory)
                    synced_count += 1
            
            if synced_count > 0:
                logger.info(f"Synced {synced_count} memories to vector store")
            
            # Detect project context
            project_overview = self._detect_project_context()
            
            # Load core memories
            recent_memories = self._load_recent_memories(limit=10)
            important_memories = self._load_important_memories(limit=10)
            
            # Load active capabilities
            active_capabilities = self._load_active_capabilities()
            
            # Generate intelligent suggestions
            suggestions = self._generate_smart_suggestions(context)
            
            # Generate important reminders
            reminders = self._generate_important_reminders()
            
            # Get current context summary
            context_summary = self._get_session_context_summary(context)
            
            # Collect memory statistics
            stats = self._collect_memory_statistics()'''
    
    # 搜索并替换awaken方法的开始部分
    if 'def awaken(self, context: Optional[str] = None) -> MemorySnapshot:' in content:
        # 找到现有awaken方法的完整范围
        lines = content.split('\n')
        awaken_start = -1
        awaken_end = -1
        
        for i, line in enumerate(lines):
            if 'def awaken(self, context: Optional[str] = None) -> MemorySnapshot:' in line:
                awaken_start = i
            elif awaken_start >= 0 and line.strip().startswith('def ') and not line.strip().startswith('def awaken'):
                awaken_end = i
                break
        
        if awaken_start >= 0:
            if awaken_end == -1:
                # 如果没找到下一个方法，查找类结束或文件结束
                for i in range(awaken_start + 1, len(lines)):
                    if lines[i].strip() and not lines[i].startswith('    ') and not lines[i].startswith('\t'):
                        awaken_end = i
                        break
                
                if awaken_end == -1:
                    awaken_end = len(lines)
            
            # 替换awaken方法
            new_lines = lines[:awaken_start] + improved_awaken.split('\n') + lines[awaken_end:]
            new_content = '\n'.join(new_lines)
            
            with open(manager_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ 已修复awaken方法")
            return True
        else:
            print("❌ 无法找到awaken方法")
            return False
    else:
        print("❌ 文件结构不符合预期")
        return False

def test_fix():
    """测试修复效果"""
    print("🧪 测试语法修复...")
    
    try:
        import subprocess
        result = subprocess.run([
            "python3", "-m", "py_compile", "claude-memory-system/claude_memory/core/memory_manager.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 语法检查通过")
            return True
        else:
            print(f"❌ 语法检查失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 修复记忆管理器语法错误")
    print("=" * 40)
    
    success = fix_memory_manager()
    if success:
        test_success = test_fix()
        if test_success:
            print("\n✅ 语法错误修复成功!")
            print("现在可以测试语义搜索改进了")
        else:
            print("\n⚠️ 修复可能不完整，需要进一步检查")
    else:
        print("\n❌ 修复失败")

if __name__ == "__main__":
    main()