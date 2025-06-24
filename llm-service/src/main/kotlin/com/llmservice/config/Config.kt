package com.llmservice.config

data class Config(
    val openai: OpenAIConfig? = null,
    val anthropic: AnthropicConfig? = null,
    val baidu: BaiduConfig? = null,
    val alibaba: AlibabaConfig? = null,
    val server: ServerConfig = ServerConfig()
)

data class OpenAIConfig(
    val apiKey: String,
    val baseUrl: String = "https://api.openai.com/v1"
)

data class AnthropicConfig(
    val apiKey: String,
    val baseUrl: String = "https://api.anthropic.com/v1"
)

data class BaiduConfig(
    val apiKey: String,
    val secretKey: String,
    val baseUrl: String = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat"
)

data class AlibabaConfig(
    val apiKey: String,
    val baseUrl: String = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
)

data class ServerConfig(
    val port: Int = 8080,
    val host: String = "0.0.0.0"
)