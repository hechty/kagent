package com.llmservice.dsl

import kotlinx.coroutines.runBlocking

/**
 * 独立的DSL测试 - 不需要启动服务器
 */
fun main() = runBlocking {
    println("🚀 简洁LLM DSL 独立测试")
    
    try {
        // 1. 最简单的用法
        println("\n=== 1. 基础用法 ===")
        val provider = deepseek("sk-325be9f2c5594c3cae07495b28817043")
        val answer = "你好，请用一句话介绍一下自己" using provider
        println("回答: $answer")
        
        // 2. 对话管理测试
        println("\n=== 2. 对话管理 ===")
        val chat = SimpleConversation(provider)
        chat.system("你是一个简洁的助手，每次回答不超过30字")
        val ans1 = chat.ask("什么是协程？")
        println("回答1: $ans1")
        
        val ans2 = chat.ask("它有什么优势？")
        println("回答2: $ans2")
        
        // 3. 多模型对比
        println("\n=== 3. 多模型对比 ===")
        val comparison = compare(
            "用一句话解释人工智能",
            mapOf(
                "deepseek" to deepseek("sk-325be9f2c5594c3cae07495b28817043"),
                "openrouter" to openrouter("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")
            )
        )
        
        comparison.forEach { (model, answer) ->
            println("$model: ${answer.take(50)}...")
        }
        
        // 4. Agent测试
        println("\n=== 4. Agent ===")
        val coder = agent("程序员", provider, "Kotlin专家")
        val advice = coder.solve("如何优化字符串拼接？")
        println("程序员建议: ${advice.take(60)}...")
        
        // 5. 回退策略测试
        println("\n=== 5. 回退策略 ===")
        val mockFaulty = mockProvider("TestFailure")
        val resilient = provider.withFallback(mockFaulty)
        val safeAnswer = "测试回退机制" using resilient
        println("回退结果: ${safeAnswer.take(40)}...")
        
        println("\n✅ DSL独立测试完成！")
        
    } catch (e: Exception) {
        println("❌ 测试过程中出现错误: ${e.message}")
        e.printStackTrace()
    }
}