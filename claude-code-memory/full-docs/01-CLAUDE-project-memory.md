# LLM Service 项目记忆

## 项目概述
这是一个Kotlin 2.1.0 + Ktor构建的统一LLM接口服务，用于对接多个LLM提供商。

## 核心架构
- **语言**: Kotlin 2.1.0
- **框架**: Ktor (服务端+客户端)
- **构建**: Gradle 8.13
- **序列化**: kotlinx.serialization
- **端口**: 8080

## 环境配置要点
- **系统**: WSL Ubuntu 24.04
- **Java**: OpenJDK 21 (必须，JVM target 21)
- **代理**: 系统使用 http://172.21.80.1:7890
- **镜像**: 阿里云Maven镜像 + 腾讯Gradle镜像
- **Python**: uv包管理器用于测试

## 核心文件结构
```
code/
├── llm-service/                 # Kotlin服务主项目
│   ├── src/main/kotlin/com/llmservice/
│   │   ├── Application.kt       # 主程序入口
│   │   ├── model/              # 数据模型
│   │   ├── service/            # 核心服务逻辑
│   │   └── provider/           # LLM提供商实现
│   ├── build.gradle.kts        # 构建配置
│   └── init.gradle             # 阿里云镜像配置
├── python-tests/               # Python集成测试
└── llm-keys.md                # API密钥配置

```

## 重要命令
```bash
# 构建和运行服务
cd /root/code/llm-service
/opt/gradle/bin/gradle build --init-script init.gradle
/opt/gradle/bin/gradle run --init-script init.gradle

# 运行测试(无代理)
cd /root/code/python-tests
export PATH="$HOME/.local/bin:$PATH"
uv run python test_llm_real.py
```

## API密钥
- DeepSeek: sk-325be9f2c5594c3cae07495b28817043
- OpenRouter: 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

## 已实现的提供商
- **DeepSeek**: deepseek-chat, deepseek-reasoner
- **OpenRouter**: openai/gpt-4.1, google/gemini-2.5-pro, anthropic/claude-sonnet-4等

## 关键API端点
- `GET /health` - 健康检查
- `GET /models` - 获取支持的模型
- `POST /chat/{provider}` - 单提供商聊天
- `POST /chat/multiple` - 多提供商并行聊天

## 重要配置点
- 所有LLM提供商都实现OpenAI兼容接口
- 使用统一的ChatRequest/ChatResponse模型
- 支持异步并发请求
- 完整的错误处理和序列化