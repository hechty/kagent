# LLM Service Multi-Module Project

这是一个基于Kotlin 2.1.0 + Ktor构建的多模块LLM服务项目，将DSL功能独立成一个单独的模块以便于测试和改进。

## 项目结构

```
llm-service-multi-module/
├── build.gradle.kts          # 根项目构建配置
├── settings.gradle.kts       # 多模块项目设置
├── llm-dsl-core/            # DSL核心模块 🎯
│   ├── build.gradle.kts     # DSL模块构建配置
│   └── src/
│       ├── main/kotlin/com/llmservice/
│       │   ├── dsl/         # DSL实现
│       │   ├── model/       # 共享数据模型
│       │   ├── service/     # 服务接口
│       │   ├── provider/    # LLM提供商实现
│       │   └── config/      # DSL配置
│       └── test/kotlin/     # DSL测试
└── llm-service/             # 主服务模块
    ├── build.gradle.kts     # 服务模块构建配置
    └── src/
        ├── main/kotlin/com/llmservice/
        │   ├── Application.kt    # 服务主入口
        │   ├── analysis/        # 分析工具
        │   ├── discussion/      # 讨论工具
        │   ├── examples/        # 使用示例
        │   └── execution/       # 执行引擎
        └── test/kotlin/         # 服务测试
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

## 构建和运行

### 构建整个项目
```bash
cd /root/code
/opt/gradle/bin/gradle build --init-script llm-service/init.gradle
```

### 运行DSL测试
```bash
# 运行DSL演示
/opt/gradle/bin/gradle :llm-dsl-core:runDSLDemo --init-script llm-service/init.gradle

# 运行DSL基础测试
/opt/gradle/bin/gradle :llm-dsl-core:runDSLTest --init-script llm-service/init.gradle

# 运行独立DSL测试
/opt/gradle/bin/gradle :llm-dsl-core:runStandaloneDSLTest --init-script llm-service/init.gradle
```

### 运行主服务
```bash
/opt/gradle/bin/gradle :llm-service:run --init-script llm-service/init.gradle
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