# CLAUDE项目记忆 - 摘要

## 核心信息
- **项目类型**: Kotlin 2.1.0 + Ktor统一LLM接口服务
- **构建工具**: Gradle 8.13，Java OpenJDK 21
- **运行环境**: WSL Ubuntu 24.04，端口8080
- **代理配置**: http://172.21.80.1:7890

## 关键架构
- 统一LLM提供商接口设计
- 支持DeepSeek、OpenRouter等多个提供商
- 完整的API密钥管理
- Python测试框架集成

## 重要命令
```bash
# 构建: /opt/gradle/bin/gradle build --init-script init.gradle
# 运行: /opt/gradle/bin/gradle run --init-script init.gradle
# 测试: uv run python test_llm_real.py
```

## API端点
- `/health` - 健康检查
- `/models` - 模型列表  
- `/chat/{provider}` - 单提供商聊天
- `/chat/multiple` - 多提供商并行聊天

**记忆类型**: 核心项目配置和架构记忆