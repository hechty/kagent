package com.llmservice.examples

import com.llmservice.dsl.*
import com.llmservice.service.LLMService
import kotlinx.coroutines.flow.collect
import kotlinx.serialization.Serializable
import kotlin.time.Duration.Companion.seconds
import kotlin.time.Duration.Companion.minutes

/**
 * DSL使用示例
 */
class DSLExamples {
    
    /**
     * 示例1: 基本使用
     */
    suspend fun basicExample(llmService: LLMService) {
        val execution = llm(llmService) {
            provider { 
                openai("your-api-key").model("gpt-4") 
            }
        }
        
        val response = execution.ask("你好，请介绍一下自己")
        
        println("响应: $response")
    }
    
    /**
     * 示例2: 流式响应
     */
    suspend fun streamingExample(llmService: LLMService) {
        val execution = llm(llmService) {
            provider { 
                openai("your-api-key").model("gpt-4") 
            }
            stream(true)
        }
        
        execution.stream {
            user("写一篇关于人工智能的长文章")
        }.collect { chunk ->
            print(chunk)
        }
    }
    
    /**
     * 示例3: 错误处理和重试
     */
    suspend fun resilienceExample(llmService: LLMService) {
        val execution = llm(llmService) {
            provider { 
                openai("your-api-key").model("gpt-4") 
            }
            
            resilience {
                retry(maxAttempts = 3, backoff = BackoffStrategy.Exponential(1.seconds))
                timeout(30.seconds)
                circuitBreaker(failureThreshold = 5)
            }
        }
        
        val response = execution.ask("解释量子计算的基本原理")
        
        println("响应: $response")
    }
    
    /**
     * 示例4: 模型回退策略
     */
    suspend fun fallbackExample(llmService: LLMService) {
        val execution = llm(llmService) {
            provider { 
                openai("your-api-key").model("gpt-4") 
            }
            
            fallbackModels {
                model {
                    anthropic("your-anthropic-key").model("claude-3-5-sonnet")
                }
                model {
                    deepseek("your-deepseek-key").model("deepseek-chat")
                }
            }
        }
        
        val response = execution.ask("分析这个市场趋势")
        
        println("响应: $response")
    }
    
    /**
     * 示例5: 上下文窗口管理
     */
    suspend fun contextManagementExample(llmService: LLMService) {
        val execution = llm(llmService) {
            provider { 
                openai("your-api-key").model("gpt-4") 
            }
            
            contextWindow {
                maxTokens(8192)
                strategy(ContextStrategy.SLIDING_WINDOW)
                summarizer { messages ->
                    "之前的对话主要讨论了: ${messages.joinToString(", ") { it.content.take(50) }}"
                }
            }
        }
        
        val response = execution.chat {
            system("你是一个专业的AI助手")
            user("我们来讨论一下机器学习的发展历史")
            assistant("好的，我很乐意和您讨论机器学习的发展历史...")
            user("请详细介绍一下深度学习的突破")
        }
        
        println("响应: $response")
    }
    
    /**
     * 示例6: 函数调用和工具集成
     */
    suspend fun toolsExample(llmService: LLMService) {
        val execution = llm(llmService) {
            provider { 
                openai("your-api-key").model("gpt-4") 
            }
            
            tools {
                function(
                    "getCurrentWeather",
                    WeatherRequest::class,
                    WeatherResponse::class
                ) { request: WeatherRequest ->
                    // 调用天气API
                    WeatherResponse(
                        location = request.location,
                        temperature = 25.0,
                        description = "晴朗"
                    )
                }
                
                function(
                    "sendEmail",
                    EmailRequest::class,
                    EmailResponse::class
                ) { request: EmailRequest ->
                    // 发送邮件
                    EmailResponse(
                        success = true,
                        messageId = "email-123"
                    )
                }
                
                tool(CalculatorTool())
            }
        }
        
        val response = execution.ask("请帮我查询北京的天气，然后发送邮件给张三")
        
        println("响应: $response")
    }
    
