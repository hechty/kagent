# 简洁LLM DSL设计文档

**文档用途**: 记录简洁而富有表达力的LLM DSL设计理念、核心API和使用模式  
**设计理念**: 简洁优于复杂，渐进式复杂度，符合直觉，充分利用Kotlin特性

## 设计原则

### 1. 简洁优于复杂
- 最常用的场景应该最简单
- 避免不必要的嵌套和配置
- 一行代码解决简单问题

### 2. 渐进式复杂度  
- 从简单到复杂自然过渡
- 高级功能可选，不影响基础使用
- 学习曲线平滑

### 3. 符合直觉
- API命名接近自然语言
- 代码即文档
- 使用模式符合开发者期望

### 4. Kotlin风味
- 充分利用中缀函数、扩展函数
- 类型安全的DSL构建器
- 协程友好的异步API

## 核心API设计

### 层次1: 最简单使用 (一行代码)

```kotlin
// 最基础用法 - 80%的场景
val answer = ask("你好") using openai("api-key")
val answer = ask("复杂问题") using deepseek("key", "deepseek-chat")

// 流式响应
ask("写长文章") using openai("key") stream { chunk -> print(chunk) }
```

**设计要点:**
- 使用中缀函数 `using` 提高可读性
- Provider创建统一简洁
- 支持流式响应但不强制

### 层次2: 基础配置

```kotlin
// 带配置的Provider
val llm = openai("key", "gpt-4") {
    temperature = 0.7
    maxTokens = 1000
    timeout = 30.seconds
}

val answer = ask("问题") using llm
```

**设计要点:**
- 配置块可选，有合理默认值
- 链式配置，类型安全
- 统一的配置模型

### 层次3: 对话管理

```kotlin
val chat = chat(openai("key")) {
    system("你是专家")
    user("问题1")  // 自动获取回复
    user("问题2")  // 基于上下文回复
}

// 继续对话
val answer = chat.ask("追问")
```

**设计要点:**
- 自动管理对话上下文
- 支持系统消息设定角色
- 可以查看完整对话历史

### 层次4: 多模型和批量处理

```kotlin
// 多模型对比
val comparison = compare("问题") {
    gpt4 = openai("key")
    claude = anthropic("key") 
    deepseek = deepseek("key")
}

// 批量处理
val answers = listOf("问题1", "问题2", "问题3").askAll(openai("key"))
```

**设计要点:**
- 语义化的多模型对比
- 内置并发控制的批量处理
- 结果类型安全

### 层次5: 模板和Agent

```kotlin
// 模板和示例学习
val formatter = template("转换为JSON格式") {
    "张三,25" to """{"name":"张三","age":25}"""
    "李四,30" to """{"name":"李四","age":30}"""  
}

// 简单Agent
val coder = agent("程序员") {
    llm = openai("key")
    role = "Kotlin专家"
}
```

**设计要点:**
- 模板支持少数示例学习
- Agent概念简化，专注角色定义
- 可扩展的工具系统

### 层次6: 错误处理和可靠性

```kotlin
// 回退策略
val resilient = openai("key")
    .withFallback(deepseek("key"), anthropic("key"))
    .withRetry(3)

val answer = ask("重要问题") using resilient
```

**设计要点:**
- 链式的可靠性配置
- 自动回退和重试
- 优雅的错误处理

## 吸收的框架优点

### LangChain
- ✅ **简单的链式调用**: `chain.run(input)` → `ask(question) using provider`
- ✅ **模块化设计**: Prompt + LLM + Parser → template + provider + response
- ✅ **内置常用模式**: ConversationChain → chat() function

### AutoGen  
- ✅ **Agent对话模式**: 简单的多Agent交互 → agent() builder
- ✅ **角色定义清晰**: 每个Agent有明确角色 → role property

### LlamaIndex
- ✅ **简洁查询**: `index.query(question)` → `ask(question) using provider`
- ✅ **开箱即用**: 内置常用功能 → 合理的默认配置

## 避免的复杂性

### ❌ 过度抽象
- 不创建不必要的抽象层
- 避免过深的继承层次
- 直接映射用户意图到API

### ❌ 配置膨胀
- 不暴露太多配置选项
- 提供智能默认值
- 按需暴露高级配置

### ❌ 概念过载
- 不引入太多概念
- 保持API表面积小
- 渐进式学习路径

## 扩展点设计

### 1. 新Provider
```kotlin
// 只需实现LLMProvider接口
fun customProvider(config: String): LLMProvider = CustomProviderImpl(config)

// 立即可用
val answer = ask("问题") using customProvider("config")
```

### 2. 新工具
```kotlin
// 实现Tool接口
class WeatherTool : Tool {
    override val name = "weather"
    override suspend fun execute(input: String) = getWeather(input)
}

// 添加到Agent
val agent = agent("助手") {
    tool(WeatherTool())
}
```

### 3. 自定义模板
```kotlin
// 创建领域特定的模板
fun sqlTemplate() = template("生成SQL查询") { /* examples */ }
fun codeTemplate() = template("生成代码") { /* examples */ }
```

## 实现策略

### 1. 核心接口最小化
```kotlin
interface LLMProvider {
    val name: String
    val supportedModels: List<String>
    suspend fun chat(request: ChatRequest): ChatResponse
}
```

### 2. DSL构建器模式
```kotlin
class ChatBuilder {
    // 类型安全的构建器
    // 延迟执行，组装完整后再调用
}
```

### 3. 扩展函数丰富API
```kotlin
// 为现有类型添加便利方法
suspend fun String.using(provider: LLMProvider): String
fun List<String>.askAll(provider: LLMProvider): List<String>
```

### 4. 协程优先
```kotlin
// 所有异步操作都基于协程
// 支持结构化并发
// 自动错误传播
```

## 使用场景映射

| 场景 | API | 复杂度 |
|------|-----|--------|
| 简单问答 | `ask() using provider` | ⭐ |
| 多轮对话 | `chat(provider) { user() }` | ⭐⭐ |
| 模型对比 | `compare() { gpt4 = ...; claude = ... }` | ⭐⭐ |
| 批量处理 | `questions.askAll(provider)` | ⭐⭐ |
| 模板应用 | `template().apply(input, provider)` | ⭐⭐⭐ |
| Agent系统 | `agent() { llm = ...; role = ... }` | ⭐⭐⭐ |
| 团队协作 | 组合多个Agent | ⭐⭐⭐⭐ |

## 质量保证

### 1. 类型安全
- 编译时错误检查
- 泛型支持结构化响应
- 空安全的Kotlin设计

### 2. 性能优化
- 连接池复用
- 批量处理优化  
- 流式响应支持

### 3. 错误处理
- 分层错误处理
- 自动重试和回退
- 友好的错误信息

### 4. 测试友好
- 易于mock的接口设计
- 独立的组件测试
- 集成测试支持

这个设计在简洁性和功能性之间取得了良好平衡，既满足了日常使用的简洁需求，又为复杂场景提供了足够的扩展能力。