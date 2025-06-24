package com.llmservice.model

import kotlinx.serialization.Serializable

@Serializable
data class ChatRequest(
    val model: String,
    val messages: List<Message>,
    val temperature: Double = 0.7,
    val maxTokens: Int? = null,
    val stream: Boolean = false
)

@Serializable
data class Message(
    val role: String,
    val content: String
)

@Serializable
data class ChatResponse(
    val id: String,
    val choices: List<Choice>,
    val usage: Usage? = null
)

@Serializable
data class Choice(
    val index: Int,
    val message: Message,
    val finishReason: String? = null
)

@Serializable
data class Usage(
    val promptTokens: Int,
    val completionTokens: Int,
    val totalTokens: Int
)

@Serializable
data class MultipleProviderResponse(
    val results: Map<String, ChatResponseResult>
)

@Serializable
sealed class ChatResponseResult {
    @Serializable
    data class Success(val response: ChatResponse) : ChatResponseResult()
    
    @Serializable
    data class Error(val error: String) : ChatResponseResult()
}