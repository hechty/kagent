# LLM DSL 练习题参考答案

## 基础练习答案

### 练习1: 简单问答
```kotlin
suspend fun exercise1() {
    val llmService = LLMService()
    
    val response = llm(llmService) {
        provider { 
            deepseek("your-api-key").model("deepseek-chat") 
        }
    }.ask("什么是Kotlin协程？")
    
    println("回答: $response")
}
```

### 练习2: 对话构建
```kotlin
suspend fun exercise2() {
    val llmService = LLMService()
    
    val response = llm(llmService) {
        provider { 
            deepseek("your-api-key").model("deepseek-chat") 
        }
    }.chat {
        system("你是一个Kotlin专家")
        user("协程和线程有什么区别？")
        assistant("协程是轻量级的并发编程概念，与传统线程相比...")
        user("协程如何处理异常？")
    }
    
    println("专家回答: $response")
}
```

### 练习3: 配置模型参数
```kotlin
suspend fun exercise3() {
    val llmService = LLMService()
    
    val response = llm(llmService) {
        provider { 
            openai("your-api-key").model("gpt-4")
        }
        // 注意：当前DSL可能需要扩展以支持temperature和maxTokens配置
        // 这些参数通常在ChatRequest中设置
    }.ask("请简洁地解释什么是设计模式")
    
    println("回答: $response")
}
```

## 中级练习答案

### 练习4: 流式响应
```kotlin
suspend fun exercise4() {
    val llmService = LLMService()
    var totalChars = 0
    val startTime = System.currentTimeMillis()
    
    val execution = llm(llmService) {
        provider { 
            deepseek("your-api-key").model("deepseek-chat") 
        }
        stream(true)
    }
    
    execution.stream {
        user("请写一篇关于人工智能发展历史的短文")
    }.collect { chunk ->
        print(chunk)
        totalChars += chunk.length
    }
    
    val endTime = System.currentTimeMillis()
    println("\n\n统计信息:")
    println("总字符数: $totalChars")
    println("生成耗时: ${endTime - startTime}ms")
}
```

### 练习5: 错误处理和重试
```kotlin
suspend fun exercise5() {
    val llmService = LLMService()
    
    val response = llm(llmService) {
        provider { 
            deepseek("your-api-key").model("deepseek-chat") 
        }
        
        resilience {
            retry(maxAttempts = 3, backoff = BackoffStrategy.Exponential(1.seconds))
            timeout(30.seconds)
            circuitBreaker(failureThreshold = 5)
        }
    }.ask("在网络不稳定的情况下，这个请求应该能够重试")
    
    println("弹性请求成功: $response")
}
```

### 练习6: 模型回退策略
```kotlin
suspend fun exercise6() {
    val llmService = LLMService()
    
    val response = llm(llmService) {
        provider { 
            openai("your-openai-key").model("gpt-4") 
        }
        
        fallbackModels {
            model { anthropic("your-anthropic-key").model("claude-3-5-sonnet") }
            model { deepseek("your-deepseek-key").model("deepseek-chat") }
        }
    }.ask("这是一个测试回退策略的请求")
    
    println("回答 (可能来自备用模型): $response")
}
```

### 练习7: 上下文窗口管理
```kotlin
suspend fun exercise7() {
    val llmService = LLMService()
    
    val execution = llm(llmService) {
        provider { 
            deepseek("your-api-key").model("deepseek-chat") 
        }
        
        contextWindow {
            maxTokens(1000)
            strategy(ContextStrategy.SLIDING_WINDOW)
        }
    }
    
    // 模拟长对话
    val questions = listOf(
        "什么是Kotlin？",
        "Kotlin有哪些特性？",
        "协程是什么？",
        "如何使用协程？",
        "协程和线程的区别？",
        "挂起函数是什么？",
        "如何处理协程异常？",
        "什么是结构化并发？",
        "Flow是什么？",
        "如何测试协程？"
    )
    
    for ((index, question) in questions.withIndex()) {
        val response = execution.ask("第${index + 1}个问题：$question")
        println("Q$${index + 1}: $question")
        println("A$${index + 1}: ${response.toString().take(100)}...")
        println("---")
    }
}
```

## 高级练习答案

