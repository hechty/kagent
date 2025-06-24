package com.llmservice.dsl

import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.delay

/**
 * 快速测试DSL功能 - 不启动Web服务器
 * 验证架构修复后的DSL可用性
 */
object DSLQuickTest {
    
    @JvmStatic
    fun main(args: Array<String>) = runBlocking {
        println("🚀 DSL快速功能测试开始")
        println("=" * 50)
        
        try {
            // 1. 基础DSL调用测试
            testBasicDSLCall()
            
            // 2. 对话功能测试  
            testConversationFeature()
            
            // 3. Agent功能测试
            testAgentFeature()
            
            println("\n✅ 所有DSL测试成功完成！")
            
        } catch (e: Exception) {
            println("\n❌ DSL测试失败: ${e.message}")
            e.printStackTrace()
        } finally {
            // 清理资源
            StandaloneDSLRunner.close()
        }
    }
    
    private suspend fun testBasicDSLCall() {
        println("\n1️⃣ 测试基础DSL调用...")
        
        // 创建提供商
        val deepseekProvider = StandaloneDSLRunner.deepseek()
        println("✅ DeepSeek提供商创建成功: ${deepseekProvider.name}")
        
        // 基础调用
        val response = "你好，请简单介绍一下协程的概念" using deepseekProvider
        println("✅ 基础DSL调用成功")
        println("🤖 DeepSeek回复: ${response.take(100)}...")
    }
    
    private suspend fun testConversationFeature() {
        println("\n2️⃣ 测试对话功能...")
        
        val provider = StandaloneDSLRunner.openrouter()
        val conversation = SimpleConversation(provider)
        
        // 设置系统角色
        conversation.system("你是一个简洁的技术助手，回答要简短精准")
        
        // 第一轮对话
        val answer1 = conversation.ask("什么是Kotlin协程？")
        println("✅ 第一轮对话成功")
        println("🤖 回复1: ${answer1.take(80)}...")
        
        delay(1000) // 避免API调用过快
        
        // 第二轮对话（带上下文）
        val answer2 = conversation.ask("它比线程有什么优势？")
        println("✅ 第二轮对话成功（保持上下文）")
        println("🤖 回复2: ${answer2.take(80)}...")
        
        println("📋 对话历史记录数量: ${conversation.history.size}")
    }
    
    private suspend fun testAgentFeature() {
        println("\n3️⃣ 测试Agent功能...")
        
        val provider = StandaloneDSLRunner.deepseek()
        val kotlinExpert = agent("Kotlin专家", provider, "Kotlin开发专家，专注于协程和DSL设计")
        
        val solution = kotlinExpert.solve("如何设计一个简洁易用的LLM DSL？")
        println("✅ Agent功能测试成功")
        println("🤖 Kotlin专家的建议: ${solution.take(100)}...")
    }
}

private operator fun String.times(count: Int): String = repeat(count)