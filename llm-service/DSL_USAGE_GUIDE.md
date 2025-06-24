# LLM Service DSL 使用指南

## 快速开始

### 1. 基础使用

```kotlin
// 创建LLM服务实例
val llmService = LLMService()

// 注册提供商（需要在使用前注册）
llmService.registerProvider(ProviderType.OPENAI, OpenAIProvider("your-api-key", httpClient))

// 基础使用 - 单次询问
val execution = llm(llmService) {
    provider { 
        openai("your-api-key").model("gpt-4") 
    }
}

val response = execution.ask("你好，请介绍一下人工智能")
println(response)
```

### 2. 对话模式

```kotlin
val execution = llm(llmService) {
    provider { openai("your-api-key").model("gpt-4") }
}

val response = execution.chat {
    system("你是一个专业的AI助手")
    user("什么是机器学习？")
    assistant("机器学习是人工智能的一个子领域...")
    user("请详细解释深度学习")
}
```

### 3. 流式响应

```kotlin
val execution = llm(llmService) {
    provider { openai("your-api-key").model("gpt-4") }
    stream(true)
}

execution.stream {
    user("写一篇关于量子计算的文章")
}.collect { chunk ->
    print(chunk) // 实时显示生成的内容
}
```

## 高级功能

### 1. 错误处理和重试

```kotlin
val execution = llm(llmService) {
    provider { openai("your-api-key").model("gpt-4") }
    
    resilience {
        retry(maxAttempts = 3, backoff = BackoffStrategy.Exponential(1.seconds))
        timeout(30.seconds)
        circuitBreaker(failureThreshold = 5)
    }
}
```

### 2. 模型回退策略

```kotlin
val execution = llm(llmService) {
    // 主要模型
    provider { openai("openai-key").model("gpt-4") }
    
    // 备用模型
    fallbackModels {
        model { anthropic("anthropic-key").model("claude-3-5-sonnet") }
        model { deepseek("deepseek-key").model("deepseek-chat") }
    }
}
```

### 3. 上下文窗口管理

```kotlin
val execution = llm(llmService) {
    provider { openai("your-api-key").model("gpt-4") }
    
    contextWindow {
        maxTokens(8192)
        strategy(ContextStrategy.SLIDING_WINDOW) // 或 SUMMARIZE, TRUNCATE
        summarizer { messages ->
            "之前对话摘要: ${messages.takeLast(5).joinToString { it.content.take(100) }}"
        }
    }
}
```

### 4. 工具和函数调用

```kotlin
@Serializable
data class WeatherRequest(val location: String)

@Serializable
data class WeatherResponse(val location: String, val temperature: Double, val description: String)

val execution = llm(llmService) {
    provider { openai("your-api-key").model("gpt-4") }
    
    tools {
        // 类型安全的函数定义
        function(
            "getCurrentWeather",
            WeatherRequest::class,
            WeatherResponse::class
        ) { request: WeatherRequest ->
            // 调用实际的天气服务
            WeatherService.getWeather(request.location)
        }
        
        // 使用现有的工具类
        tool(CalculatorTool())
    }
}

val response = execution.ask("请查询北京的天气情况")
```

### 5. 类型安全的响应

```kotlin
@Serializable
data class TravelPlan(
    val destination: String,
    val days: Int,
    val activities: List<String>,
    val budget: Double
)

val execution = llm(llmService) {
    provider { openai("your-api-key").model("gpt-4") }
    responseFormat(TravelPlan::class)
}

// 返回值会被自动解析为TravelPlan对象
val plan = execution.ask("制定一个去日本5天的旅行计划，预算2万元")
```

### 6. 批量处理

```kotlin
val texts = listOf(
    "这是第一段需要处理的文本...",
    "这是第二段需要处理的文本...",
    "这是第三段需要处理的文本..."
)

val execution = llm(llmService) {
    provider { openai("your-api-key").model("gpt-4") }
    
    batch {
        concurrency(5) // 最大并发数
        rateLimit(100, per = 1.minutes) // 速率限制
    }
    
    resilience {
        retry(maxAttempts = 2)
        timeout(30.seconds)
    }
}

val summaries = execution.batch(texts) { text ->
    "请总结以下文本: $text"
}

summaries.forEach { summary ->
    println("摘要: $summary")
}
```

## 配置选项详解

### Provider配置

```kotlin
provider {
    // OpenAI
    openai("api-key", "custom-base-url") // baseUrl可选
    
    // Anthropic
    anthropic("api-key")
    
    // DeepSeek
    deepseek("api-key")
    
    // 指定模型
    model("gpt-4")
}
```