### 练习8: 函数调用 - 天气查询
```kotlin
@Serializable
data class WeatherRequest(val city: String)

@Serializable
data class WeatherResponse(
    val city: String,
    val temperature: Double,
    val description: String,
    val humidity: Int
)

// 模拟天气服务
object WeatherService {
    suspend fun getWeather(city: String): WeatherResponse {
        // 模拟API调用延迟
        delay(100)
        
        // 返回模拟数据
        return when (city.lowercase()) {
            "北京", "beijing" -> WeatherResponse("北京", 15.0, "晴朗", 45)
            "上海", "shanghai" -> WeatherResponse("上海", 18.0, "多云", 60)
            "深圳", "shenzhen" -> WeatherResponse("深圳", 25.0, "小雨", 80)
            else -> WeatherResponse(city, 20.0, "未知", 50)
        }
    }
}

suspend fun exercise8() {
    val llmService = LLMService()
    
    val response = llm(llmService) {
        provider { 
            deepseek("your-api-key").model("deepseek-chat") 
        }
        
        tools {
            function(
                "getCurrentWeather",
                WeatherRequest::class,
                WeatherResponse::class
            ) { request: WeatherRequest ->
                WeatherService.getWeather(request.city)
            }
        }
    }.ask("请查询北京的天气情况")
    
    println("天气查询结果: $response")
}
```

### 练习9: 类型安全响应 - 结构化数据
```kotlin
@Serializable
data class TravelPlan(
    val destination: String,
    val duration: Int,
    val budget: Double,
    val itinerary: List<DayPlan>,
    val estimatedCost: Double
)

@Serializable
data class DayPlan(
    val day: Int,
    val activities: List<String>,
    val meals: List<String>,
    val accommodation: String
)

suspend fun exercise9() {
    val llmService = LLMService()
    
    val plan = llm(llmService) {
        provider { 
            openai("your-api-key").model("gpt-4") 
        }
        responseFormat(TravelPlan::class)
    }.ask("制定一个日本5天旅行计划，预算2万元，包括详细的行程安排")
    
    // plan 应该是 TravelPlan 类型
    if (plan is TravelPlan) {
        println("目的地: ${plan.destination}")
        println("天数: ${plan.duration}")
        println("预算: ${plan.budget}")
        println("预估花费: ${plan.estimatedCost}")
        
        plan.itinerary.forEach { day ->
            println("第${day.day}天:")
            println("  活动: ${day.activities.joinToString(", ")}")
            println("  餐饮: ${day.meals.joinToString(", ")}")
            println("  住宿: ${day.accommodation}")
        }
    }
}
```

### 练习10: 批量处理 - 文本分析
```kotlin
suspend fun exercise10() {
    val llmService = LLMService()
    
    val articles = listOf(
        "今天天气真好，心情愉快，工作效率很高！",
        "这部电影太糟糕了，浪费了我两个小时的时间。",
        "Kotlin是一种现代的编程语言，具有简洁的语法和强大的功能。",
        "股市今天大跌，投资者损失惨重，市场情绪低迷。",
        "新的AI技术突破为医疗诊断带来了希望。",
        "公司今天宣布裁员，员工们都很担心自己的工作。",
        "春天来了，花儿开了，一切都充满了生机。",
        "技术文档：如何正确使用Kotlin协程进行异步编程。"
    )
    
    val startTime = System.currentTimeMillis()
    
    val execution = llm(llmService) {
        provider { 
            deepseek("your-api-key").model("deepseek-chat") 
        }
        
        batch {
            concurrency(3)
            rateLimit(10, per = 1.minutes)
        }
        
        resilience {
            retry(maxAttempts = 2)
            timeout(30.seconds)
        }
    }
    
    val sentiments = execution.batch(articles) { article ->
        "请分析以下文本的情感倾向，只回答：正面、负面或中性。文本：$article"
    }
    
    val endTime = System.currentTimeMillis()
    
    println("批量情感分析结果:")
    articles.zip(sentiments).forEachIndexed { index, (article, sentiment) ->
        println("${index + 1}. 文本: ${article.take(30)}...")
        println("   情感: $sentiment")
        println()
    }
    
    println("处理统计:")
    println("总文章数: ${articles.size}")
    println("成功处理: ${sentiments.size}")
    println("处理时间: ${endTime - startTime}ms")
    println("成功率: ${(sentiments.size.toDouble() / articles.size * 100).toInt()}%")
}
```

## 实战项目答案

