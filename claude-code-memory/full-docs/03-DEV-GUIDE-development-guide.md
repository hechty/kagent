# LLM Service 开发指南

**文档用途**: 记录LLM统一接口服务的开发要点、常见问题解决方案和扩展指南
**快速定位**: 搜索关键词 - 新提供商、测试、部署、问题排查、扩展功能

## 开发环境要求
- WSL Ubuntu 24.04+ 
- Java 21 (必须，不支持Java 8/11)
- Kotlin 2.1.0+
- Gradle 8.13+
- uv (Python测试工具)

## 添加新LLM提供商

### 1. 创建Provider实现
```kotlin
// 在 src/main/kotlin/com/llmservice/provider/ 下创建
class NewProvider(
    private val apiKey: String,
    private val baseUrl: String = "https://api.example.com/v1",
    private val httpClient: HttpClient
) : LLMProvider {
    override val name: String = "NewProvider"
    override val supportedModels: List<String> = listOf("model1", "model2")
    
    override suspend fun chat(request: ChatRequest): ChatResponse {
        // 实现OpenAI兼容的接口调用
    }
}
```

### 2. 注册到枚举
```kotlin
// LLMProvider.kt
enum class ProviderType {
    // ... 现有的 ...
    NEW_PROVIDER
}
```

### 3. 在Application.kt中注册
```kotlin
llmService.registerProvider(
    ProviderType.NEW_PROVIDER,
    NewProvider(apiKey = "xxx", httpClient = httpClient)
)
```

## 测试开发

### 创建新测试
1. 在 `/root/code/python-tests/` 下创建 `test_*.py`
2. 必须在文件开头禁用代理:
```python
import os
# 禁用代理
os.environ.pop('http_proxy', None)
# ... 其他代理变量
```

### 运行测试
```bash
cd /root/code/python-tests
export PATH="$HOME/.local/bin:$PATH"
uv run python test_name.py
```

## 常见问题排查

### 1. 代理问题
**症状**: 测试返回502错误
**解决**: 
- Python测试中禁用代理环境变量
- 直接访问使用 `curl --noproxy "*" http://127.0.0.1:8080`

### 2. 序列化错误
**症状**: LinkedHashMap序列化失败
**解决**: 使用具体的数据类而非Map，如MultipleProviderResponse

### 3. JVM版本冲突
**症状**: JVM-target compatibility detected
**解决**: 确保kotlinOptions.jvmTarget = "21"和Java toolchain都设为21

### 4. Gradle下载超时
**症状**: gradle wrapper下载失败
**解决**: 使用腾讯镜像或阿里云镜像修改gradle-wrapper.properties

## 简洁LLM DSL使用

### 基础用法
```kotlin
// 最简单的一行代码
val answer = "你好" using deepseek("api-key")

// 对话管理
val chat = conversation(provider) {
    system("你是专家")
    ask("问题1")
}

// 多模型对比
val comparison = compare("问题", mapOf(
    "gpt4" to openrouter("key"),
    "deepseek" to deepseek("key")
))

// Agent
val coder = agent("程序员", provider, "Kotlin专家")
val result = coder.solve("优化这段代码")
```

### 核心设计理念
1. **渐进式复杂度**: 从一行代码到复杂场景
2. **类型安全**: 充分利用Kotlin类型系统
3. **简洁优于复杂**: 避免过度工程化
4. **符合直觉**: API接近自然语言

## 扩展功能

### 添加流式响应
1. 在ChatRequest中添加stream字段支持
2. 在各Provider中实现SSE响应处理
3. 在Application.kt中添加对应的路由

### 添加认证机制
1. 创建AuthenticationProvider
2. 在Application.kt中安装Authentication插件
3. 为需要保护的路由添加authenticate块

### 添加监控指标
1. 添加Micrometer依赖
2. 在build.gradle.kts中配置metrics
3. 创建自定义metrics收集器

## 性能优化

### HTTP客户端配置
- 连接池大小调优
- 超时时间设置
- Keep-alive配置

### 并发处理
- 使用Dispatchers.IO进行IO密集型操作
- 合理设置协程池大小
- 避免在热路径上创建过多协程

## 部署注意事项

### 生产环境配置
- API密钥通过环境变量注入
- 启用HTTPS
- 配置适当的日志级别
- 设置健康检查探针

### Docker化部署
```dockerfile
FROM openjdk:21-jre-slim
COPY build/libs/*.jar app.jar
EXPOSE 8080
CMD ["java", "-jar", "app.jar"]
```

## API密钥管理
- 开发环境: 使用 llm-keys.md 中的测试密钥
- 生产环境: 通过环境变量或密钥管理服务注入
- 密钥轮换: 支持运行时重新加载配置