package com.llmservice.provider

import com.llmservice.model.*
import com.llmservice.service.LLMProvider
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.http.*
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

class AnthropicProvider(
    private val apiKey: String,
    private val baseUrl: String = "https://api.anthropic.com/v1",
    private val httpClient: HttpClient
) : LLMProvider {
    
    override val name: String = "Anthropic"
    override val supportedModels: List<String> = listOf(
        "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", 
        "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
    )
    
    @Serializable
    private data class AnthropicRequest(
        val model: String,
        val messages: List<AnthropicMessage>,
        val temperature: Double = 0.7,
        @SerialName("max_tokens") val maxTokens: Int = 1000,
        val stream: Boolean = false
    )
    
    @Serializable
    private data class AnthropicMessage(
        val role: String,
        val content: String
    )
    
    @Serializable
    private data class AnthropicResponse(
        val id: String,
        val content: List<AnthropicContent>,
        val usage: AnthropicUsage? = null,
        @SerialName("stop_reason") val stopReason: String? = null
    )
    
    @Serializable
    private data class AnthropicContent(
        val type: String,
        val text: String
    )
    
    @Serializable
    private data class AnthropicUsage(
        @SerialName("input_tokens") val inputTokens: Int,
        @SerialName("output_tokens") val outputTokens: Int
    )
    
    override suspend fun chat(request: ChatRequest): ChatResponse {
        val anthropicRequest = AnthropicRequest(
            model = request.model,
            messages = request.messages.map { AnthropicMessage(it.role, it.content) },
            temperature = request.temperature,
            maxTokens = request.maxTokens ?: 1000,
            stream = request.stream
        )
        
        val response = httpClient.post("$baseUrl/messages") {
            contentType(ContentType.Application.Json)
            header("x-api-key", apiKey)
            header("anthropic-version", "2023-06-01")
            setBody(anthropicRequest)
        }
        
        val anthropicResponse = response.body<AnthropicResponse>()
        
        return ChatResponse(
            id = anthropicResponse.id,
            choices = listOf(
                Choice(
                    index = 0,
                    message = Message("assistant", anthropicResponse.content.first().text),
                    finishReason = anthropicResponse.stopReason
                )
            ),
            usage = anthropicResponse.usage?.let { usage ->
                Usage(
                    promptTokens = usage.inputTokens,
                    completionTokens = usage.outputTokens,
                    totalTokens = usage.inputTokens + usage.outputTokens
                )
            }
        )
    }
}