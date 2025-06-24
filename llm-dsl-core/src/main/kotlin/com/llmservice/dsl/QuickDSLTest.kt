package com.llmservice.dsl

import kotlinx.coroutines.runBlocking

/**
 * 极简DSL测试 - 验证DSL的基本功能
 */
object QuickDSLTest {
    @JvmStatic
    fun main(args: Array<String>) = runBlocking {
        println("🚀 简洁LLM DSL 快速测试")
        
        try {
            // 测试基本的provider创建
            println("\n=== Provider创建测试 ===")
            val provider = deepseek("sk-325be9f2c5594c3cae07495b28817043")
            println("✅ DeepSeek Provider创建成功: ${provider.name}")
            println("支持的模型: ${provider.supportedModels}")
            
            // 测试最基本的DSL用法
            println("\n=== 基础DSL测试 ===")
            val question = "你好，请用一句话回答：什么是Kotlin？"
            val answer = question using provider
            println("问题: $question")
            println("回答: $answer")
            
            // 测试对话管理
            println("\n=== 对话管理测试 ===")
            val chat = SimpleConversation(provider)
            chat.system("你是一个简洁的技术助手，回答不超过20字")
            val ans1 = chat.ask("什么是协程？")
            println("第一轮回答: $ans1")
            
            val ans2 = chat.ask("它的主要优势是什么？")
            println("第二轮回答: $ans2")
            
            // 测试Agent
            println("\n=== Agent测试 ===")
            val coder = agent("Kotlin专家", provider, "资深Kotlin开发者")
            val advice = coder.solve("如何在Kotlin中进行字符串插值？")
            println("专家建议: $advice")
            
            // 测试mock provider
            println("\n=== Mock Provider测试 ===")
            val mockProv = mockProvider("TestMock")
            val mockAnswer = "测试Mock功能" using mockProv
            println("Mock回答: $mockAnswer")
            
            println("\n✅ 所有DSL功能测试通过！")
            
        } catch (e: Exception) {
            println("❌ 测试失败: ${e.message}")
            e.printStackTrace()
        }
    }
}