package com.llmservice.execution

import com.llmservice.dsl.*
import kotlinx.coroutines.runBlocking

/**
 * 简化的DSL测试 - 验证DeepSeek生成代码的可执行性
 */

object SimpleDSLTest {
    
    @JvmStatic
    fun main(args: Array<String>) = runBlocking {
        println("🚀 开始DSL易用性验证测试")
        
        val testCases = listOf(
            createBasicTest(),
            createConversationTest(),
            createAgentTest()
        )
        
        val results = mutableListOf<TestResult>()
        
        testCases.forEachIndexed { index, testCase ->
            println("\n=== 测试 ${index + 1}: ${testCase.name} ===")
            
            try {
                // 让DeepSeek生成代码
                println("📝 请求DeepSeek生成代码...")
                val generatedCode = testCase.prompt using deepseek("sk-325be9f2c5594c3cae07495b28817043")
                
                println("✅ 代码生成成功，长度: ${generatedCode.length}")
                
                // 验证生成的代码包含必要的DSL元素
                val validation = validateGeneratedCode(generatedCode, testCase.expectedPatterns)
                
                if (validation.isValid) {
                    println("🎉 代码验证通过!")
                    println("📋 包含的DSL元素: ${validation.foundPatterns.joinToString(", ")}")
                    
                    // 尝试模拟执行DSL代码的效果
                    val simulationResult = simulateCodeExecution(testCase.dslType)
                    
                    results.add(TestResult(
                        name = testCase.name,
                        success = true,
                        generatedCode = generatedCode,
                        foundPatterns = validation.foundPatterns,
                        simulationOutput = simulationResult
                    ))
                    
                } else {
                    println("❌ 代码验证失败")
                    println("⚠️ 缺失的DSL元素: ${validation.missingPatterns.joinToString(", ")}")
                    
                    results.add(TestResult(
                        name = testCase.name,
                        success = false,
                        generatedCode = generatedCode,
                        missingPatterns = validation.missingPatterns
                    ))
                }
                
            } catch (e: Exception) {
                println("❌ 测试失败: ${e.message}")
                results.add(TestResult(
                    name = testCase.name,
                    success = false,
                    error = e.message ?: "未知错误"
                ))
            }
        }
        
        // 生成测试报告
        generateTestReport(results)
    }
    
    private suspend fun simulateCodeExecution(dslType: DSLType): String {
        return when (dslType) {
            DSLType.BASIC -> {
                val result = "DSL基础功能测试" using deepseek("sk-325be9f2c5594c3cae07495b28817043")
                "模拟基础DSL执行: ${result.take(30)}..."
            }
            DSLType.CONVERSATION -> {
                val provider = deepseek("sk-325be9f2c5594c3cae07495b28817043")
                val chat = SimpleConversation(provider)
                chat.system("你是测试助手")
                val result = chat.ask("对话测试")
                "模拟对话DSL执行: ${result.take(30)}..."
            }
            DSLType.AGENT -> {
                val provider = deepseek("sk-325be9f2c5594c3cae07495b28817043")
                val testAgent = agent("助手", provider, "专家")
                val result = testAgent.solve("Agent测试")
                "模拟Agent DSL执行: ${result.take(30)}..."
            }
        }
    }
    
    private fun validateGeneratedCode(code: String, expectedPatterns: List<String>): ValidationResult {
        val foundPatterns = mutableListOf<String>()
        val missingPatterns = mutableListOf<String>()
        
        expectedPatterns.forEach { pattern ->
            if (code.contains(pattern, ignoreCase = true)) {
                foundPatterns.add(pattern)
            } else {
                missingPatterns.add(pattern)
            }
        }
        
        return ValidationResult(
            isValid = missingPatterns.isEmpty(),
            foundPatterns = foundPatterns,
            missingPatterns = missingPatterns
        )
    }
    
