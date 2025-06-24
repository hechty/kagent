package com.llmservice.discussion

import com.llmservice.config.DSLConfig
import com.llmservice.dsl.*
import kotlinx.coroutines.runBlocking

/**
 * 独立的DSL与Gemini交流 - 不启动服务器，直接使用DSL调用API
 */
object StandaloneDSLGeminiChat {
    
    private val openrouterApiKey = "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"
    
    @JvmStatic
    fun main(args: Array<String>) = runBlocking {
        println("🚀 独立Kotlin DSL与Gemini 2.5 Pro交流")
        println("=" * 60)
        
        // 1. 测试原始简洁语法
        testOriginalSyntax()
        
        // 2. 测试改进的安全语法
        testImprovedSafeSyntax()
        
        // 3. 测试对话管理
        testConversationManagement()
        
        // 4. 与Gemini讨论DSL设计
        discussDSLDesignWithGemini()
        
        println("\n🎉 独立DSL与Gemini交流完成")
    }
    
    private suspend fun testOriginalSyntax() {
        println("\n📝 1. 测试原始简洁语法")
        println("-" * 40)
        
        try {
            val gemini = optimizedOpenrouter(openrouterApiKey, "google/gemini-2.5-pro", DSLConfig.QUICK_TEST)
            
            println("使用最简语法: 'Hello' using gemini")
            val greeting = "Hello Gemini! 请用中文简单介绍你自己。" using gemini
            
            println("✅ Gemini回答:")
            println("   $greeting")
            
        } catch (e: Exception) {
            println("❌ 原始语法测试失败: ${e.message}")
        }
    }
    
    private suspend fun testImprovedSafeSyntax() {
        println("\n🛡️ 2. 测试改进的安全语法")
        println("-" * 40)
        
        try {
            val gemini = optimizedOpenrouter(openrouterApiKey, "google/gemini-2.5-pro", DSLConfig.DEVELOPMENT)
            
            println("使用安全语法: 'question' askSafely gemini")
            val result = "Kotlin DSL的核心优势是什么？请用3点总结。" askSafely gemini
            
            when (result) {
                is DSLResult.Success -> {
                    println("✅ 成功:")
                    println("   回答: ${result.data}")
                    println("📊 执行信息:")
                    println("   耗时: ${result.metadata.executionTime}")
                    println("   模型: ${result.metadata.model}")
                    result.metadata.tokenUsage?.let {
                        println("   Token: 输入${it.promptTokens} + 输出${it.completionTokens} = 总计${it.totalTokens}")
                    }
                }
                is DSLResult.Failure -> {
                    println("❌ 失败:")
                    println("   错误: ${result.error.message}")
                    println("   类型: ${result.error::class.simpleName}")
                }
            }
            
        } catch (e: Exception) {
            println("❌ 安全语法测试失败: ${e.message}")
        }
    }
    
    private suspend fun testConversationManagement() {
        println("\n💬 3. 测试对话管理")
        println("-" * 40)
        
        try {
            val gemini = optimizedOpenrouter(openrouterApiKey, "google/gemini-2.5-pro", DSLConfig.DEVELOPMENT)
            
            println("创建对话会话...")
            val chat = resilientConversation(gemini)
            
            chat.system("你是一个Kotlin专家，请用简洁的中文回答技术问题。")
            
            // 第一轮
            println("\n👤 用户: DSL的设计原则是什么？")
            val answer1 = chat.ask("DSL的设计原则是什么？")
            when (answer1) {
                is DSLResult.Success -> {
                    println("🤖 Gemini: ${answer1.data}")
                    
                    // 第二轮 - 测试上下文
                    println("\n👤 用户: 基于这些原则，我们的DSL还需要什么改进？")
                    val answer2 = chat.ask("基于这些原则，我们的DSL还需要什么改进？")
                    when (answer2) {
                        is DSLResult.Success -> {
                            println("🤖 Gemini: ${answer2.data}")
                            
                            // 显示对话统计
                            println("\n📊 对话统计:")
                            println("   总轮数: ${chat.stats.size}")
                            val totalMs = chat.stats.sumOf { it.executionTime.inWholeMilliseconds }
                            println("   总耗时: ${totalMs}ms (${totalMs/1000.0}秒)")
                            println("   消息数: ${chat.history.size}")
                        }
                        is DSLResult.Failure -> {
                            println("❌ 第二轮失败: ${answer2.error.message}")
                        }
                    }
                }
                is DSLResult.Failure -> {
                    println("❌ 第一轮失败: ${answer1.error.message}")
                }
            }
            
        } catch (e: Exception) {
            println("❌ 对话管理测试失败: ${e.message}")
        }
    }
    
    private suspend fun discussDSLDesignWithGemini() {
        println("\n🎯 4. 与Gemini深度讨论DSL设计")
        println("-" * 40)
        
        try {
            val gemini = optimizedOpenrouter(openrouterApiKey, "google/gemini-2.5-pro", DSLConfig.DEVELOPMENT)
            
            val deepQuestion = """
            我们刚刚展示了我们的Kotlin LLM DSL的两种语法：
            
            1. 简洁版: "question" using provider
            2. 安全版: "question" askSafely provider (返回DSLResult<String>)
            
            从实际使用角度：
            1. 你认为哪种语法更符合Kotlin的设计哲学？
            2. 对于生产环境，你会推荐哪种？为什么？
            3. 我们还应该设计什么样的语法糖来提升开发体验？
            
            请给出具体的技术建议和代码示例。
            """.trimIndent()
            
            println("向Gemini提出深度技术问题...")
            val discussion = deepQuestion askWith gemini
            
            println("🎯 Gemini的深度分析:")
            println(discussion)
            
            // 继续深入
            println("\n" + "-" * 40)
            println("继续讨论具体实现...")
            
            val followUp = """
            基于你的建议，我想了解：
            1. 在Kotlin中，如何设计既简洁又类型安全的Error Handling？
            2. 对于流式响应（Streaming），你会建议什么样的DSL语法？
            3. 如果要支持批量处理，最优雅的DSL设计是什么？
            
            请提供具体的Kotlin代码示例。
            """.trimIndent()
            
            val detailedAdvice = followUp askWith gemini
            
            println("🔬 Gemini的详细建议:")
            println(detailedAdvice)
            
        } catch (e: Exception) {
            println("❌ 深度讨论失败: ${e.message}")
        }
    }
    
    private operator fun String.times(count: Int): String = repeat(count)
}