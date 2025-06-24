package com.llmservice.service

import com.llmservice.model.ChatRequest
import com.llmservice.model.ChatResponse

interface LLMProvider {
    val name: String
    val supportedModels: List<String>
    
    suspend fun chat(request: ChatRequest): ChatResponse
    fun isModelSupported(model: String): Boolean = supportedModels.contains(model)
}

enum class ProviderType {
    OPENAI,
    ANTHROPIC,
    GOOGLE,
    AZURE,
    ALIBABA,
    BAIDU,
    ZHIPU,
    DEEPSEEK,
    OPENROUTER
}