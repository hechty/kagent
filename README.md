# LLM Service Multi-Module Project

A Kotlin-based multi-module project for integrating with multiple Large Language Model (LLM) providers.

## 📁 Project Structure

```
├── llm-dsl-core/           # DSL核心模块 - 提供DSL语法和基础功能
├── llm-service/            # 服务模块 - HTTP API和服务层
├── docs/                   # 📖 项目文档
│   ├── design/            # 设计文档
│   ├── guides/            # 使用指南  
│   └── tutorials/         # 教程和练习
└── build.gradle.kts       # 根项目构建配置
```

## 模块说明

### llm-dsl-core 模块
- **用途**: 独立的DSL核心功能模块
- **包含**: DSL实现、数据模型、服务接口、提供商实现
- **特点**: 
  - ✅ 可独立测试和开发
  - ✅ 包含完整的DSL功能
  - ✅ 支持多种LLM提供商
  - ✅ 提供流式和批量处理能力

### llm-service 模块  
- **用途**: 基于DSL的Web服务和高级功能
- **依赖**: llm-dsl-core模块
- **包含**: HTTP服务器、分析工具、示例代码

## 📖 文档

- **完整文档**: [docs/](docs/) 
- **服务API文档**: [llm-service/README.md](llm-service/README.md)
- **DSL使用指南**: [docs/guides/usage-guide.md](docs/guides/usage-guide.md)

## 🚀 Quick Start

### 构建整个项目
```bash
./gradlew build
```

### 运行服务
```bash
./gradlew :llm-service:run
```

### 运行DSL测试
```bash
./gradlew :llm-dsl-core:runDSLTest
```

## DSL使用示例

```kotlin
// 基础用法
val result = deepseek("your-api-key") {
    temperature = 0.8
    maxTokens = 1000
}.chat("Hello, how are you?")

// 高级用法
val llm = llm {
    provider {
        type = ProviderType.DEEPSEEK
        apiKey = "your-api-key"
        model = "deepseek-chat"
    }
    resilience {
        retryAttempts = 3
        timeout = 30.seconds
    }
}
```

## 优势

1. **模块化设计**: DSL功能完全独立，便于单独测试和改进
2. **独立开发**: DSL模块可以独立于Web服务进行开发
3. **易于测试**: DSL功能有专门的测试任务和测试套件
4. **清晰分离**: 业务逻辑和Web服务功能分离
5. **复用性强**: DSL模块可以被其他项目复用

## 环境配置

- **Java**: OpenJDK 21
- **Kotlin**: 2.1.0  
- **Gradle**: 8.13
- **框架**: Ktor 2.3.5

## API密钥配置

参考 `llm-keys.md` 文件配置你的API密钥。