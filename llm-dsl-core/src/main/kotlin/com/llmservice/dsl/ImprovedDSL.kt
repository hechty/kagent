package com.llmservice.dsl

import com.llmservice.config.DSLConfig
import com.llmservice.config.EnvironmentDetector
import com.llmservice.model.*
import com.llmservice.service.LLMProvider
import com.llmservice.provider.*
import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.plugins.logging.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.coroutines.*
import kotlinx.serialization.json.Json
import kotlin.time.Duration

/**
 * 改进的LLM DSL - 基于实际使用问题的优化版本
 * 
 * 主要改进：
 * 1. 智能超时配置
 * 2. 更好的错误处理和重试
 * 3. 环境感知配置
 * 4. 代理冲突检测
 * 5. 详细的错误信息
 */

// ========================================
// 1. 改进的配置管理
// ========================================

/**
 * DSL异常类 - 提供更好的错误信息
 */
sealed class DSLException(message: String, cause: Throwable? = null) : Exception(message, cause) {
    class TimeoutException(val timeoutDuration: Duration, cause: Throwable? = null) : 
        DSLException("Request timed out after $timeoutDuration. Try using a simpler prompt or check your connection.", cause)
    
    class AuthenticationException(val provider: String, cause: Throwable? = null) : 
        DSLException("Authentication failed for $provider. Please check your API key.", cause)
    
    class RateLimitException(val provider: String, cause: Throwable? = null) : 
        DSLException("Rate limit exceeded for $provider. Please wait and try again.", cause)
    
    class ModelNotSupportedException(val model: String, val provider: String) : 
        DSLException("Model '$model' is not supported by provider '$provider'")
    
    class NetworkException(message: String, cause: Throwable? = null) : 
        DSLException("Network error: $message", cause)
        
    class ConfigurationException(message: String) : 
        DSLException("Configuration error: $message")
}

/**
 * DSL结果类 - 包含成功结果或详细错误信息
 */
sealed class DSLResult<T> {
    data class Success<T>(val data: T, val metadata: DSLMetadata) : DSLResult<T>()
    data class Failure<T>(val error: DSLException, val metadata: DSLMetadata) : DSLResult<T>()
    
    fun getOrThrow(): T = when (this) {
        is Success -> data
        is Failure -> throw error
    }
    
    fun getOrNull(): T? = when (this) {
        is Success -> data
        is Failure -> null
    }
}

/**
 * DSL元数据 - 包含执行信息
 */
data class DSLMetadata(
    val executionTime: Duration,
    val provider: String,
    val model: String,
    val tokenUsage: Usage? = null,
    val retryCount: Int = 0,
    val warnings: List<String> = emptyList()
)

// ========================================
// 2. 改进的Provider工厂
// ========================================

/**
 * 智能HTTP客户端创建 - 根据配置优化
 */
private fun createOptimizedHttpClient(config: DSLConfig): HttpClient {
    return HttpClient(CIO) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                isLenient = true
            })
        }
        
        if (config.enableDetailedErrors) {
            install(Logging) {
                level = LogLevel.INFO
            }
        }
        
        // 改进5: 智能超时配置
        install(HttpTimeout) {
            requestTimeoutMillis = config.requestTimeout.inWholeMilliseconds
            connectTimeoutMillis = config.connectTimeout.inWholeMilliseconds
            socketTimeoutMillis = config.socketTimeout.inWholeMilliseconds
        }
        
        // 改进6: 智能重试机制
        if (config.maxRetries > 0) {
            install(HttpRequestRetry) {
                retryOnServerErrors(maxRetries = config.maxRetries)
                exponentialDelay()
                if (config.retryOnTimeout) {
                    retryOnExceptionIf { _, cause ->
                        cause is kotlinx.coroutines.TimeoutCancellationException
                    }
                }
            }
        }
    }
}

/**
 * 改进的DeepSeek提供商创建
 */
fun optimizedDeepseek(
    apiKey: String, 
    model: String = "deepseek-chat", 
    config: DSLConfig = EnvironmentDetector.getRecommendedConfig()
): LLMProvider {
    val httpClient = createOptimizedHttpClient(config)
    return DeepSeekProvider(apiKey, httpClient = httpClient)
}

/**
 * 改进的OpenRouter提供商创建  
 */
fun optimizedOpenrouter(
    apiKey: String, 
    model: String = "google/gemini-2.5-pro", 
    config: DSLConfig = EnvironmentDetector.getRecommendedConfig()
): LLMProvider {
    val httpClient = createOptimizedHttpClient(config)
    return OpenRouterProvider(apiKey, httpClient = httpClient)
}

// ========================================
// 3. 改进的核心DSL函数
// ========================================

/**
 * 改进的ask函数 - 返回DSLResult而不是直接抛异常
 */
