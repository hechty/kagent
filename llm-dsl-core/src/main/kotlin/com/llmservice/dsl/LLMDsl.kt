package com.llmservice.dsl

import com.llmservice.model.*
import com.llmservice.service.LLMProvider
import com.llmservice.service.ProviderType
import kotlinx.coroutines.flow.Flow
import kotlinx.serialization.KSerializer
import kotlin.time.Duration

/**
 * DSL的核心构建器类
 */
class LLMBuilder {
    internal var primaryProvider: ProviderConfig? = null
    internal var fallbackProviders: List<ProviderConfig> = emptyList()
    internal var resilienceConfig: ResilienceConfig? = null
    internal var contextConfig: ContextConfig? = null
    internal var streamConfig: StreamConfig? = null
    internal var batchConfig: BatchConfig? = null
    internal var toolsConfig: ToolsConfig? = null
    internal var responseFormat: ResponseFormatConfig? = null
    
    fun provider(block: ProviderConfigBuilder.() -> Unit) {
        primaryProvider = ProviderConfigBuilder().apply(block).build()
    }
    
    fun fallbackModels(block: FallbackConfigBuilder.() -> Unit) {
        fallbackProviders = FallbackConfigBuilder().apply(block).build()
    }
    
    fun resilience(block: ResilienceConfigBuilder.() -> Unit) {
        resilienceConfig = ResilienceConfigBuilder().apply(block).build()
    }
    
    fun contextWindow(block: ContextConfigBuilder.() -> Unit) {
        contextConfig = ContextConfigBuilder().apply(block).build()
    }
    
    fun stream(enabled: Boolean = true) {
        streamConfig = StreamConfig(enabled)
    }
    
    fun tools(block: ToolsConfigBuilder.() -> Unit) {
        toolsConfig = ToolsConfigBuilder().apply(block).build()
    }
    
    fun <T : Any> responseFormat(clazz: kotlin.reflect.KClass<T>): ResponseFormatConfig {
        responseFormat = ResponseFormatConfig(clazz)
        return responseFormat!!
    }
    
    fun batch(block: BatchConfigBuilder.() -> Unit) {
        batchConfig = BatchConfigBuilder().apply(block).build()
    }
}

/**
 * Provider配置构建器
 */
class ProviderConfigBuilder {
    private var type: ProviderType? = null
    private var apiKey: String? = null
    private var model: String? = null
    private var baseUrl: String? = null
    
    fun openai(apiKey: String, baseUrl: String? = null): ProviderConfigBuilder {
        this.type = ProviderType.OPENAI
        this.apiKey = apiKey
        this.baseUrl = baseUrl
        return this
    }
    
    fun anthropic(apiKey: String): ProviderConfigBuilder {
        this.type = ProviderType.ANTHROPIC
        this.apiKey = apiKey
        return this
    }
    
    fun deepseek(apiKey: String): ProviderConfigBuilder {
        this.type = ProviderType.DEEPSEEK
        this.apiKey = apiKey
        return this
    }
    
    fun model(modelName: String): ProviderConfigBuilder {
        this.model = modelName
        return this
    }
    
    internal fun build(): ProviderConfig {
        return ProviderConfig(
            type = type ?: throw IllegalStateException("Provider type must be specified"),
            apiKey = apiKey ?: throw IllegalStateException("API key must be specified"),
            model = model ?: throw IllegalStateException("Model must be specified"),
            baseUrl = baseUrl
        )
    }
}

/**
 * 回退配置构建器
 */
class FallbackConfigBuilder {
    private val providers = mutableListOf<ProviderConfig>()
    
    fun model(block: ProviderConfigBuilder.() -> Unit) {
        providers.add(ProviderConfigBuilder().apply(block).build())
    }
    
    internal fun build(): List<ProviderConfig> = providers.toList()
}

/**
 * 弹性配置构建器
 */
class ResilienceConfigBuilder {
    private var retryConfig: RetryConfig? = null
    private var circuitBreakerConfig: CircuitBreakerConfig? = null
    private var timeout: Duration? = null
    
    fun retry(maxAttempts: Int, backoff: BackoffStrategy = BackoffStrategy.Fixed(Duration.ZERO)) {
        retryConfig = RetryConfig(maxAttempts, backoff)
    }
    
    fun timeout(duration: Duration) {
        timeout = duration
    }
    
    fun circuitBreaker(failureThreshold: Int, resetTimeout: Duration = Duration.INFINITE) {
        circuitBreakerConfig = CircuitBreakerConfig(failureThreshold, resetTimeout)
    }
    
    internal fun build(): ResilienceConfig {
        return ResilienceConfig(retryConfig, circuitBreakerConfig, timeout)
    }
}

/**
 * 上下文配置构建器
 */
class ContextConfigBuilder {
    private var maxTokens: Int? = null
    private var strategy: ContextStrategy = ContextStrategy.TRUNCATE
    private var summarizer: ((List<Message>) -> String)? = null
    