### 重试策略

```kotlin
resilience {
    // 固定延迟重试
    retry(maxAttempts = 3, backoff = BackoffStrategy.Fixed(2.seconds))
    
    // 指数退避重试
    retry(maxAttempts = 3, backoff = BackoffStrategy.Exponential(1.seconds, maxDelay = 60.seconds))
    
    // 线性退避重试
    retry(maxAttempts = 3, backoff = BackoffStrategy.Linear(1.seconds))
    
    // 超时设置
    timeout(30.seconds)
    
    // 熔断器
    circuitBreaker(failureThreshold = 5, resetTimeout = 60.seconds)
}
```

### 上下文策略

```kotlin
contextWindow {
    maxTokens(8192)
    
    // 截断策略
    strategy(ContextStrategy.TRUNCATE)
    
    // 滑动窗口（保留最新消息）
    strategy(ContextStrategy.SLIDING_WINDOW)
    
    // 智能摘要（需要提供摘要函数）
    strategy(ContextStrategy.SUMMARIZE)
    summarizer { messages ->
        // 自定义摘要逻辑
        "对话摘要: ${messages.size}条消息，主要讨论了..."
    }
}
```

## 最佳实践

### 1. 错误处理

```kotlin
try {
    val response = execution.ask("你的问题")
    // 处理响应
} catch (e: LLMExecutionException) {
    // 处理LLM执行相关的错误
    println("LLM执行失败: ${e.message}")
} catch (e: Exception) {
    // 处理其他错误
    println("未知错误: ${e.message}")
}
```

### 2. 资源管理

```kotlin
// 创建HTTP客户端（应该在应用启动时创建并复用）
val httpClient = HttpClient(CIO) {
    install(ContentNegotiation) {
        json()
    }
    install(Logging) {
        level = LogLevel.INFO
    }
}

// 在应用关闭时记得关闭客户端
// httpClient.close()
```

### 3. 配置复用

```kotlin
// 创建通用配置
fun createLLMExecution(llmService: LLMService, apiKey: String) = llm(llmService) {
    provider { openai(apiKey).model("gpt-4") }
    
    resilience {
        retry(maxAttempts = 3, backoff = BackoffStrategy.Exponential(1.seconds))
        timeout(30.seconds)
    }
    
    contextWindow {
        maxTokens(8192)
        strategy(ContextStrategy.SLIDING_WINDOW)
    }
}

// 使用通用配置
suspend fun main() {
    val llmService = LLMService()
    val execution = createLLMExecution(llmService, "your-api-key")
    
    val response = execution.ask("你的问题")
    println(response)
}
```

### 4. 监控和日志

```kotlin
val execution = llm(llmService) {
    provider { openai("your-api-key").model("gpt-4") }
    
    resilience {
        retry(maxAttempts = 3) {
            // 可以在这里添加重试日志
            println("正在重试请求...")
        }
    }
}
```

## 常见问题

### Q: 如何处理API限流？

A: 使用速率限制配置：

```kotlin
batch {
    concurrency(5) // 限制并发数
    rateLimit(60, per = 1.minutes) // 每分钟最多60个请求
}
```

### Q: 如何实现自定义的回退策略？

A: 可以通过fallbackModels配置多个备用模型：

```kotlin
fallbackModels {
    model { anthropic("key1").model("claude-3-5-sonnet") }
    model { deepseek("key2").model("deepseek-chat") }
    model { openai("key3").model("gpt-3.5-turbo") } // 最后的备用选择
}
```

### Q: 如何优化长对话的性能？

A: 使用上下文窗口管理：

```kotlin
contextWindow {
    maxTokens(8192)
    strategy(ContextStrategy.SUMMARIZE)
    summarizer { messages ->
        // 使用另一个LLM来生成摘要
        summarizationService.summarize(messages)
    }
}
```

### Q: 如何添加自定义工具？

A: 实现Tool接口：

```kotlin
class DatabaseTool(private val connection: DatabaseConnection) : Tool {
    override val name = "database_query"
    
    override suspend fun execute(input: String): String {
        val query = Json.decodeFromString<DatabaseQuery>(input)
        val result = connection.execute(query.sql)
        return Json.encodeToString(result)
    }
}

// 使用自定义工具
tools {
    tool(DatabaseTool(databaseConnection))
}
```

这个DSL设计提供了强大而灵活的LLM服务接口，支持从简单的单次查询到复杂的企业级应用场景。通过合理配置和使用这些功能，可以构建出稳定、高效的LLM应用。