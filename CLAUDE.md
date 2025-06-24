# 🧠 Claude Code 记忆系统 - MCP 工具模式

**新模式**: 你现在拥有MCP记忆工具，比全局命令更加强大和直观！

## 🚀 使用MCP记忆工具

记忆系统已集成为MCP工具，提供原生工具级体验！

### 🔍 搜索记忆（MCP工具）
直接调用 `memory_recall` 工具：

**基础搜索**:
```
memory_recall(query="Python性能优化")
```

**高级搜索**:
```
memory_recall(
    query="架构设计",
    max_results=5,
    min_relevance=0.2
)
```

### 💾 记录记忆（MCP工具）  
直接调用 `memory_remember` 工具：

**基础记录**:
```
memory_remember(
    title="新功能实现",
    content="详细的实现过程和关键点"
)
```

**完整记录**:
```
memory_remember(
    title="微服务架构设计",
    content="采用API网关+服务发现的架构模式",
    memory_type="semantic",
    importance=9.0,
    tags=["架构", "微服务", "设计"]
)
```

### 📊 查看状态（MCP工具）
```
memory_status()
```

## ⚡ 强制执行规则（MCP模式）

1. **每次对话开始**: 必须先用 `memory_recall` 搜索相关记忆
2. **提供建议时**: 基于记忆搜索结果回答
3. **对话结束前**: 必须用 `memory_remember` 记录重要信息
4. **使用MCP工具**: 直接调用工具函数，无需bash命令

### 🎯 标准使用流程（MCP模式）

**用户问题**: "Python性能优化有什么建议？"

**第1步 - 搜索记忆**:
```
memory_recall(query="Python性能优化", max_results=3)
```

**第2步 - 基于结果回答用户**

**第3步 - 记录新知识**:
```
memory_remember(
    title="Python性能优化建议",
    content="详细的优化建议内容",
    memory_type="semantic", 
    importance=8.0,
    tags=["Python", "性能", "优化"]
)
```

## 🎯 MCP工具参数说明

### memory_recall 参数:
- `query` (必需): 搜索关键词
- `max_results` (可选): 最大结果数，默认3
- `min_relevance` (可选): 最小相关性，默认0.1

### memory_remember 参数:
- `title` (必需): 记忆标题
- `content` (必需): 记忆内容
- `memory_type` (可选): semantic|episodic|procedural|working，默认semantic
- `importance` (可选): 重要性1-10，默认5.0
- `tags` (可选): 标签列表，默认[]

## 🎯 主动性评分标准

- **A级 (优秀)**: 每次对话使用2+次MCP记忆工具，主动建议记录
- **B级 (良好)**: 每次对话使用1-2次MCP记忆工具
- **C级 (基础)**: 偶尔使用MCP记忆工具
- **D级 (不足)**: 很少或不使用MCP记忆工具

**当前目标**: 达到A级主动性！

## 🚨 重要提醒

- **MCP原生体验**: 记忆工具现在是真正的Claude Code原生工具
- **直接调用**: 无需bash命令，直接调用工具函数
- **强大功能**: 完整的参数支持和错误处理
- **必须使用**: memory_recall 和 memory_remember 工具
- **每次对话**: 至少使用1次搜索 + 1次记录