    fun maxTokens(tokens: Int) {
        maxTokens = tokens
    }
    
    fun strategy(strategy: ContextStrategy) {
        this.strategy = strategy
    }
    
    fun summarizer(summarizer: (List<Message>) -> String) {
        this.summarizer = summarizer
    }
    
    internal fun build(): ContextConfig {
        return ContextConfig(maxTokens, strategy, summarizer)
    }
}

/**
 * 工具配置构建器
 */
class ToolsConfigBuilder {
    private val functions = mutableListOf<FunctionTool>()
    private val tools = mutableListOf<Tool>()
    
    fun <T : Any, R : Any> function(
        name: String,
        inputClass: kotlin.reflect.KClass<T>,
        outputClass: kotlin.reflect.KClass<R>,
        handler: suspend (T) -> R
    ) {
        functions.add(FunctionTool(name, inputClass, outputClass) { input ->
            @Suppress("UNCHECKED_CAST")
            handler(input as T)
        })
    }
    
    fun tool(tool: Tool) {
        tools.add(tool)
    }
    
    internal fun build(): ToolsConfig {
        return ToolsConfig(functions.toList(), tools.toList())
    }
}

/**
 * 批量配置构建器
 */
class BatchConfigBuilder {
    private var concurrency: Int = 1
    private var rateLimit: RateLimit? = null
    
    fun concurrency(limit: Int) {
        concurrency = limit
    }
    
    fun rateLimit(requests: Int, per: Duration) {
        rateLimit = RateLimit(requests, per)
    }
    
    internal fun build(): BatchConfig {
        return BatchConfig(concurrency, rateLimit)
    }
}

// 配置数据类
data class ProviderConfig(
    val type: ProviderType,
    val apiKey: String,
    val model: String,
    val baseUrl: String? = null
)

data class ResilienceConfig(
    val retry: RetryConfig?,
    val circuitBreaker: CircuitBreakerConfig?,
    val timeout: Duration?
)

data class RetryConfig(
    val maxAttempts: Int,
    val backoff: BackoffStrategy
)

data class CircuitBreakerConfig(
    val failureThreshold: Int,
    val resetTimeout: Duration
)

data class ContextConfig(
    val maxTokens: Int?,
    val strategy: ContextStrategy,
    val summarizer: ((List<Message>) -> String)?
)

data class StreamConfig(val enabled: Boolean)

data class ToolsConfig(
    val functions: List<FunctionTool>,
    val tools: List<Tool>
)

data class BatchConfig(
    val concurrency: Int,
    val rateLimit: RateLimit?
)

data class ResponseFormatConfig(val type: kotlin.reflect.KClass<*>)

data class RateLimit(val requests: Int, val per: Duration)

// 枚举和策略类
enum class ContextStrategy {
    SLIDING_WINDOW,
    SUMMARIZE,
    TRUNCATE
}

sealed class BackoffStrategy {
    data class Fixed(val delay: Duration) : BackoffStrategy()
    data class Exponential(val initialDelay: Duration, val maxDelay: Duration = Duration.INFINITE) : BackoffStrategy()
    data class Linear(val increment: Duration) : BackoffStrategy()
}

// 工具接口
interface Tool {
    val name: String
    suspend fun execute(input: String): String
}

data class FunctionTool(
    val name: String,
    val inputType: kotlin.reflect.KClass<*>,
    val outputType: kotlin.reflect.KClass<*>,
    val handler: suspend (Any) -> Any
)

// DSL入口函数
suspend fun llm(
    llmService: com.llmservice.service.LLMService,
    block: LLMBuilder.() -> Unit
): LLMExecution {
    val builder = LLMBuilder().apply(block)
    return LLMExecution(builder, llmService)
}

/**
 * LLM执行类 - 包装了所有配置并提供执行方法
 */
class LLMExecution(
    private val builder: LLMBuilder,
    private val llmService: com.llmservice.service.LLMService
) {
    private val executor = LLMExecutor(llmService, builder)
    
    suspend fun ask(prompt: String): Any {
        return executor.ask(prompt)
    }
    
    suspend fun chat(block: ChatBuilder.() -> Unit): Any {
        val messages = ChatBuilder().apply(block).build()
        return executor.chat(messages)
    }
    
    fun stream(block: ChatBuilder.() -> Unit): Flow<String> {
        val messages = ChatBuilder().apply(block).build()
        return executor.streamChat(messages)
    }
    
    suspend fun <T> batch(items: List<T>, processor: suspend (T) -> String): List<String> {
        return executor.batch(items, processor)
    }
}

/**
 * 对话构建器
 */
class ChatBuilder {
    private val messages = mutableListOf<Message>()
    
    fun system(content: String) {
        messages.add(Message("system", content))
    }
    
    fun user(content: String) {
        messages.add(Message("user", content))
    }
    
    fun assistant(content: String) {
        messages.add(Message("assistant", content))
    }
    
    internal fun build(): List<Message> = messages.toList()
}