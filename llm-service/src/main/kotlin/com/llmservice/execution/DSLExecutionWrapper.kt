package com.llmservice.execution

import com.llmservice.dsl.*
import kotlinx.coroutines.runBlocking

/**
 * DSL代码执行包装器
 * 专门用于测试和验证DSL代码的执行能力
 */

class DSLExecutionWrapper(
    private val executionEngine: CodeExecutionEngine = KotlinExecutionEngine()
) {
    
    fun testDSLUsability(): DSLUsabilityTestResult = runBlocking {
        println("🚀 开始DSL易用性测试")
        
        val testSuites = listOf(
            createBasicUsageTest(),
            createConversationTest(), 
            createAgentTest(),
            createCompareTest(),
            createBatchProcessingTest()
        )
        
        val results = mutableListOf<DSLTestResult>()
        
        testSuites.forEachIndexed { index, suite ->
            println("\n=== 测试 ${index + 1}: ${suite.name} ===")
            
            try {
                // 1. 生成测试代码
                val prompt = suite.prompt + "\n\n请只返回Kotlin代码，不要包含解释。"
                val generatedCode = prompt using deepseek("sk-325be9f2c5594c3cae07495b28817043")
                
                println("✅ 代码生成成功，长度: ${generatedCode.length}")
                
                // 2. 清理代码
                val cleanCode = cleanGeneratedCode(generatedCode)
                
                // 3. 执行代码
                val executionRequest = CodeExecutionRequest(
                    code = cleanCode,
                    template = CodeTemplateManager.getTemplate("dsl_test")
                )
                
                val executionResult = executionEngine.executeCode(executionRequest)
                
                results.add(DSLTestResult(
                    testName = suite.name,
                    success = executionResult.success,
                    generatedCode = cleanCode,
                    executionOutput = executionResult.output,
                    error = executionResult.error,
                    executionTime = executionResult.executionTimeMs
                ))
                
                if (executionResult.success) {
                    println("🎉 代码执行成功!")
                    println("📤 输出: ${executionResult.output.take(100)}...")
                } else {
                    println("❌ 代码执行失败: ${executionResult.error}")
                }
                
            } catch (e: Exception) {
                println("❌ 测试异常: ${e.message}")
                results.add(DSLTestResult(
                    testName = suite.name,
                    success = false,
                    error = e.message ?: "未知错误"
                ))
            }
        }
        
        generateUsabilityReport(results)
    }
    
    private fun cleanGeneratedCode(rawCode: String): String {
        // 移除markdown标记
        var cleaned = rawCode
            .replace("```kotlin", "")
            .replace("```kt", "")
            .replace("```", "")
            .trim()
        
        // 移除重复的package和import语句（模板会处理）
        val lines = cleaned.lines()
        val filteredLines = lines.filterNot { line ->
            val trimmed = line.trim()
            trimmed.startsWith("package ") ||
            trimmed.startsWith("import kotlinx.coroutines") ||
            trimmed.startsWith("fun main(")
        }
        
        return filteredLines.joinToString("\n").trim()
    }
    
    private fun generateUsabilityReport(results: List<DSLTestResult>): DSLUsabilityTestResult {
        val successCount = results.count { it.success }
        val totalCount = results.size
        val successRate = (successCount.toDouble() / totalCount * 100).toInt()
        
        println("\n" + "=".repeat(70))
        println("🏆 DSL易用性测试最终报告")
        println("=".repeat(70))
        
        results.forEach { result ->
            println("\n📋 ${result.testName}")
            if (result.success) {
                println("  ✅ 状态: 执行成功")
                println("  ⏱️ 耗时: ${result.executionTime}ms")
                println("  📤 输出: ${result.executionOutput.take(80)}...")
            } else {
                println("  ❌ 状态: 执行失败")
                println("  🐛 错误: ${result.error}")
            }
        }
        
        println("\n🎯 总体成功率: $successRate% ($successCount/$totalCount)")
        
        val rating = when {
            successRate == 100 -> DSLUsabilityRating.EXCELLENT
            successRate >= 80 -> DSLUsabilityRating.GOOD  
            successRate >= 60 -> DSLUsabilityRating.FAIR
            successRate >= 40 -> DSLUsabilityRating.POOR
            else -> DSLUsabilityRating.VERY_POOR
        }
        
        val feedback = when (rating) {
            DSLUsabilityRating.EXCELLENT -> "🏆 完美！DSL设计完全成功，LLM能够100%正确使用！"
            DSLUsabilityRating.GOOD -> "🎉 优秀！DSL易用性很高，LLM能生成大部分可执行代码"
            DSLUsabilityRating.FAIR -> "✅ 良好！DSL基本可用，但还有改进空间"
            DSLUsabilityRating.POOR -> "⚠️ 一般！DSL需要优化，LLM使用困难"
            DSLUsabilityRating.VERY_POOR -> "❌ 需要重新设计！DSL对LLM来说太难使用"
        }
        
        println(feedback)
        
        return DSLUsabilityTestResult(
            overallRating = rating,
            successRate = successRate,
            testResults = results,
            feedback = feedback
        )
    }
    
    // 测试用例定义
    
    private fun createBasicUsageTest() = DSLTestSuite(
        name = "基础DSL使用",
        prompt = """
使用简洁的Kotlin LLM DSL编写一个函数 `executeTest()`，实现：
1. 询问DeepSeek: "什么是函数式编程？"
2. 打印结果

使用模式: "问题" using deepseek("sk-325be9f2c5594c3cae07495b28817043")
"""
    )
    
    private fun createConversationTest() = DSLTestSuite(
        name = "对话管理测试",
        prompt = """
使用Kotlin LLM DSL编写 `executeTest()` 函数：
1. 创建SimpleConversation对话
2. 设置系统角色："你是编程专家，回答简洁"
3. 询问："什么是设计模式？"
4. 继续问："举一个例子"
5. 打印两轮对话

使用: SimpleConversation, system(), ask()
API Key: "sk-325be9f2c5594c3cae07495b28817043"
"""
    )
    
    private fun createAgentTest() = DSLTestSuite(
        name = "Agent系统测试", 
        prompt = """
使用Kotlin LLM DSL编写 `executeTest()` 函数：
1. 创建Agent: agent("助手", provider, "Kotlin专家")
2. 解决问题："如何优化性能？"
3. 打印Agent回答

API Key: "sk-325be9f2c5594c3cae07495b28817043"
"""
    )
    
    private fun createCompareTest() = DSLTestSuite(
        name = "多模型对比测试",
        prompt = """
使用Kotlin LLM DSL编写 `executeTest()` 函数：
1. 使用compare()对比两个模型对"什么是微服务？"的回答
2. 模型: deepseek和mockProvider("TestMock")
3. 打印对比结果

API Key: "sk-325be9f2c5594c3cae07495b28817043"
"""
    )
    
    private fun createBatchProcessingTest() = DSLTestSuite(
        name = "批量处理测试",
        prompt = """
使用Kotlin LLM DSL编写 `executeTest()` 函数：
1. 定义问题列表: ["什么是API？", "什么是REST？"]
2. 使用processAll()批量处理
3. 打印结果

API Key: "sk-325be9f2c5594c3cae07495b28817043"
"""
    )
}

// 数据类定义

data class DSLTestSuite(
    val name: String,
    val prompt: String
)

data class DSLTestResult(
    val testName: String,
    val success: Boolean,
    val generatedCode: String = "",
    val executionOutput: String = "",
    val error: String = "",
    val executionTime: Long = 0
)

data class DSLUsabilityTestResult(
    val overallRating: DSLUsabilityRating,
    val successRate: Int,
    val testResults: List<DSLTestResult>,
    val feedback: String
)

enum class DSLUsabilityRating {
    EXCELLENT,  // 90-100%
    GOOD,       // 80-89%
    FAIR,       // 60-79%
    POOR,       // 40-59%
    VERY_POOR   // 0-39%
}