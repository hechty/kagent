# LLM Service

A Kotlin-based service for integrating with multiple Large Language Model (LLM) providers.

## Supported Providers

- **OpenAI**: GPT-4, GPT-3.5 series
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus/Sonnet/Haiku
- **Baidu**: ERNIE 4.0/3.5/Speed/Lite/Tiny series
- **Alibaba**: Qwen Turbo/Plus/Max series

## Features

- Unified API for multiple LLM providers
- Async/coroutine support
- Multiple provider chat (parallel requests)
- Type-safe request/response models
- Configurable timeouts and retry logic

## Quick Start

### Build and Run

```bash
cd code/llm-service
./gradlew build
./gradlew run
```

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Get Supported Models
```bash
GET /models
```

#### Chat with Single Provider
```bash
POST /chat/{provider}
Content-Type: application/json

{
  "model": "gpt-4",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7
}
```

#### Chat with Multiple Providers
```bash
POST /chat/multiple
Content-Type: application/json

{
  "model": "gpt-4",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ]
}
```

## Configuration

Set environment variables or update the config:

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export BAIDU_API_KEY="your-baidu-key"
export BAIDU_SECRET_KEY="your-baidu-secret"
export ALIBABA_API_KEY="your-alibaba-key"
```

## Project Structure

```
src/main/kotlin/com/llmservice/
├── Application.kt          # Main application
├── config/
│   └── Config.kt          # Configuration classes
├── model/
│   └── ChatRequest.kt     # Request/Response models
├── provider/              # LLM provider implementations
│   ├── OpenAIProvider.kt
│   ├── AnthropicProvider.kt
│   ├── BaiduProvider.kt
│   └── AlibabaProvider.kt
└── service/
    ├── LLMProvider.kt     # Provider interface
    └── LLMService.kt      # Main service class
```

## Technology Stack

- **Kotlin 2.1.0** - Modern JVM language
- **Ktor** - HTTP client/server framework
- **Kotlinx Serialization** - JSON serialization
- **Coroutines** - Async programming
- **Gradle** - Build system