### 练习11: 智能客服系统
```kotlin
// 订单查询工具
@Serializable
data class OrderRequest(val orderId: String)

@Serializable
data class OrderInfo(
    val orderId: String,
    val status: String,
    val items: List<String>,
    val total: Double,
    val createTime: String
)

// 情感分析工具
@Serializable
data class EmotionRequest(val text: String)

@Serializable
data class EmotionResponse(
    val emotion: String, // happy, angry, neutral, frustrated
    val intensity: Int   // 1-10
)

class CustomerServiceBot(private val llmService: LLMService) {
    private val conversationHistory = mutableListOf<Message>()
    
    suspend fun handleCustomerQuery(userInput: String): String {
        // 添加用户消息到历史
        conversationHistory.add(Message("user", userInput))
        
        val response = llm(llmService) {
            provider { 
                deepseek("your-api-key").model("deepseek-chat") 
            }
            
            contextWindow {
                maxTokens(2000)
                strategy(ContextStrategy.SLIDING_WINDOW)
            }
            
            tools {
                function(
                    "queryOrder",
                    OrderRequest::class,
                    OrderInfo::class
                ) { request ->
                    queryOrderInfo(request.orderId)
                }
                
                function(
                    "analyzeEmotion",
                    EmotionRequest::class,
                    EmotionResponse::class
                ) { request ->
                    analyzeUserEmotion(request.text)
                }
            }
        }.chat {
            system("""
                你是一个专业的客服助手。请友好、耐心地帮助客户。
                如果客户情绪激动，请先安抚情绪。
                对于复杂问题，可以建议转接人工客服。
                你可以使用以下工具：
                - queryOrder: 查询订单信息
                - analyzeEmotion: 分析客户情绪
            """.trimIndent())
            
            // 添加历史对话
            conversationHistory.forEach { msg ->
                when (msg.role) {
                    "user" -> user(msg.content)
                    "assistant" -> assistant(msg.content)
                    "system" -> system(msg.content)
                }
            }
        }
        
        // 添加助手回复到历史
        conversationHistory.add(Message("assistant", response.toString()))
        
        return response.toString()
    }
    
    private suspend fun queryOrderInfo(orderId: String): OrderInfo {
        // 模拟订单查询
        return OrderInfo(
            orderId = orderId,
            status = "已发货",
            items = listOf("Kotlin编程书籍", "程序员T恤"),
            total = 299.0,
            createTime = "2024-01-15 14:30:00"
        )
    }
    
    private suspend fun analyzeUserEmotion(text: String): EmotionResponse {
        // 简单的情感分析逻辑
        return when {
            text.contains("生气") || text.contains("愤怒") -> 
                EmotionResponse("angry", 8)
            text.contains("满意") || text.contains("好的") -> 
                EmotionResponse("happy", 7)
            text.contains("着急") || text.contains("急") -> 
                EmotionResponse("frustrated", 6)
            else -> EmotionResponse("neutral", 3)
        }
    }
}

suspend fun exercise11() {
    val llmService = LLMService()
    val bot = CustomerServiceBot(llmService)
    
    // 模拟客服对话
    val queries = listOf(
        "你好，我想查询我的订单",
        "我的订单号是ORD123456",
        "为什么还没有发货？我很着急！",
        "好的，谢谢你的帮助"
    )
    
    for (query in queries) {
        println("客户: $query")
        val response = bot.handleCustomerQuery(query)
        println("客服: $response")
        println("---")
    }
}
```

### 练习12: 代码审查助手
```kotlin
@Serializable
data class CodeReviewRequest(
    val code: String,
    val language: String
)

@Serializable
data class CodeReviewResponse(
    val issues: List<CodeIssue>,
    val suggestions: List<String>,
    val improvedCode: String,
    val overallScore: Int // 1-10
)

@Serializable
data class CodeIssue(
    val type: String, // "performance", "readability", "security", "style"
    val severity: String, // "low", "medium", "high"
    val description: String,
    val line: Int?
)

suspend fun exercise12() {
    val llmService = LLMService()
    
    val codeToReview = """
    fun processUsers(users: List<User>): List<String> {
        val result = mutableListOf<String>()
        for (user in users) {
            if (user.isActive) {
                result.add(user.name.toUpperCase())
            }
        }
        return result
    }
    """.trimIndent()
    
    val review = llm(llmService) {
        provider { 
            openai("your-api-key").model("gpt-4") 
        }
        responseFormat(CodeReviewResponse::class)
    }.ask("""
        请审查以下Kotlin代码，提供详细的改进建议：
        
        ```kotlin
        $codeToReview
        ```
        
        请从以下方面分析：
        1. 代码可读性
        2. 性能优化
        3. Kotlin惯用法
        4. 潜在问题
        
        并提供改进后的代码版本。
    """.trimIndent())
    
    if (review is CodeReviewResponse) {
        println("代码审查报告:")
        println("总体评分: ${review.overallScore}/10")
        println()
        
        println("发现的问题:")
        review.issues.forEach { issue ->
            println("- [${issue.severity.uppercase()}] ${issue.type}: ${issue.description}")
            issue.line?.let { println("  行号: $it") }
        }
        println()
        
        println("改进建议:")
        review.suggestions.forEach { suggestion ->
            println("- $suggestion")
        }
        println()
        
        println("改进后的代码:")
        println(review.improvedCode)
    }
}
```

