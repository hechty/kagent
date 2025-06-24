package com.llmservice.dsl

import com.llmservice.model.*
import com.llmservice.service.LLMService
import com.llmservice.service.ProviderType
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.serialization.json.Json
import kotlin.time.Duration
import kotlin.time.Duration.Companion.seconds
import kotlin.time.Duration.Companion.milliseconds
import kotlin.math.pow

/**
 * LLM执行器 - 负责实际执行DSL配置的逻辑
 */
class LLMExecutor(
    private val llmService: LLMService,
    private val config: LLMBuilder
) {
    
    /**
     * 执行单次询问
     */
    suspend fun ask(prompt: String): Any {
        val messages = listOf(Message("user", prompt))
        return executeChat(messages)
    }
    
    /**
     * 执行对话
     */
    suspend fun chat(messages: List<Message>): Any {
        return executeChat(messages)
    }
    
    /**
     * 执行流式响应
     */
    fun streamChat(messages: List<Message>): Flow<String> = flow {
        if (config.streamConfig?.enabled != true) {
            // 如果没有启用流式，就模拟流式响应
            val response = executeChat(messages)
            if (response is ChatResponse) {
                response.choices.firstOrNull()?.message?.content?.let { content ->
                    content.chunked(10).forEach { chunk ->
                        emit(chunk)
                        delay(50) // 模拟流式延迟
                    }
                }
            }
        } else {
            // TODO: 实现真正的流式响应
            emit("流式响应功能待实现")
        }
    }
    
    /**
     * 批量处理
     */
    suspend fun <T> batch(items: List<T>, processor: suspend (T) -> String): List<String> = coroutineScope {
        val batchConfig = config.batchConfig ?: BatchConfig(concurrency = 1, rateLimit = null)
        val semaphore = Semaphore(batchConfig.concurrency)
        
        items.map { item: T ->
            async {
                semaphore.withPermit {
                    // 应用速率限制
                    batchConfig.rateLimit?.let { rateLimit ->
                        delay(rateLimit.per.inWholeMilliseconds / rateLimit.requests)
                    }
                    
                    withRetry(config.resilienceConfig?.retry) {
                        processor(item)
                    }
                }
            }
        }.awaitAll()
    }
    
    /**
     * 核心聊天执行逻辑
     */
    private suspend fun executeChat(messages: List<Message>): Any {
        val processedMessages = processContextWindow(messages)
        val request = buildChatRequest(processedMessages)
        
        return withRetry(config.resilienceConfig?.retry) {
            withTimeout(config.resilienceConfig?.timeout ?: 60.seconds) {
                executeChatWithFallback(request)
            }
        }
    }
    
    /**
     * 处理上下文窗口
     */
    private fun processContextWindow(messages: List<Message>): List<Message> {
        val contextConfig = config.contextConfig ?: return messages
        
        // 简单的token估算（实际应该使用tokenizer）
        val estimatedTokens = messages.sumOf { it.content.length / 4 }
        val maxTokens = contextConfig.maxTokens ?: return messages
        
        if (estimatedTokens <= maxTokens) return messages
        
        return when (contextConfig.strategy) {
            ContextStrategy.TRUNCATE -> {
                messages.takeLast(maxTokens / (estimatedTokens / messages.size))
            }
            ContextStrategy.SLIDING_WINDOW -> {
                // 保留系统消息和最新的消息
                val systemMessages = messages.filter { it.role == "system" }
                val otherMessages = messages.filter { it.role != "system" }
                val recentMessages = otherMessages.takeLast(maxTokens / (estimatedTokens / messages.size) - systemMessages.size)
                systemMessages + recentMessages
            }
            ContextStrategy.SUMMARIZE -> {
                contextConfig.summarizer?.let { summarizer ->
                    val summary = summarizer(messages.dropLast(5))
                    listOf(Message("system", "之前对话摘要: $summary")) + messages.takeLast(5)
                } ?: messages.takeLast(maxTokens / (estimatedTokens / messages.size))
            }
        }
    }
    
    /**
     * 构建ChatRequest
     */
    private fun buildChatRequest(messages: List<Message>): ChatRequest {
        val primaryProvider = config.primaryProvider 
            ?: throw IllegalStateException("Primary provider must be configured")
            
        return ChatRequest(
            model = primaryProvider.model,
            messages = messages,
            stream = config.streamConfig?.enabled ?: false
        )
    }
    
    /**
     * 执行聊天请求（含回退逻辑）
     */
    private suspend fun executeChatWithFallback(request: ChatRequest): Any {
        val primaryProvider = config.primaryProvider!!
        
        try {
            val response = llmService.chat(primaryProvider.type, request)
            return processResponse(response)
        } catch (e: Exception) {
            // 尝试回退提供商
            for (fallbackProvider in config.fallbackProviders) {
                try {
                    val fallbackRequest = request.copy(model = fallbackProvider.model)
                    val response = llmService.chat(fallbackProvider.type, fallbackRequest)
                    return processResponse(response)
                } catch (fallbackException: Exception) {
                    // 继续尝试下一个回退提供商
                    continue
                }
            }
            
            // 所有提供商都失败了
            throw LLMExecutionException("All providers failed", e)
        }
    }
    
    /**
     * 处理响应（包括类型转换）
     */
    private fun processResponse(response: ChatResponse): Any {
        val responseFormat = config.responseFormat
        if (responseFormat != null) {
            // 尝试将响应转换为指定类型
            val content = response.choices.firstOrNull()?.message?.content
                ?: throw LLMExecutionException("No response content")
                
            return try {
                // 这里需要根据实际类型进行JSON反序列化
                // 暂时返回原始内容
                content
            } catch (e: Exception) {
                throw LLMExecutionException("Failed to parse response as ${responseFormat.type.simpleName}", e)
            }
        }
        
        return response
    }
    
    /**
     * 重试机制
     */
    private suspend fun <T> withRetry(
        retryConfig: RetryConfig?,
        operation: suspend () -> T
    ): T {
        if (retryConfig == null) {
            return operation()
        }
        
        var lastException: Exception? = null
        
        repeat(retryConfig.maxAttempts) { attempt ->
            try {
                return operation()
            } catch (e: Exception) {
                lastException = e
                
                if (attempt < retryConfig.maxAttempts - 1) {
                    val delay = when (val backoff = retryConfig.backoff) {
                        is BackoffStrategy.Fixed -> backoff.delay
                        is BackoffStrategy.Exponential -> {
                            val delayMs = backoff.initialDelay.inWholeMilliseconds * 2.0.pow(attempt).toLong()
                            minOf(delayMs.milliseconds, backoff.maxDelay)
                        }
                        is BackoffStrategy.Linear -> backoff.increment * (attempt + 1)
                    }
                    delay(delay)
                }
            }
        }
        
        throw lastException ?: RuntimeException("Retry failed")
    }
}

/**
 * LLM执行异常
 */
class LLMExecutionException(message: String, cause: Throwable? = null) : Exception(message, cause)