package com.llmservice.service

import com.llmservice.model.ChatRequest
import com.llmservice.model.ChatResponse
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope

class LLMService {
    private val providers = mutableMapOf<ProviderType, LLMProvider>()
    
    fun registerProvider(type: ProviderType, provider: LLMProvider) {
        providers[type] = provider
    }
    
    fun getProvider(type: ProviderType): LLMProvider? = providers[type]
    
    fun getSupportedModels(): Map<ProviderType, List<String>> {
        return providers.mapValues { it.value.supportedModels }
    }
    
    suspend fun chat(providerType: ProviderType, request: ChatRequest): ChatResponse {
        val provider = providers[providerType] 
            ?: throw IllegalArgumentException("Provider $providerType not registered")
        
        if (!provider.isModelSupported(request.model)) {
            throw IllegalArgumentException("Model ${request.model} not supported by provider ${provider.name}")
        }
        
        return provider.chat(request)
    }
    
    suspend fun chatMultiple(
        providers: List<ProviderType>, 
        request: ChatRequest
    ): Map<ProviderType, Result<ChatResponse>> = coroutineScope {
        providers.map { providerType ->
            async {
                providerType to runCatching { chat(providerType, request) }
            }
        }.awaitAll().toMap()
    }
}