### 练习13: 多模型投票系统
```kotlin
data class ModelResult(
    val model: String,
    val response: String,
    val confidence: Double,
    val responseTime: Long
)

data class VotingResult(
    val winningResponse: String,
    val winningModel: String,
    val allResults: List<ModelResult>,
    val judgeReasoning: String
)

class MultiModelVoting(private val llmService: LLMService) {
    
    suspend fun getConsensusAnswer(question: String): VotingResult {
        // 1. 向多个模型提问
        val models = listOf(
            "openai" to "your-openai-key",
            "anthropic" to "your-anthropic-key", 
            "deepseek" to "your-deepseek-key"
        )
        
        val results = mutableListOf<ModelResult>()
        
        for ((modelName, apiKey) in models) {
            try {
                val startTime = System.currentTimeMillis()
                
                val response = llm(llmService) {
                    provider {
                        when (modelName) {
                            "openai" -> openai(apiKey).model("gpt-4")
                            "anthropic" -> anthropic(apiKey).model("claude-3-5-sonnet")
                            "deepseek" -> deepseek(apiKey).model("deepseek-chat")
                            else -> throw IllegalArgumentException("Unknown model: $modelName")
                        }
                    }
                    resilience {
                        retry(maxAttempts = 2)
                        timeout(30.seconds)
                    }
                }.ask(question)
                
                val endTime = System.currentTimeMillis()
                
                results.add(ModelResult(
                    model = modelName,
                    response = response.toString(),
                    confidence = calculateConfidence(response.toString()),
                    responseTime = endTime - startTime
                ))
                
            } catch (e: Exception) {
                println("模型 $modelName 请求失败: ${e.message}")
            }
        }
        
        // 2. 使用裁判模型选择最佳答案
        val judgeResponse = llm(llmService) {
            provider { 
                openai("your-openai-key").model("gpt-4") 
            }
        }.ask(buildJudgePrompt(question, results))
        
        // 3. 解析裁判结果
        val winningModel = extractWinningModel(judgeResponse.toString())
        val winningResponse = results.find { it.model == winningModel }?.response 
            ?: results.firstOrNull()?.response ?: "无法获取结果"
        
        return VotingResult(
            winningResponse = winningResponse,
            winningModel = winningModel,
            allResults = results,
            judgeReasoning = judgeResponse.toString()
        )
    }
    
    private fun buildJudgePrompt(question: String, results: List<ModelResult>): String {
        return """
        请作为公正的裁判，评估以下不同AI模型对问题的回答质量。
        
        问题: $question
        
        各模型回答:
        ${results.mapIndexed { index, result ->
            "${index + 1}. 模型${result.model}:\n${result.response}\n"
        }.joinToString("\n")}
        
        请选择最准确、最有帮助的回答，并说明理由。
        请在回答开头明确说明: "最佳回答来自: [模型名称]"
        """.trimIndent()
    }
    
    private fun extractWinningModel(judgeResponse: String): String {
        val regex = "最佳回答来自:?\\s*(\\w+)".toRegex()
        return regex.find(judgeResponse)?.groupValues?.get(1) ?: "unknown"
    }
    
    private fun calculateConfidence(response: String): Double {
        // 简单的信心度计算逻辑
        return when {
            response.contains("确定") || response.contains("肯定") -> 0.9
            response.contains("可能") || response.contains("大概") -> 0.7
            response.contains("不确定") || response.contains("可能不") -> 0.5
            else -> 0.8
        }
    }
}

suspend fun exercise13() {
    val llmService = LLMService()
    val voting = MultiModelVoting(llmService)
    
    val questions = listOf(
        "什么是量子计算的基本原理？",
        "如何优化Kotlin代码的性能？",
        "人工智能的未来发展趋势是什么？"
    )
    
    for (question in questions) {
        println("问题: $question")
        println("="*50)
        
        val result = voting.getConsensusAnswer(question)
        
        println("各模型表现:")
        result.allResults.forEach { model ->
            println("${model.model}: ${model.response.take(100)}... (${model.responseTime}ms)")
        }
        println()
        
        println("裁判决定: ${result.winningModel}")
        println("获胜答案: ${result.winningResponse.take(200)}...")
        println()
        println("裁判理由: ${result.judgeReasoning}")
        println("\n" + "="*80 + "\n")
    }
}
```

这些参考答案展示了如何使用LLM DSL的各种功能。在实际练习中，你需要：

1. 替换为你的真实API密钥
2. 根据具体需求调整参数
3. 添加适当的错误处理
4. 测试不同场景下的表现

记住：这些只是参考实现，鼓励你根据自己的理解和创意来完成练习！