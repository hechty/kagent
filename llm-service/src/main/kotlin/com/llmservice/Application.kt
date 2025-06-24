package com.llmservice

import com.llmservice.model.*
import com.llmservice.provider.*
import com.llmservice.service.LLMService
import com.llmservice.service.ProviderType
import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.plugins.logging.*
import io.ktor.client.plugins.*
import kotlin.time.Duration.Companion.seconds
import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.serialization.json.Json

fun main() {
    embeddedServer(Netty, port = 8080, host = "0.0.0.0") {
        configureRouting()
    }.start(wait = true)
}

fun Application.configureRouting() {
    this.install(ContentNegotiation) {
        json(Json {
            prettyPrint = true
            isLenient = true
            ignoreUnknownKeys = true
        })
    }
    
    val httpClient = HttpClient(CIO) {
        install(io.ktor.client.plugins.contentnegotiation.ContentNegotiation) {
            json(Json {
                prettyPrint = true
                isLenient = true
                ignoreUnknownKeys = true
            })
        }
        install(io.ktor.client.plugins.logging.Logging) {
            level = LogLevel.INFO
        }
        
        // 改进1: 添加合理的超时配置
        install(HttpTimeout) {
            requestTimeoutMillis = 90_000  // 90秒，适合复杂LLM请求
            connectTimeoutMillis = 10_000  // 10秒连接超时
            socketTimeoutMillis = 90_000   // 90秒数据传输超时
        }
        
        // 改进2: 配置重试机制
        install(HttpRequestRetry) {
            retryOnServerErrors(maxRetries = 2)
            exponentialDelay()
        }
    }
    
    val llmService = LLMService()
    
    // 注册提供商
    llmService.registerProvider(
        ProviderType.DEEPSEEK,
        DeepSeekProvider(
            apiKey = "sk-325be9f2c5594c3cae07495b28817043",
            httpClient = httpClient
        )
    )
    
    llmService.registerProvider(
        ProviderType.OPENROUTER,
        OpenRouterProvider(
            apiKey = "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",
            httpClient = httpClient
        )
    )
    
    routing {
        get("/") {
            call.respondText("LLM Service is running!")
        }
        
        get("/health") {
            call.respondText("OK")
        }
        
        get("/models") {
            call.respond(llmService.getSupportedModels())
        }
        
        post("/chat/{provider}") {
            val providerParam = call.parameters["provider"]
            val providerType = try {
                ProviderType.valueOf(providerParam?.uppercase() ?: "")
            } catch (e: IllegalArgumentException) {
                call.respond(mapOf(
                    "error" to "Invalid provider: $providerParam",
                    "error_type" to "INVALID_PROVIDER",
                    "available_providers" to ProviderType.values().map { it.name }
                ))
                return@post
            }
            
            try {
                val request = call.receive<ChatRequest>()
                val response = llmService.chat(providerType, request)
                call.respond(response)
            } catch (e: Exception) {
                // 改进3: 更好的错误分类和处理
                val errorResponse = when {
                    e.message?.contains("timeout", ignoreCase = true) == true -> mapOf(
                        "error" to "Request timeout - the model is taking too long to respond",
                        "error_type" to "TIMEOUT",
                        "suggestion" to "Try a simpler prompt or use a faster model",
                        "original_error" to e.message
                    )
                    e.message?.contains("401", ignoreCase = true) == true -> mapOf(
                        "error" to "Authentication failed - check your API key",
                        "error_type" to "AUTH_ERROR",
                        "suggestion" to "Verify your API key is correct and has sufficient credits"
                    )
                    e.message?.contains("429", ignoreCase = true) == true -> mapOf(
                        "error" to "Rate limit exceeded",
                        "error_type" to "RATE_LIMIT",
                        "suggestion" to "Wait a moment and try again"
                    )
                    else -> mapOf(
                        "error" to (e.message ?: "Unknown error occurred"),
                        "error_type" to "UNKNOWN",
                        "suggestion" to "Check your request format and try again"
                    )
                }
                call.respond(errorResponse)
            }
        }
        
        post("/chat/multiple") {
            try {
                val request = call.receive<ChatRequest>()
                val providers = listOf(ProviderType.DEEPSEEK, ProviderType.OPENROUTER)
                val responses = llmService.chatMultiple(providers, request)
                
                val results = responses.mapValues { (_, result) ->
                    result.fold(
                        onSuccess = { ChatResponseResult.Success(it) },
                        onFailure = { ChatResponseResult.Error(it.message ?: "Unknown error") }
                    )
                }.mapKeys { it.key.name }
                
                call.respond(MultipleProviderResponse(results))
            } catch (e: Exception) {
                call.respond(mapOf("error" to e.message))
            }
        }
    }
}