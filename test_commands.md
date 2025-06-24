# 🧪 Claude Code 记忆工具测试指南

## 方法1: 命令行测试（推荐）

### 1. 启动Claude Code
```bash
cd /root/code
claude
```

### 2. 测试场景

#### 场景1: 问题解决
输入：
```
我在Python开发中遇到性能瓶颈，请帮助分析和优化。
```

**期望行为**：
- Claude主动搜索相关记忆
- 提供基于历史经验的建议
- 询问是否记录解决方案

#### 场景2: 技术学习
输入：
```
请教我微服务架构的最佳实践。
```

**期望行为**：
- 搜索架构相关记忆
- 基于历史知识提供指导
- 记录重要概念

#### 场景3: 项目开发
输入：
```
我需要设计一个用户认证系统，有什么建议？
```

**期望行为**：
- 搜索认证系统经验
- 提供设计模式建议
- 记录设计决策

### 3. 评估标准

**A级表现**：
- 每次对话使用2+次记忆工具
- 主动搜索相关记忆
- 主动建议记录重要信息
- 明确提到记忆工具使用

**B级表现**：
- 每次对话使用1-2次记忆工具
- 有记忆工具使用意识

**C级表现**：
- 偶尔使用记忆工具
- 需要提醒才使用

**D级表现**：
- 很少或不使用记忆工具

## 方法2: SDK测试（高级）

### 1. 运行SDK测试脚本
```bash
source claude-memory-system/.venv/bin/activate
python3 test_memory_integration.py
```

### 2. 选择测试模式
- 选择1：完整测试（推荐）
- 选择2：快速测试

## 方法3: 手动验证

### 1. 检查CLAUDE.md配置
```bash
cat CLAUDE.md
```

### 2. 检查记忆系统状态
```bash
source claude-memory-system/.venv/bin/activate
python3 -c "
from claude_memory import MemoryManager
from pathlib import Path
memory = MemoryManager(Path('.'))
snapshot = memory.awaken('测试')
print(f'记忆总数: {snapshot.memory_statistics.total_memories}')
"
```

### 3. 测试记忆搜索
```bash
source claude-memory-system/.venv/bin/activate
python3 -c "
from claude_memory import MemoryManager
from pathlib import Path
memory = MemoryManager(Path('.'))
results = memory.recall('测试', max_results=3)
print(f'搜索结果: {len(results)} 个')
"
```

## 🎯 测试重点

1. **主动性** - Claude是否主动使用记忆工具
2. **准确性** - 搜索结果是否相关
3. **完整性** - 是否包含搜索+记录的完整流程
4. **用户体验** - 是否提升了对话质量

## 📊 记录测试结果

对于每个测试场景，记录：
- [ ] Claude是否主动搜索记忆
- [ ] Claude是否基于记忆提供建议
- [ ] Claude是否主动记录重要信息
- [ ] Claude是否明确说明记忆工具使用
- [ ] 整体对话质量是否提升

## 🔧 故障排除

### 如果Claude不使用记忆工具：
1. 检查CLAUDE.md文件是否存在
2. 确认记忆系统正常工作
3. 尝试更强制的系统提示语言

### 如果记忆搜索无结果：
1. 检查记忆数据是否存在
2. 尝试不同的搜索关键词
3. 检查记忆系统同步状态

### 如果SDK测试失败：
1. 确认Claude Code已正确安装
2. 检查Python环境和依赖
3. 尝试简化测试场景