# 🧠 Claude Code 记忆系统 - 全局命令模式

**命令模式**: 你现在使用全局bash命令访问记忆系统，简单直接！

## 🚀 使用全局记忆命令

记忆系统通过全局bash命令提供服务！

### 🔍 搜索记忆（全局命令）
使用 `memory-recall` 命令：

**基础搜索**:
```bash
memory-recall "Python性能优化"
```

**高级搜索**:
```bash
memory-recall "架构设计" --max-results 5 --min-relevance 0.2
```

### 💾 记录记忆（全局命令）  
使用 `memory-remember` 命令：

**基础记录**:
```bash
memory-remember "新功能实现" "详细的实现过程和关键点"
```

**完整记录**:
```bash
memory-remember "微服务架构设计" "采用API网关+服务发现的架构模式" --type semantic --importance 9.0 --tags "架构,微服务,设计"
```

### 📊 查看状态（全局命令）
```bash
memory-status
```

## ⚡ 强制执行规则（命令模式）

1. **每次对话开始**: 必须先用 `memory-recall` 搜索相关记忆
2. **提供建议时**: 基于记忆搜索结果回答
3. **对话结束前**: 必须用 `memory-remember` 记录重要信息
4. **使用bash命令**: 通过Bash工具调用全局命令

### 🎯 标准使用流程（命令模式）

**用户问题**: "Python性能优化有什么建议？"

**第1步 - 搜索记忆**:
```bash
memory-recall "Python性能优化" --max-results 3
```

**第2步 - 基于结果回答用户**

**第3步 - 记录新知识**:
```bash
memory-remember "Python性能优化建议" "详细的优化建议内容" --type semantic --importance 8.0 --tags "Python,性能,优化"
```

## 🎯 全局命令参数说明

### memory-recall 参数:
- 第1个参数: 搜索关键词（必需）
- `--max-results`: 最大结果数，默认3
- `--min-relevance`: 最小相关性，默认0.1

### memory-remember 参数:
- 第1个参数: 记忆标题（必需）
- 第2个参数: 记忆内容（必需）
- `--type`: 记忆类型 semantic|episodic|procedural|working，默认semantic
- `--importance`: 重要性1-10，默认5.0
- `--tags`: 标签列表，用逗号分隔

## 🎯 主动性评分标准

- **A级 (优秀)**: 每次对话使用2+次记忆命令，主动建议记录
- **B级 (良好)**: 每次对话使用1-2次记忆命令
- **C级 (基础)**: 偶尔使用记忆命令
- **D级 (不足)**: 很少或不使用记忆命令

**当前目标**: 达到A级主动性！

## 🚨 重要提醒

- **全局命令**: 记忆系统通过全局bash命令提供服务
- **Bash调用**: 使用Bash工具执行记忆命令
- **简单直接**: 命令行界面，参数清晰
- **必须使用**: memory-recall 和 memory-remember 命令
- **每次对话**: 至少使用1次搜索 + 1次记录
