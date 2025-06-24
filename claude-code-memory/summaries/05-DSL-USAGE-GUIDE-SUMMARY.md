# DSL使用指南 - 摘要

## 快速开始
### 基础使用流程
1. 创建LLMService实例
2. 注册提供商
3. 配置DSL
4. 执行查询

```kotlin
val llmService = LLMService()
llmService.registerProvider(ProviderType.OPENAI, OpenAIProvider("api-key", httpClient))
val execution = llm(llmService) {
    provider { openai("api-key").model("gpt-4") }
}
val response = execution.ask("你好")
```

## 核心功能
### 对话模式
- 多轮对话支持
- 上下文保持
- 系统提示词配置

### 高级特性
- 流式响应
- 批量处理
- 工具集成
- 错误处理和重试

### 配置选项
- 模型参数调优
- 弹性配置
- 上下文窗口管理
- 响应格式定制

## 实际应用场景
- 基础问答系统
- 智能对话助手
- 批量文本处理
- 工具增强的Agent

**记忆类型**: DSL使用指南记忆