package com.llmservice.execution

import com.llmservice.dsl.*
import kotlinx.coroutines.runBlocking

/**
 * 执行系统测试运行器
 * 集成所有执行功能的测试入口
 */

object ExecutionTestRunner {
    
    @JvmStatic
    fun main(args: Array<String>) = runBlocking {
        println("🚀 启动代码执行系统综合测试")
        
        try {
            // 1. 测试基础执行引擎
            testBasicExecutionEngine()
            
            // 2. 测试安全管理器
            testSecurityManager()
            
            // 3. 测试DSL执行包装器
            testDSLExecutionWrapper()
            
            println("\n🎉 所有测试完成！")
            
        } catch (e: Exception) {
            println("❌ 测试过程中出现异常: ${e.message}")
            e.printStackTrace()
        }
    }
    
    private suspend fun testBasicExecutionEngine() {
        println("\n=== 测试基础执行引擎 ===")
        
        val engine = KotlinExecutionEngine()
        
        // 简单代码测试
        val simpleCode = """
            println("Hello from dynamic execution!")
            val x = 5 + 3
            println("计算结果: ${'$'}x")
        """
        
        val request = CodeExecutionRequest(
            code = simpleCode,
            template = CodeTemplateManager.getTemplate("basic")
        )
        
        val result = engine.executeCode(request)
        
        if (result.success) {
            println("✅ 基础执行引擎测试成功")
            println("📤 输出: ${result.output}")
        } else {
            println("❌ 基础执行引擎测试失败: ${result.error}")
        }
    }
    
    private fun testSecurityManager() {
        println("\n=== 测试安全管理器 ===")
        
        // 测试安全代码
        val safeCode = """
            val numbers = listOf(1, 2, 3, 4, 5)
            val sum = numbers.sum()
            println("Sum: ${'$'}sum")
        """
        
        val safeResult = ExecutionSecurityManager.validateCodeSecurity(safeCode)
        println("✅ 安全代码验证: ${if (safeResult.isSecure) "通过" else "失败"}")
        
        // 测试危险代码
        val dangerousCode = """
            System.exit(0)
            val file = File("important.txt")
            file.delete()
        """
        
        val dangerousResult = ExecutionSecurityManager.validateCodeSecurity(dangerousCode)
        println("⚠️ 危险代码验证: ${if (!dangerousResult.isSecure) "正确识别" else "检测失败"}")
        println("   发现 ${dangerousResult.violations.size} 个安全问题")
    }
    
    private suspend fun testDSLExecutionWrapper() {
        println("\n=== 测试DSL执行包装器 ===")
        
        val wrapper = DSLExecutionWrapper()
        
        try {
            val usabilityResult = wrapper.testDSLUsability()
            println("\n📊 DSL易用性测试完成")
            println("🎯 总体评级: ${usabilityResult.overallRating}")
            println("📈 成功率: ${usabilityResult.successRate}%")
            
        } catch (e: Exception) {
            println("❌ DSL执行包装器测试失败: ${e.message}")
        }
    }
    
    // 演示完整的代码生成和执行流程
    suspend fun demonstrateFullPipeline() {
        println("\n=== 演示完整的代码生成执行流程 ===")
        
        // 1. 使用DSL让LLM生成代码
        val codeGenerationPrompt = """
请用Kotlin编写一个函数，计算斐波那契数列的第n项：

要求：
1. 函数名为fibonacci
2. 参数为n: Int
3. 使用递归实现
4. 在main函数中调用并打印结果

只返回代码，不要解释。
"""
        
        println("📝 请求LLM生成代码...")
        val generatedCode = codeGenerationPrompt using deepseek("sk-325be9f2c5594c3cae07495b28817043")
        
        println("✅ 代码生成完成，长度: ${generatedCode.length}")
        
        // 2. 安全验证
        val securityResult = ExecutionSecurityManager.validateCodeSecurity(generatedCode)
        println("🔒 安全验证: ${if (securityResult.isSecure) "通过" else "有风险"}")
        
        if (!securityResult.isSecure) {
            println("⚠️ 安全问题:")
            securityResult.violations.forEach { violation ->
                println("   - ${violation.message}")
            }
            return
        }
        
        // 3. 代码执行
        val engine = KotlinExecutionEngine()
        val executionRequest = CodeExecutionRequest(
            code = generatedCode,
            template = CodeTemplateManager.getTemplate("function")
        )
        
        println("⚡ 执行生成的代码...")
        val executionResult = engine.executeCode(executionRequest)
        
        if (executionResult.success) {
            println("🎉 代码执行成功!")
            println("📤 执行结果:")
            println(executionResult.output)
        } else {
            println("❌ 代码执行失败:")
            println(executionResult.error)
        }
    }
}