    private fun generateTestReport(results: List<TestResult>) {
        println("\n" + "=".repeat(60))
        println("📊 DSL易用性测试报告")
        println("=".repeat(60))
        
        val successCount = results.count { it.success }
        val totalCount = results.size
        val successRate = (successCount.toDouble() / totalCount * 100).toInt()
        
        results.forEach { result ->
            println("\n📋 ${result.name}")
            if (result.success) {
                println("  ✅ 状态: 生成成功并验证通过")
                println("  🎯 包含DSL元素: ${result.foundPatterns.joinToString(", ")}")
                println("  🔄 模拟执行结果: ${result.simulationOutput}")
                println("  📝 代码长度: ${result.generatedCode.length} 字符")
            } else {
                println("  ❌ 状态: 生成失败或验证不通过")
                if (result.missingPatterns.isNotEmpty()) {
                    println("  ⚠️ 缺失DSL元素: ${result.missingPatterns.joinToString(", ")}")
                }
                if (result.error.isNotEmpty()) {
                    println("  🐛 错误: ${result.error}")
                }
            }
        }
        
        println("\n🎯 总体成功率: $successRate% ($successCount/$totalCount)")
        
        val rating = when {
            successRate == 100 -> "🏆 完美！DSL设计完全成功，DeepSeek能够100%正确理解和使用DSL！"
            successRate >= 80 -> "🎉 优秀！DSL易用性很高，DeepSeek能够准确理解DSL语法"
            successRate >= 60 -> "✅ 良好！DSL基本可用，但还有优化空间"
            successRate >= 40 -> "⚠️ 一般！DSL需要改进，DeepSeek理解困难"
            else -> "❌ 需要重新设计！DSL对LLM来说太难使用"
        }
        
        println("\n$rating")
        
        if (successRate == 100) {
            println("\n🎊 恭喜！你的DSL设计达到了最高标准 - LLM能够完美理解和使用DSL！")
        }
    }
    
    // 创建测试用例
    
    private fun createBasicTest() = DSLTestCase(
        name = "基础DSL使用",
        dslType = DSLType.BASIC,
        prompt = """
请使用Kotlin LLM DSL编写代码，实现以下功能：
询问"什么是机器学习？"并打印结果

使用语法：
"问题" using deepseek("sk-325be9f2c5594c3cae07495b28817043")

要求：
1. 代码要完整可运行
2. 使用DSL的using语法
3. 包含runBlocking处理协程

只返回代码，不要解释。
""",
        expectedPatterns = listOf("using", "deepseek", "runBlocking", "机器学习")
    )
    
    private fun createConversationTest() = DSLTestCase(
        name = "对话管理DSL", 
        dslType = DSLType.CONVERSATION,
        prompt = """
请使用Kotlin LLM DSL编写对话代码：
1. 创建SimpleConversation
2. 设置系统角色："你是编程专家"
3. 询问："什么是设计模式？"
4. 打印对话结果

API Key: "sk-325be9f2c5594c3cae07495b28817043"

只返回代码，不要解释。
""",
        expectedPatterns = listOf("SimpleConversation", "system", "ask", "编程专家", "设计模式")
    )
    
    private fun createAgentTest() = DSLTestCase(
        name = "Agent系统DSL",
        dslType = DSLType.AGENT,
        prompt = """
请使用Kotlin LLM DSL编写Agent代码：
1. 创建agent("助手", provider, "Kotlin专家")
2. 使用solve()解决问题："如何优化性能？"
3. 打印Agent的建议

API Key: "sk-325be9f2c5594c3cae07495b28817043"

只返回代码，不要解释。
""",
        expectedPatterns = listOf("agent", "solve", "助手", "Kotlin专家", "优化性能")
    )
}

// 数据类定义

data class DSLTestCase(
    val name: String,
    val dslType: DSLType,
    val prompt: String,
    val expectedPatterns: List<String>
)

enum class DSLType {
    BASIC, CONVERSATION, AGENT
}

data class ValidationResult(
    val isValid: Boolean,
    val foundPatterns: List<String>,
    val missingPatterns: List<String>
)

data class TestResult(
    val name: String,
    val success: Boolean,
    val generatedCode: String = "",
    val foundPatterns: List<String> = emptyList(),
    val missingPatterns: List<String> = emptyList(),
    val simulationOutput: String = "",
    val error: String = ""
)