package com.llmservice.discussion

import com.llmservice.config.DSLConfig
import com.llmservice.dsl.*
import kotlinx.coroutines.runBlocking

/**
 * 使用我们的Kotlin DSL与Gemini 2.5 Pro进行交流
 * 验证DSL在实际对话中的表现
 */
object KotlinDSLGeminiChat {
    
    private val openrouterApiKey = "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"
    
    @JvmStatic
    fun main(args: Array<String>) = runBlocking {
        println("🚀 使用Kotlin DSL与Gemini 2.5 Pro交流")
        println("=" * 60)
        
        // 1. 基础DSL测试
        testBasicDSLUsage()
        
        // 2. 改进的DSL测试
        testImprovedDSLUsage()
        
        // 3. 深度技术讨论
        testTechnicalDiscussion()
        
        // 4. 对话式交流
        testConversationalChat()
        
        println("\n✅ Kotlin DSL与Gemini交流测试完成")
    }
    
    private suspend fun testBasicDSLUsage() {
        println("\n📝 1. 基础DSL使用测试")
        println("-" * 40)
        
        try {
            // 使用简洁的原始DSL语法
            val provider = optimizedOpenrouter(openrouterApiKey, config = DSLConfig.QUICK_TEST)
            
            println("使用原始DSL语法: 'question' using provider")
            val response = "Hello Gemini! Please introduce yourself briefly." using provider
            
            println("✅ Gemini回答:")
            println("   $response")
            
        } catch (e: Exception) {
            println("❌ 基础DSL测试失败: ${e.message}")
        }
    }
    
    private suspend fun testImprovedDSLUsage() {
        println("\n🔧 2. 改进的DSL使用测试")
        println("-" * 40)
        
        try {
            val provider = optimizedOpenrouter(openrouterApiKey, config = DSLConfig.DEVELOPMENT)
            
            println("使用改进的DSL语法: 'question' askSafely provider")
            val result = "What are the key advantages of Kotlin over Java for DSL development?" askSafely provider
            
            when (result) {
                is DSLResult.Success -> {
                    println("✅ 成功获得回答:")
                    println("   内容: ${result.data}")
                    println("📊 元数据:")
                    println("   执行时间: ${result.metadata.executionTime}")
                    println("   提供商: ${result.metadata.provider}")
                    println("   模型: ${result.metadata.model}")
                    if (result.metadata.tokenUsage != null) {
                        println("   Token使用: ${result.metadata.tokenUsage}")
                    }
                    if (result.metadata.warnings.isNotEmpty()) {
                        println("⚠️ 警告: ${result.metadata.warnings}")
                    }
                }
                is DSLResult.Failure -> {
                    println("❌ 请求失败:")
                    println("   错误类型: ${result.error::class.simpleName}")
                    println("   错误消息: ${result.error.message}")
                    println("   元数据: ${result.metadata}")
                }
            }
            
        } catch (e: Exception) {
            println("❌ 改进DSL测试失败: ${e.message}")
        }
    }
    
    private suspend fun testTechnicalDiscussion() {
        println("\n💡 3. 深度技术讨论")
        println("-" * 40)
        
        try {
            val provider = optimizedOpenrouter(openrouterApiKey, config = DSLConfig.DEVELOPMENT)
            
            val technicalQuestion = """
            基于我们刚才的讨论，我想深入了解：
            
            1. 在Kotlin中，使用infix函数（如 'askSafely'）相比普通函数调用有什么性能影响？
            2. 对于LLM框架，你认为函数式编程范式（如Result类型）相比命令式有什么优势？
            3. 从类型安全角度，Kotlin的密封类（sealed class）在错误处理中比Java的异常机制有什么优势？
            
            请提供技术性深入分析，包括具体例子。
            """.trimIndent()
            
            println("向Gemini提出技术问题...")
            val response = technicalQuestion askWith provider
            
            println("🎯 Gemini的技术分析:")
            println(response)
            
        } catch (e: Exception) {
            println("❌ 技术讨论失败: ${e.message}")
        }
    }
    
    private suspend fun testConversationalChat() {
        println("\n💬 4. 对话式交流测试")
        println("-" * 40)
        
        try {
            val provider = optimizedOpenrouter(openrouterApiKey, config = DSLConfig.DEVELOPMENT)
            
            println("创建弹性对话...")
            val conversation = resilientConversation(provider, DSLConfig.DEVELOPMENT)
            
            // 设置系统角色
            conversation.system("你是一个Kotlin语言专家和DSL设计师，请用简洁专业的中文回答。")
            
            // 第一轮对话
            println("\n第一轮对话:")
            val result1 = conversation.ask("我们的DSL设计的核心理念是什么？")
            when (result1) {
                is DSLResult.Success -> {
                    println("🤖 Gemini: ${result1.data}")
                    println("⏱️ 耗时: ${result1.metadata.executionTime}")
                }
                is DSLResult.Failure -> {
                    println("❌ 第一轮失败: ${result1.error.message}")
                    return
                }
            }
            
            // 第二轮对话 - 测试上下文记忆
            println("\n第二轮对话:")
            val result2 = conversation.ask("基于这个理念，我们还应该添加哪些功能？")
            when (result2) {
                is DSLResult.Success -> {
                    println("🤖 Gemini: ${result2.data}")
                    println("⏱️ 耗时: ${result2.metadata.executionTime}")
                }
                is DSLResult.Failure -> {
                    println("❌ 第二轮失败: ${result2.error.message}")
                    return
                }
            }
            
            // 第三轮对话 - 深入讨论
            println("\n第三轮对话:")
            val result3 = conversation.ask("从实用性角度，哪个功能最重要，为什么？")
            when (result3) {
                is DSLResult.Success -> {
                    println("🤖 Gemini: ${result3.data}")
                    println("⏱️ 耗时: ${result3.metadata.executionTime}")
                    
                    // 显示对话统计
                    println("\n📊 对话统计:")
                    println("   总轮数: ${conversation.stats.size}")
                    val totalTime = conversation.stats.sumOf { it.executionTime.inWholeMilliseconds }
                    println("   总耗时: ${totalTime}ms")
                    val avgTime = totalTime / conversation.stats.size
                    println("   平均耗时: ${avgTime}ms")
                    
                    // 显示对话历史
                    println("\n📜 完整对话历史:")
                    conversation.history.forEachIndexed { index, message ->
                        val speaker = when (message.role) {
                            "system" -> "🔧 系统"
                            "user" -> "👤 用户"
                            "assistant" -> "🤖 Gemini"
                            else -> message.role
                        }
                        println("   $speaker: ${message.content.take(50)}...")
                    }
                }
                is DSLResult.Failure -> {
                    println("❌ 第三轮失败: ${result3.error.message}")
                }
            }
            
        } catch (e: Exception) {
            println("❌ 对话测试失败: ${e.message}")
        }
    }
    
    private operator fun String.times(count: Int): String {
        return this.repeat(count)
    }
}