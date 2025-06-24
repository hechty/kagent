package com.llmservice.provider

import com.llmservice.model.*
import com.llmservice.service.LLMProvider
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.http.*
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

class AlibabaProvider(
    private val apiKey: String,
    private val baseUrl: String = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
    private val httpClient: HttpClient
) : LLMProvider {
    
    override val name: String = "Alibaba"
    override val supportedModels: List<String> = listOf(
        "qwen-turbo", "qwen-plus", "qwen-max", "qwen-max-1201", 
        "qwen-max-longcontext", "qwen2-72b-instruct", "qwen2-57b-a14b-instruct",
        "qwen2-7b-instruct", "qwen2-1.5b-instruct", "qwen2-0.5b-instruct"
    )
    
    @Serializable
    private data class AlibabaRequest(
        val model: String,
        val input: AlibabaInput,
        val parameters: AlibabaParameters? = null
    )
    
    @Serializable
    private data class AlibabaInput(
        val messages: List<AlibabaMessage>
    )
    
    @Serializable
    private data class AlibabaMessage(
        val role: String,
        val content: String
    )
    
    @Serializable
    private data class AlibabaParameters(
        val temperature: Double = 0.7,
        @SerialName("max_tokens") val maxTokens: Int? = null,
        val stream: Boolean = false
    )
    
    @Serializable
    private data class AlibabaResponse(
        @SerialName("request_id") val requestId: String,
        val output: AlibabaOutput,
        val usage: AlibabaUsage? = null
    )
    
    @Serializable
    private data class AlibabaOutput(
        val text: String,
        @SerialName("finish_reason") val finishReason: String? = null
    )
    
    @Serializable
    private data class AlibabaUsage(
        @SerialName("input_tokens") val inputTokens: Int,
        @SerialName("output_tokens") val outputTokens: Int,
        @SerialName("total_tokens") val totalTokens: Int
    )
    
    override suspend fun chat(request: ChatRequest): ChatResponse {
        val alibabaRequest = AlibabaRequest(
            model = request.model,
            input = AlibabaInput(
                messages = request.messages.map { AlibabaMessage(it.role, it.content) }
            ),
            parameters = AlibabaParameters(
                temperature = request.temperature,
                maxTokens = request.maxTokens,
                stream = request.stream
            )
        )
        
        val response = httpClient.post(baseUrl) {
            contentType(ContentType.Application.Json)
            header("Authorization", "Bearer $apiKey")
            setBody(alibabaRequest)
        }
        
        val alibabaResponse = response.body<AlibabaResponse>()
        
        return ChatResponse(
            id = alibabaResponse.requestId,
            choices = listOf(
                Choice(
                    index = 0,
                    message = Message("assistant", alibabaResponse.output.text),
                    finishReason = alibabaResponse.output.finishReason
                )
            ),
            usage = alibabaResponse.usage?.let { usage ->
                Usage(
                    promptTokens = usage.inputTokens,
                    completionTokens = usage.outputTokens,
                    totalTokens = usage.totalTokens
                )
            }
        )
    }
}