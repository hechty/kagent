package com.llmservice.provider

import com.llmservice.model.*
import com.llmservice.service.LLMProvider
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.http.*
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

class OpenRouterProvider(
    private val apiKey: String,
    private val baseUrl: String = "https://openrouter.ai/api/v1",
    private val httpClient: HttpClient
) : LLMProvider {
    
    override val name: String = "OpenRouter"
    override val supportedModels: List<String> = listOf(
        "openai/gpt-4.1", "google/gemini-2.5-pro", "anthropic/claude-sonnet-4",
        "minimax/minimax-m1", "google/gemini-2.5-flash-lite-preview-06-17"
    )
    
    @Serializable
    private data class OpenRouterRequest(
        val model: String,
        val messages: List<OpenRouterMessage>,
        val temperature: Double = 0.7,
        @SerialName("max_tokens") val maxTokens: Int? = null,
        val stream: Boolean = false
    )
    
    @Serializable
    private data class OpenRouterMessage(
        val role: String,
        val content: String
    )
    
    @Serializable
    private data class OpenRouterResponse(
        val id: String,
        val choices: List<OpenRouterChoice>,
        val usage: OpenRouterUsage? = null
    )
    
    @Serializable
    private data class OpenRouterChoice(
        val index: Int,
        val message: OpenRouterMessage,
        @SerialName("finish_reason") val finishReason: String? = null
    )
    
    @Serializable
    private data class OpenRouterUsage(
        @SerialName("prompt_tokens") val promptTokens: Int,
        @SerialName("completion_tokens") val completionTokens: Int,
        @SerialName("total_tokens") val totalTokens: Int
    )
    
    override suspend fun chat(request: ChatRequest): ChatResponse {
        val openRouterRequest = OpenRouterRequest(
            model = request.model,
            messages = request.messages.map { OpenRouterMessage(it.role, it.content) },
            temperature = request.temperature,
            maxTokens = request.maxTokens,
            stream = request.stream
        )
        
        val response = httpClient.post("$baseUrl/chat/completions") {
            contentType(ContentType.Application.Json)
            header("Authorization", "Bearer $apiKey")
            header("HTTP-Referer", "https://llm-service.local")
            header("X-Title", "LLM Service")
            setBody(openRouterRequest)
        }
        
        val openRouterResponse = response.body<OpenRouterResponse>()
        
        return ChatResponse(
            id = openRouterResponse.id,
            choices = openRouterResponse.choices.map { choice ->
                Choice(
                    index = choice.index,
                    message = Message(choice.message.role, choice.message.content),
                    finishReason = choice.finishReason
                )
            },
            usage = openRouterResponse.usage?.let { usage ->
                Usage(
                    promptTokens = usage.promptTokens,
                    completionTokens = usage.completionTokens,
                    totalTokens = usage.totalTokens
                )
            }
        )
    }
}