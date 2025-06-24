package com.llmservice.dsl

import com.llmservice.config.DSLConfig
import com.llmservice.config.EnvironmentDetector
import kotlinx.coroutines.runBlocking

/**
 * 测试改进后的DSL功能
 */
object DSLImprovementTest {
    
    private val deepseekApiKey = "sk-325be9f2c5594c3cae07495b28817043"
    private val openrouterApiKey = "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"
    
    @JvmStatic
    fun main(args: Array<String>) = runBlocking {
        println("🚀 测试改进后的DSL功能")
        println("=" * 50)
        
        // 1. 环境诊断
        testEnvironmentDiagnostics()
        
        // 2. 基础功能测试
        testBasicFunctionality()
        
        // 3. 错误处理测试
        testErrorHandling()
        
        // 4. 性能测试
        testPerformance()
        
        println("✅ DSL改进测试完成")
    }
    
    private suspend fun testEnvironmentDiagnostics() {
        println("\n📊 1. 环境诊断测试")
        println("-" * 30)
        
        println(DSLDiagnostics.environmentReport())
        
        // 测试快速健康检查
        val provider = optimizedDeepseek(deepseekApiKey, config = DSLConfig.QUICK_TEST)
        val healthResult = DSLDiagnostics.healthCheck(provider)
        
        when (healthResult) {
            is DSLResult.Success -> {
                println("✅ 健康检查通过: ${healthResult.data}")
                println("📈 元数据: ${healthResult.metadata}")
            }
            is DSLResult.Failure -> {
                println("❌ 健康检查失败: ${healthResult.error.message}")
                println("📈 元数据: ${healthResult.metadata}")
            }
        }
    }
    
    private suspend fun testBasicFunctionality() {
        println("\n🔧 2. 基础功能测试")
        println("-" * 30)
        
        // 测试改进的API
        val provider = optimizedOpenrouter(openrouterApiKey, config = DSLConfig.QUICK_TEST)
        
        println("测试askSafely API...")
        val result = "Hello, just say 'Hi'" askSafely provider
        
        when (result) {
            is DSLResult.Success -> {
                println("✅ askSafely成功: ${result.data}")
                println("📊 执行时间: ${result.metadata.executionTime}")
                println("🎯 提供商: ${result.metadata.provider}")
                if (result.metadata.warnings.isNotEmpty()) {
                    println("⚠️ 警告: ${result.metadata.warnings}")
                }
            }
            is DSLResult.Failure -> {
                println("❌ askSafely失败: ${result.error.message}")
                println("📊 执行时间: ${result.metadata.executionTime}")
            }
        }
        
        // 测试弹性对话
        println("\n测试弹性对话...")
        val conversation = resilientConversation(provider, DSLConfig.QUICK_TEST)
        conversation.system("You are a helpful assistant. Keep responses brief.")
        
        val convResult = conversation.ask("What is 1+1?")
        when (convResult) {
            is DSLResult.Success -> {
                println("✅ 对话成功: ${convResult.data}")
                println("📊 对话统计: ${conversation.stats}")
            }
            is DSLResult.Failure -> {
                println("❌ 对话失败: ${convResult.error.message}")
            }
        }
    }
    
    private suspend fun testErrorHandling() {
        println("\n🛡️ 3. 错误处理测试")
        println("-" * 30)
        
        // 测试无效API密钥
        val invalidProvider = optimizedDeepseek("invalid-key", config = DSLConfig.QUICK_TEST)
        val errorResult = "Test error handling" askSafely invalidProvider
        
        when (errorResult) {
            is DSLResult.Success -> {
                println("⚠️ 意外成功（可能是模拟响应）: ${errorResult.data}")
            }
            is DSLResult.Failure -> {
                println("✅ 错误处理正常:")
                println("   错误类型: ${errorResult.error::class.simpleName}")
                println("   错误消息: ${errorResult.error.message}")
                println("   元数据: ${errorResult.metadata}")
            }
        }
    }
    
    private suspend fun testPerformance() {
        println("\n⚡ 4. 性能测试")
        println("-" * 30)
        
        val provider = optimizedDeepseek(deepseekApiKey, config = DSLConfig.QUICK_TEST)
        val perfResults = DSLDiagnostics.performanceTest(provider)
        
        println("性能测试结果:")
        perfResults.forEach { (key, value) ->
            println("  $key: $value")
        }
    }
    
    private operator fun String.times(count: Int): String {
        return this.repeat(count)
    }
}