package com.llmservice.provider

import com.llmservice.model.*
import com.llmservice.service.LLMProvider
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.http.*
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

class DeepSeekProvider(
    private val apiKey: String,
    private val baseUrl: String = "https://api.deepseek.com/v1",
    private val httpClient: HttpClient
) : LLMProvider {
    
    override val name: String = "DeepSeek"
    override val supportedModels: List<String> = listOf(
        "deepseek-chat", "deepseek-reasoner"
    )
    
    @Serializable
    private data class DeepSeekRequest(
        val model: String,
        val messages: List<DeepSeekMessage>,
        val temperature: Double = 0.7,
        @SerialName("max_tokens") val maxTokens: Int? = null,
        val stream: Boolean = false
    )
    
    @Serializable
    private data class DeepSeekMessage(
        val role: String,
        val content: String
    )
    
    @Serializable
    private data class DeepSeekResponse(
        val id: String,
        val choices: List<DeepSeekChoice>,
        val usage: DeepSeekUsage? = null
    )
    
    @Serializable
    private data class DeepSeekChoice(
        val index: Int,
        val message: DeepSeekMessage,
        @SerialName("finish_reason") val finishReason: String? = null
    )
    
    @Serializable
    private data class DeepSeekUsage(
        @SerialName("prompt_tokens") val promptTokens: Int,
        @SerialName("completion_tokens") val completionTokens: Int,
        @SerialName("total_tokens") val totalTokens: Int
    )
    
    override suspend fun chat(request: ChatRequest): ChatResponse {
        val deepSeekRequest = DeepSeekRequest(
            model = request.model,
            messages = request.messages.map { DeepSeekMessage(it.role, it.content) },
            temperature = request.temperature,
            maxTokens = request.maxTokens,
            stream = request.stream
        )
        
        val response = httpClient.post("$baseUrl/chat/completions") {
            contentType(ContentType.Application.Json)
            header("Authorization", "Bearer $apiKey")
            setBody(deepSeekRequest)
        }
        
        val deepSeekResponse = response.body<DeepSeekResponse>()
        
        return ChatResponse(
            id = deepSeekResponse.id,
            choices = deepSeekResponse.choices.map { choice ->
                Choice(
                    index = choice.index,
                    message = Message(choice.message.role, choice.message.content),
                    finishReason = choice.finishReason
                )
            },
            usage = deepSeekResponse.usage?.let { usage ->
                Usage(
                    promptTokens = usage.promptTokens,
                    completionTokens = usage.completionTokens,
                    totalTokens = usage.totalTokens
                )
            }
        )
    }
}