    /**
     * 示例7: 类型安全的响应处理
     */
    suspend fun typeSafeResponseExample(llmService: LLMService) {
        val execution = llm(llmService) {
            provider { 
                openai("your-api-key").model("gpt-4") 
            }
            
            responseFormat(TravelPlan::class)
        }
        
        val plan = execution.ask("制定一个去日本5天的旅行计划，预算2万元")
        
        // plan现在是TravelPlan类型
        println("旅行计划: $plan")
    }
    
    /**
     * 示例8: 批量处理
     */
    suspend fun batchProcessingExample(llmService: LLMService) {
        val texts = listOf(
            "这是一段需要总结的文本1...",
            "这是一段需要总结的文本2...",
            "这是一段需要总结的文本3..."
        )
        
        val execution = llm(llmService) {
            provider { 
                openai("your-api-key").model("gpt-4") 
            }
            
            resilience {
                retry(maxAttempts = 2)
                timeout(30.seconds)
            }
        }
        
        val results = execution.batch(texts) { text ->
            "请总结这段文字: $text"
        }
        
        results.forEach { result ->
            println("总结: $result")
        }
    }
    
    /**
     * 示例9: 复杂的多功能组合
     */
    suspend fun complexExample(llmService: LLMService) {
        val execution = llm(llmService) {
            // 主提供商配置
            provider { 
                openai("your-api-key").model("gpt-4") 
            }
            
            // 回退策略
            fallbackModels {
                model {
                    anthropic("your-anthropic-key").model("claude-3-5-sonnet")
                }
            }
            
            // 弹性配置
            resilience {
                retry(maxAttempts = 3, backoff = BackoffStrategy.Exponential(1.seconds))
                timeout(60.seconds)
                circuitBreaker(failureThreshold = 10)
            }
            
            // 上下文管理
            contextWindow {
                maxTokens(16384)
                strategy(ContextStrategy.SUMMARIZE)
                summarizer { messages ->
                    "对话摘要: 主要讨论了AI技术的发展和应用"
                }
            }
            
            // 工具集成
            tools {
                function(
                    "webSearch",
                    SearchRequest::class,
                    SearchResponse::class
                ) { request: SearchRequest ->
                    SearchResponse(
                        query = request.query,
                        results = listOf("搜索结果1", "搜索结果2")
                    )
                }
            }
            
            // 类型安全响应
            responseFormat(AnalysisReport::class)
        }
        
        // 对话
        val response = execution.chat {
            system("你是一个专业的AI研究分析师")
            user("请分析当前AI技术的发展趋势，并提供详细的报告")
        }
        
        println("分析报告: $response")
    }
}

// 数据类定义
@Serializable
data class TravelPlan(
    val destination: String,
    val days: Int,
    val activities: List<String>,
    val budget: Double
)

@Serializable
data class WeatherRequest(val location: String)

@Serializable
data class WeatherResponse(
    val location: String,
    val temperature: Double,
    val description: String
)

@Serializable
data class EmailRequest(
    val to: String,
    val subject: String,
    val body: String
)

@Serializable
data class EmailResponse(
    val success: Boolean,
    val messageId: String
)

@Serializable
data class SearchRequest(val query: String)

@Serializable
data class SearchResponse(
    val query: String,
    val results: List<String>
)

@Serializable
data class AnalysisReport(
    val title: String,
    val summary: String,
    val trends: List<String>,
    val recommendations: List<String>
)

// 示例工具实现
class CalculatorTool : Tool {
    override val name: String = "calculator"
    
    override suspend fun execute(input: String): String {
        // 简单的计算器实现
        return try {
            val result = when {
                input.contains("+") -> {
                    val parts = input.split("+")
                    parts[0].trim().toDouble() + parts[1].trim().toDouble()
                }
                input.contains("-") -> {
                    val parts = input.split("-")
                    parts[0].trim().toDouble() - parts[1].trim().toDouble()
                }
                input.contains("*") -> {
                    val parts = input.split("*")
                    parts[0].trim().toDouble() * parts[1].trim().toDouble()
                }
                input.contains("/") -> {
                    val parts = input.split("/")
                    parts[0].trim().toDouble() / parts[1].trim().toDouble()
                }
                else -> input.toDouble()
            }
            result.toString()
        } catch (e: Exception) {
            "计算错误: ${e.message}"
        }
    }
}