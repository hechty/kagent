package com.llmservice.provider

import com.llmservice.model.*
import com.llmservice.service.LLMProvider
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.http.*
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

class BaiduProvider(
    private val apiKey: String,
    private val secretKey: String,
    private val baseUrl: String = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat",
    private val httpClient: HttpClient
) : LLMProvider {
    
    override val name: String = "Baidu"
    override val supportedModels: List<String> = listOf(
        "ernie-4.0-8k", "ernie-4.0-8k-preview", "ernie-3.5-8k", 
        "ernie-3.5-8k-preview", "ernie-speed-8k", "ernie-speed-128k",
        "ernie-lite-8k", "ernie-tiny-8k"
    )
    
    @Serializable
    private data class BaiduRequest(
        val messages: List<BaiduMessage>,
        val temperature: Double = 0.7,
        @SerialName("max_output_tokens") val maxOutputTokens: Int? = null,
        val stream: Boolean = false
    )
    
    @Serializable
    private data class BaiduMessage(
        val role: String,
        val content: String
    )
    
    @Serializable
    private data class BaiduResponse(
        val id: String,
        val result: String,
        val usage: BaiduUsage? = null,
        @SerialName("finish_reason") val finishReason: String? = null
    )
    
    @Serializable
    private data class BaiduUsage(
        @SerialName("prompt_tokens") val promptTokens: Int,
        @SerialName("completion_tokens") val completionTokens: Int,
        @SerialName("total_tokens") val totalTokens: Int
    )
    
    @Serializable
    private data class TokenResponse(
        @SerialName("access_token") val accessToken: String,
        @SerialName("expires_in") val expiresIn: Int
    )
    
    private suspend fun getAccessToken(): String {
        val response = httpClient.post("https://aip.baidubce.com/oauth/2.0/token") {
            parameter("grant_type", "client_credentials")
            parameter("client_id", apiKey)
            parameter("client_secret", secretKey)
        }
        return response.body<TokenResponse>().accessToken
    }
    
    override suspend fun chat(request: ChatRequest): ChatResponse {
        val accessToken = getAccessToken()
        
        val baiduRequest = BaiduRequest(
            messages = request.messages.map { BaiduMessage(it.role, it.content) },
            temperature = request.temperature,
            maxOutputTokens = request.maxTokens,
            stream = request.stream
        )
        
        val modelEndpoint = when (request.model) {
            "ernie-4.0-8k" -> "completions_pro"
            "ernie-3.5-8k" -> "completions"
            "ernie-speed-8k" -> "ernie_speed"
            "ernie-lite-8k" -> "eb-instant"
            "ernie-tiny-8k" -> "ernie-tiny-8k"
            else -> "completions"
        }
        
        val response = httpClient.post("$baseUrl/$modelEndpoint") {
            contentType(ContentType.Application.Json)
            parameter("access_token", accessToken)
            setBody(baiduRequest)
        }
        
        val baiduResponse = response.body<BaiduResponse>()
        
        return ChatResponse(
            id = baiduResponse.id,
            choices = listOf(
                Choice(
                    index = 0,
                    message = Message("assistant", baiduResponse.result),
                    finishReason = baiduResponse.finishReason
                )
            ),
            usage = baiduResponse.usage?.let { usage ->
                Usage(
                    promptTokens = usage.promptTokens,
                    completionTokens = usage.completionTokens,
                    totalTokens = usage.totalTokens
                )
            }
        )
    }
}