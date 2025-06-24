package com.llmservice.dsl

import com.llmservice.provider.*
import com.llmservice.service.LLMService
import com.llmservice.service.LLMProvider
import com.llmservice.service.ProviderType
import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.plugins.logging.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.json.Json
import kotlinx.coroutines.runBlocking

/**
 * 独立的DSL运行器，不需要启动Web服务器
 * 直接使用Provider进行API调用
 */
object StandaloneDSLRunner {
    
    private val httpClient = HttpClient(CIO) {
        install(ContentNegotiation) {
            json(Json {
                prettyPrint = true
                isLenient = true
                ignoreUnknownKeys = true
            })
        }
        install(Logging) {
            level = LogLevel.INFO
        }
        install(io.ktor.client.plugins.HttpTimeout) {
            requestTimeoutMillis = 60000 // 60 seconds
            connectTimeoutMillis = 10000 // 10 seconds
            socketTimeoutMillis = 60000 // 60 seconds
        }
    }
    
    private val llmService = LLMService()
    
    init {
        // 初始化所有提供商
        initializeProviders()
    }
    
    private fun initializeProviders() {
        // DeepSeek
        llmService.registerProvider(
            ProviderType.DEEPSEEK,
            DeepSeekProvider(
                apiKey = "sk-325be9f2c5594c3cae07495b28817043",
                httpClient = httpClient
            )
        )
        
        // OpenRouter
        llmService.registerProvider(
            ProviderType.OPENROUTER,
            OpenRouterProvider(
                apiKey = "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",
                httpClient = httpClient
            )
        )
    }
    
    /**
     * 获取DSL提供商实例
     */
    fun deepseek(): LLMProvider {
        return llmService.getProvider(ProviderType.DEEPSEEK)
            ?: throw IllegalStateException("DeepSeek provider not initialized")
    }
    
    fun openrouter(): LLMProvider {
        return llmService.getProvider(ProviderType.OPENROUTER)
            ?: throw IllegalStateException("OpenRouter provider not initialized")
    }
    
    /**
     * 关闭资源
     */
    fun close() {
        httpClient.close()
    }
}

/**
 * 全局DSL工厂函数
 */
fun deepseek(): LLMProvider = StandaloneDSLRunner.deepseek()
fun openrouter(): LLMProvider = StandaloneDSLRunner.openrouter()