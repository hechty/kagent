# 🧠 Claude Code 记忆系统使用指令

**核心要求**: 你必须直接使用bash命令调用记忆工具，不要使用Task工具间接搜索。

## 🚀 强制使用bash命令

### 📍 当前记忆系统位置
```bash
/root/code/claude-memory-system/
```

### 🔍 搜索记忆（必须使用bash命令）
```bash
cd /root/code/claude-memory-system && source .venv/bin/activate && python3 -c "
from claude_memory import MemoryManager
from pathlib import Path
memory = MemoryManager(Path('..'))
results = memory.recall('用户问题关键词', max_results=3)
for r in results: print(f'记忆: {r.title} - {r.content[:100]}')
"
```

### 💾 记录记忆（必须使用bash命令）
```bash
cd /root/code/claude-memory-system && source .venv/bin/activate && python3 -c "
from claude_memory import MemoryManager
from pathlib import Path
memory = MemoryManager(Path('..'))
memory.remember(
    content='详细内容',
    title='简洁标题',
    memory_type='semantic',
    importance=7.0
)
print('✅ 记忆已保存')
"
```

## ⚡ 强制执行规则

1. **每次对话开始**: 必须先用bash命令搜索相关记忆
2. **提供建议时**: 基于记忆搜索结果
3. **对话结束前**: 必须用bash命令记录重要信息
4. **禁止使用Task工具**: 直接使用bash命令调用记忆系统

### 🎯 命令执行示例

**用户问题**: "Python性能优化"
**必须执行**:
```bash
cd /root/code/claude-memory-system && source .venv/bin/activate && python3 -c "
from claude_memory import MemoryManager
from pathlib import Path  
memory = MemoryManager(Path('..'))
results = memory.recall('Python性能优化', max_results=3)
for r in results: print(f'{r.title}: {r.content[:50]}...')
"
```

**回答完成后必须执行**:
```bash
cd /root/code/claude-memory-system && source .venv/bin/activate && python3 -c "
from claude_memory import MemoryManager
from pathlib import Path
memory = MemoryManager(Path('..'))
memory.remember(
    content='Python性能优化技巧：使用缓存、避免重复计算、选择合适数据结构',
    title='Python性能优化建议',
    memory_type='semantic',
    importance=8.0
)
print('✅ 已记录Python性能优化建议')
"
```

## 🚨 重要提醒

- **绝对禁止**: 使用Task工具搜索记忆
- **必须使用**: 上述bash命令直接调用记忆系统
- **每次对话**: 至少执行1次搜索 + 1次记录
- **命令路径**: 确保在 `/root/code/claude-memory-system/` 目录下执行
