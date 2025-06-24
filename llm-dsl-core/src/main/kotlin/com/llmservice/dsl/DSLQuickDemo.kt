package com.llmservice.dsl

import kotlinx.coroutines.runBlocking

/**
 * 简洁DSL的快速演示
 */

fun main() = runBlocking {
    println("🚀 简洁LLM DSL演示")
    
    try {
        // 1. 最简单的用法
        println("\n=== 1. 基础用法 ===")
        val provider = deepseek("sk-325be9f2c5594c3cae07495b28817043")
        val answer = "你好，请简单介绍一下自己" using provider
        println("回答: $answer")
        
        // 2. 对话管理
        println("\n=== 2. 对话管理 ===")
        val chat = conversation(provider) {
            system("你是一个Kotlin专家")
            val ans1 = ask("什么是协程？")
            println("专家: ${ans1.take(100)}...")
        }
        
        val followUp = chat.ask("协程有什么优势？")
        println("专家续: ${followUp.take(100)}...")
        
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
            println("$model: ${answer.take(60)}...")
        }
        
        // 4. 批量处理
        println("\n=== 4. 批量处理 ===")
        val questions = listOf("什么是API？", "什么是数据库？")
        val answers = questions.processAll(provider)
        
        questions.zip(answers).forEach { (q, a) ->
            println("Q: $q")
            println("A: ${a.take(50)}...")
            println("---")
        }
        
        // 5. Agent
        println("\n=== 5. Agent ===")
        val coder = agent("程序员", provider, "资深Kotlin开发者")
        val advice = coder.solve("如何优化这个函数：fun add(a: Int, b: Int) = a + b")
        println("程序员建议: ${advice.take(80)}...")
        
        // 6. 回退策略
        println("\n=== 6. 回退策略 ===")
        val mockFaulty = mockProvider("Faulty").apply {
            // 这个会立即失败用于测试回退
        }
        val resilient = mockFaulty.withFallback(provider)
        val safeAnswer = "这是回退测试" using resilient
        println("回退成功: $safeAnswer")
        
        // 7. 全局便利函数
        println("\n=== 7. 便利函数 ===")
        val quickAnswer = ask("今天天气怎么样？")
        println("快速回答: ${quickAnswer.take(50)}...")
        
        val quickComp = quickCompare("解释什么是区块链")
        quickComp.forEach { (model, answer) ->
            println("$model: ${answer.take(40)}...")
        }
        
        println("\n✅ DSL演示完成！")
        
    } catch (e: Exception) {
        println("❌ 演示过程中出现错误: ${e.message}")
        e.printStackTrace()
    }
}

/**
 * 最小测试
 */
fun quickTest() = runBlocking {
    try {
        val answer = "你好" using deepseek("sk-325be9f2c5594c3cae07495b28817043")
        println("✅ 测试成功: $answer")
    } catch (e: Exception) {
        println("❌ 测试失败: ${e.message}")
    }
}