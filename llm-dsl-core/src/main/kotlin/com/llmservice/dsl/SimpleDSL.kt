package com.llmservice.dsl

import com.llmservice.model.*
import com.llmservice.service.*
import com.llmservice.service.LLMProvider
import com.llmservice.provider.*
import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.plugins.logging.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.coroutines.*
import kotlinx.serialization.json.Json
import kotlin.time.Duration
import kotlin.time.Duration.Companion.seconds

/**
 * 简洁而富有表达力的LLM DSL - 最终版本
 * 设计原则：简洁优于复杂，渐进式复杂度，符合直觉
 */

// ========================================
// 1. 核心配置类
// ========================================

data class LLMConfig(
    var temperature: Double = 0.7,
    var maxTokens: Int? = null,
    var timeout: Duration = 30.seconds
)

// ========================================
// 2. Provider工厂函数 - 使用StandaloneDSLRunner
// ========================================


/**
 * 自定义API密钥的DeepSeek提供商
 */
fun deepseek(apiKey: String, model: String = "deepseek-chat", config: (LLMConfig.() -> Unit)? = null): LLMProvider {
    val httpClient = HttpClient(CIO) {
        install(io.ktor.client.plugins.contentnegotiation.ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                isLenient = true
            })
        }
        install(io.ktor.client.plugins.logging.Logging) {
            level = LogLevel.INFO
        }
    }
    return DeepSeekProvider(apiKey, httpClient = httpClient)
}

/**
 * 自定义API密钥的OpenRouter提供商
 */
fun openrouter(apiKey: String, model: String = "openai/gpt-4", config: (LLMConfig.() -> Unit)? = null): LLMProvider {
    val httpClient = HttpClient(CIO) {
        install(io.ktor.client.plugins.contentnegotiation.ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                isLenient = true
            })
        }
        install(io.ktor.client.plugins.logging.Logging) {
            level = LogLevel.INFO
        }
    }
    return OpenRouterProvider(apiKey, httpClient = httpClient)
}

fun mockProvider(name: String, model: String = "mock-model"): LLMProvider {
    return object : LLMProvider {
        override val name = name
        override val supportedModels = listOf(model)
        override suspend fun chat(request: ChatRequest): ChatResponse {
            delay(100) // 模拟网络延迟
            return ChatResponse(
                id = "${name}-${System.currentTimeMillis()}",
                choices = listOf(
                    Choice(
                        index = 0,
                        message = Message("assistant", "$name 模拟回答: ${request.messages.last().content}"),
                        finishReason = "stop"
                    )
                ),
                usage = Usage(10, 20, 30)
            )
        }
    }
}

// ========================================
// 3. 核心DSL函数
// ========================================

/**
 * 最简单的用法：ask("你好") using provider
 */
suspend infix fun String.using(provider: LLMProvider): String {
    val request = ChatRequest(
        model = provider.supportedModels.firstOrNull() ?: "default",
        messages = listOf(Message("user", this))
    )
    val response = provider.chat(request)
    return response.choices.first().message.content
}

/**
 * 简化版对话管理
 */
class SimpleConversation(private val provider: LLMProvider) {
    private val messages = mutableListOf<Message>()
    
    fun system(content: String) {
        messages.add(Message("system", content))
    }
    
    suspend fun ask(content: String): String {
        messages.add(Message("user", content))
        val request = ChatRequest(
            model = provider.supportedModels.firstOrNull() ?: "default",
            messages = messages.toList()
        )
        val response = provider.chat(request)
        val answer = response.choices.first().message.content
        messages.add(Message("assistant", answer))
        return answer
    }
    
    val history: List<Message> get() = messages.toList()
}

fun conversation(provider: LLMProvider, init: suspend SimpleConversation.() -> Unit): SimpleConversation {
    val conv = SimpleConversation(provider)
    runBlocking { conv.init() }
    return conv
}

/**
 * 多模型对比
 */
suspend fun compare(question: String, providers: Map<String, LLMProvider>): Map<String, String> {
    return providers.mapValues { (_, provider) ->
        question using provider
    }
}

/**
 * 批量处理
 */
suspend fun List<String>.processAll(provider: LLMProvider): List<String> = coroutineScope {
    this@processAll.map { question ->
        async { question using provider }
    }.awaitAll()
}

/**
 * 简单的Agent
 */
class SimpleAgent(
    val name: String,
    private val provider: LLMProvider,
    private val role: String
) {
    suspend fun solve(problem: String): String {
        val prompt = if (role.isNotEmpty()) {
            "你是：$role。请解决：$problem"
        } else {
            problem
        }
        return prompt using provider
    }
}

fun agent(name: String, provider: LLMProvider, role: String = ""): SimpleAgent {
    return SimpleAgent(name, provider, role)
}

// ========================================
// 4. 便利函数
// ========================================

/**
 * 回退策略
 */
class FallbackProvider(
    private val primary: LLMProvider,
    private val fallbacks: List<LLMProvider>
) : LLMProvider {
    override val name = "Fallback(${primary.name})"
    override val supportedModels = primary.supportedModels
    
    override suspend fun chat(request: ChatRequest): ChatResponse {
        val allProviders = listOf(primary) + fallbacks
        
        for (provider in allProviders) {
            try {
                return provider.chat(request)
            } catch (e: Exception) {
                if (provider == allProviders.last()) throw e
                // 继续尝试下一个provider
            }
        }
        error("所有provider都失败了")
    }
}

fun LLMProvider.withFallback(vararg fallbacks: LLMProvider): FallbackProvider {
    return FallbackProvider(this, fallbacks.toList())
}

// ========================================
// 5. 全局便利函数
// ========================================

/**
 * 快速问答，使用默认provider
 */
private val defaultProvider by lazy { StandaloneDSLRunner.deepseek() }

suspend fun ask(question: String): String = question using defaultProvider

suspend fun quickCompare(question: String): Map<String, String> {
    return compare(question, mapOf(
        "deepseek" to StandaloneDSLRunner.deepseek(),
        "openrouter" to StandaloneDSLRunner.openrouter()
    ))
}