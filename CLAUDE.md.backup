# 🧠 Claude Code 记忆系统使用指令

**核心要求**: 你必须使用简洁的记忆工具命令，不要使用Task工具间接搜索。

## 🚀 使用全局记忆命令

记忆工具已设置为全局命令，像Bash、Read、Write一样简洁易用！

### 🔍 搜索记忆（强制使用）
```bash
memory-recall "搜索关键词"
```

**扩展用法**:
```bash
memory-recall "搜索关键词" [最大结果数] [最小相关性]
memory-recall "Python性能优化" 3 0.1
```

### 💾 记录记忆（强制使用）
```bash
memory-remember "标题" "内容"
```

**扩展用法**:
```bash
memory-remember "标题" "内容" [类型] [重要性] [标签...]
memory-remember "Python优化技巧" "使用缓存提升性能" semantic 8.0 Python 性能 优化
```

### 📊 查看状态
```bash
memory-status
```

## ⚡ 强制执行规则

1. **每次对话开始**: 必须先用 `memory-recall` 搜索相关记忆
2. **提供建议时**: 基于记忆搜索结果回答
3. **对话结束前**: 必须用 `memory-remember` 记录重要信息
4. **禁止使用Task工具**: 直接使用记忆命令

### 🎯 标准使用流程

**用户问题**: "Python性能优化有什么建议？"

**第1步 - 搜索记忆**:
```bash
memory-recall "Python性能优化"
```

**第2步 - 基于结果回答用户**

**第3步 - 记录新知识**:
```bash
memory-remember "Python性能优化建议" "详细的优化建议内容" semantic 8.0 Python 性能
```

## 🎯 主动性评分标准

- **A级 (优秀)**: 每次对话使用2+次记忆工具，主动建议记录
- **B级 (良好)**: 每次对话使用1-2次记忆工具  
- **C级 (基础)**: 偶尔使用记忆工具
- **D级 (不足)**: 很少或不使用记忆工具

**当前目标**: 达到A级主动性！

## 🚨 重要提醒

- **简洁如原生工具**: 记忆命令现在和Bash、Read、Write一样简洁
- **绝对禁止**: 使用Task工具或复杂脚本
- **必须使用**: memory-recall 和 memory-remember 命令  
- **每次对话**: 至少使用1次搜索 + 1次记录
