package com.llmservice.provider

import com.llmservice.model.*
import com.llmservice.service.LLMProvider
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.http.*
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

class OpenAIProvider(
    private val apiKey: String,
    private val baseUrl: String = "https://api.openai.com/v1",
    private val httpClient: HttpClient
) : LLMProvider {
    
    override val name: String = "OpenAI"
    override val supportedModels: List<String> = listOf(
        "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini",
        "gpt-3.5-turbo", "gpt-3.5-turbo-16k"
    )
    
    @Serializable
    private data class OpenAIRequest(
        val model: String,
        val messages: List<OpenAIMessage>,
        val temperature: Double = 0.7,
        @SerialName("max_tokens") val maxTokens: Int? = null,
        val stream: Boolean = false
    )
    
    @Serializable
    private data class OpenAIMessage(
        val role: String,
        val content: String
    )
    
    @Serializable
    private data class OpenAIResponse(
        val id: String,
        val choices: List<OpenAIChoice>,
        val usage: OpenAIUsage? = null
    )
    
    @Serializable
    private data class OpenAIChoice(
        val index: Int,
        val message: OpenAIMessage,
        @SerialName("finish_reason") val finishReason: String? = null
    )
    
    @Serializable
    private data class OpenAIUsage(
        @SerialName("prompt_tokens") val promptTokens: Int,
        @SerialName("completion_tokens") val completionTokens: Int,
        @SerialName("total_tokens") val totalTokens: Int
    )
    
    override suspend fun chat(request: ChatRequest): ChatResponse {
        val openaiRequest = OpenAIRequest(
            model = request.model,
            messages = request.messages.map { OpenAIMessage(it.role, it.content) },
            temperature = request.temperature,
            maxTokens = request.maxTokens,
            stream = request.stream
        )
        
        val response = httpClient.post("$baseUrl/chat/completions") {
            contentType(ContentType.Application.Json)
            header("Authorization", "Bearer $apiKey")
            setBody(openaiRequest)
        }
        
        val openaiResponse = response.body<OpenAIResponse>()
        
        return ChatResponse(
            id = openaiResponse.id,
            choices = openaiResponse.choices.map { choice ->
                Choice(
                    index = choice.index,
                    message = Message(choice.message.role, choice.message.content),
                    finishReason = choice.finishReason
                )
            },
            usage = openaiResponse.usage?.let { usage ->
                Usage(
                    promptTokens = usage.promptTokens,
                    completionTokens = usage.completionTokens,
                    totalTokens = usage.totalTokens
                )
            }
        )
    }
}