suspend infix fun String.askSafely(provider: LLMProvider): DSLResult<String> {
    val startTime = System.currentTimeMillis()
    var retryCount = 0
    val warnings = mutableListOf<String>()
    
    // 环境检查
    if (EnvironmentDetector.hasProxyConflict()) {
        warnings.add(EnvironmentDetector.getProxyAdvice())
    }
    
    return try {
        val request = ChatRequest(
            model = provider.supportedModels.firstOrNull() ?: "default",
            messages = listOf(Message("user", this))
        )
        
        val response = provider.chat(request)
        val executionTime = Duration.parse("${System.currentTimeMillis() - startTime}ms")
        
        DSLResult.Success(
            data = response.choices.first().message.content,
            metadata = DSLMetadata(
                executionTime = executionTime,
                provider = provider.name,
                model = request.model,
                tokenUsage = response.usage,
                retryCount = retryCount,
                warnings = warnings
            )
        )
    } catch (e: Exception) {
        val executionTime = Duration.parse("${System.currentTimeMillis() - startTime}ms")
        val dslException = when {
            e.message?.contains("timeout", ignoreCase = true) == true -> 
                DSLException.TimeoutException(Duration.parse("30s"), e)
            e.message?.contains("401", ignoreCase = true) == true -> 
                DSLException.AuthenticationException(provider.name, e)
            e.message?.contains("429", ignoreCase = true) == true -> 
                DSLException.RateLimitException(provider.name, e)
            else -> DSLException.NetworkException(e.message ?: "Unknown error", e)
        }
        
        DSLResult.Failure(
            error = dslException,
            metadata = DSLMetadata(
                executionTime = executionTime,
                provider = provider.name,
                model = "unknown",
                retryCount = retryCount,
                warnings = warnings
            )
        )
    }
}

/**
 * 改进的ask函数 - 使用新的API名称避免冲突
 */
suspend infix fun String.askWith(provider: LLMProvider): String {
    val result = this askSafely provider
    return result.getOrThrow()
}

/**
 * 改进的对话管理
 */
class ResilientConversation(
    private val provider: LLMProvider,
    private val config: DSLConfig = EnvironmentDetector.getRecommendedConfig()
) {
    private val messages = mutableListOf<Message>()
    private val executionHistory = mutableListOf<DSLMetadata>()
    
    fun system(content: String) {
        messages.add(Message("system", content))
    }
    
    suspend fun ask(content: String): DSLResult<String> {
        messages.add(Message("user", content))
        
        val result = try {
            val request = ChatRequest(
                model = provider.supportedModels.firstOrNull() ?: "default",
                messages = messages.toList(),
                temperature = config.defaultTemperature,
                maxTokens = config.defaultMaxTokens
            )
            
            val startTime = System.currentTimeMillis()
            val response = provider.chat(request)
            val executionTime = Duration.parse("${System.currentTimeMillis() - startTime}ms")
            
            val answer = response.choices.first().message.content
            messages.add(Message("assistant", answer))
            
            val metadata = DSLMetadata(
                executionTime = executionTime,
                provider = provider.name,
                model = request.model,
                tokenUsage = response.usage
            )
            executionHistory.add(metadata)
            
            DSLResult.Success(answer, metadata)
        } catch (e: Exception) {
            val metadata = DSLMetadata(
                executionTime = Duration.ZERO,
                provider = provider.name,
                model = "unknown"
            )
            executionHistory.add(metadata)
            
            DSLResult.Failure(
                DSLException.NetworkException(e.message ?: "Unknown error", e),
                metadata
            )
        }
        
        return result
    }
    
    val history: List<Message> get() = messages.toList()
    val stats: List<DSLMetadata> get() = executionHistory.toList()
}

/**
 * 创建弹性对话
 */
fun resilientConversation(
    provider: LLMProvider, 
    config: DSLConfig = EnvironmentDetector.getRecommendedConfig()
): ResilientConversation {
    return ResilientConversation(provider, config)
}

// ========================================
// 4. 诊断和调试工具
// ========================================

/**
 * DSL健康检查
 */
object DSLDiagnostics {
    suspend fun healthCheck(provider: LLMProvider): DSLResult<String> {
        return "Hello" askSafely provider
    }
    
    fun environmentReport(): String {
        return buildString {
            appendLine("=== DSL Environment Report ===")
            appendLine("Environment: ${EnvironmentDetector.detectEnvironment()}")
            appendLine("Recommended Config: ${EnvironmentDetector.getRecommendedConfig()}")
            appendLine("Proxy Status: ${EnvironmentDetector.getProxyAdvice()}")
            appendLine("Java Version: ${System.getProperty("java.version")}")
            appendLine("Available Processors: ${Runtime.getRuntime().availableProcessors()}")
        }
    }
    
    suspend fun performanceTest(provider: LLMProvider): Map<String, Any> {
        val results = mutableMapOf<String, Any>()
        
        // 简单请求测试
        val simpleStart = System.currentTimeMillis()
        val simpleResult = "Hello" askSafely provider
        val simpleTime = System.currentTimeMillis() - simpleStart
        
        results["simple_request_ms"] = simpleTime
        results["simple_success"] = simpleResult is DSLResult.Success
        
        // 复杂请求测试
        val complexStart = System.currentTimeMillis()
        val complexResult = "Explain quantum computing in 50 words" askSafely provider
        val complexTime = System.currentTimeMillis() - complexStart
        
        results["complex_request_ms"] = complexTime
        results["complex_success"] = complexResult is DSLResult.Success
        
        return results
    }
}

// ========================================
// 5. 便利函数和扩展
// ========================================

/**
 * 快速诊断函数
 */
suspend fun diagnoseDSL() {
    println(DSLDiagnostics.environmentReport())
}

/**
 * 默认提供商（用于快速测试）
 */
object QuickTest {
    suspend fun withDeepseek(apiKey: String, test: suspend (LLMProvider) -> Unit) {
        val provider = optimizedDeepseek(apiKey, config = DSLConfig.QUICK_TEST)
        test(provider)
    }
    
    suspend fun withGemini(apiKey: String, test: suspend (LLMProvider) -> Unit) {
        val provider = optimizedOpenrouter(apiKey, config = DSLConfig.QUICK_TEST)
        test(provider)
    }
}