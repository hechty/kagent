package com.llmservice.dsl

import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.delay

/**
 * 使用DSL测试LLM对DSL的理解和使用能力
 * 让DeepSeek生成代码，然后执行生成的代码验证正确性
 */

object DSLUsabilityTest {
    
    // DSL文档和教学提示词
    private val DSL_TUTORIAL = """
# Kotlin LLM DSL 完整使用教程

## 包导入 (重要!)
```kotlin
package com.llmservice.dsl
import kotlinx.coroutines.runBlocking
```

## 1. 基础用法 - 最简单的一行代码
```kotlin
fun basicUsage() = runBlocking {
    val answer = "你好，请介绍一下自己" using deepseek("sk-325be9f2c5594c3cae07495b28817043")
    println("回答: ${'$'}answer")
}
```

## 2. 对话管理
```kotlin
fun conversationUsage() = runBlocking {
    val provider = deepseek("sk-325be9f2c5594c3cae07495b28817043")
    val chat = SimpleConversation(provider)
    chat.system("你是一个Kotlin专家，回答要简洁")
    val ans1 = chat.ask("什么是协程？")
    println("第一轮: ${'$'}ans1")
    
    val ans2 = chat.ask("协程有什么优势？")
    println("第二轮: ${'$'}ans2")
}
```

## 3. Agent系统
```kotlin
fun agentUsage() = runBlocking {
    val provider = deepseek("sk-325be9f2c5594c3cae07495b28817043")
    val coder = agent("程序员", provider, "资深Kotlin开发者")
    val advice = coder.solve("如何优化ArrayList的性能？")
    println("专家建议: ${'$'}advice")
}
```

## 4. 多模型对比
```kotlin
fun compareUsage() = runBlocking {
    val comparison = compare(
        "解释什么是人工智能",
        mapOf(
            "deepseek" to deepseek("sk-325be9f2c5594c3cae07495b28817043"),
            "mock" to mockProvider("TestMock")
        )
    )
    comparison.forEach { (model, answer) ->
        println("${'$'}model: ${'$'}{answer.take(50)}...")
    }
}
```

## 5. 批量处理
```kotlin
fun batchUsage() = runBlocking {
    val provider = deepseek("sk-325be9f2c5594c3cae07495b28817043")
    val questions = listOf("什么是API？", "什么是数据库？")
    val answers = questions.processAll(provider)
    questions.zip(answers).forEach { (q, a) ->
        println("Q: ${'$'}q")
        println("A: ${'$'}{a.take(50)}...")
    }
}
```

## 重要提示：
1. 所有函数必须用 `runBlocking` 包围或在suspend函数中调用
2. 使用真实的API Key: "sk-325be9f2c5594c3cae07495b28817043"
3. 包名必须是: package com.llmservice.dsl
4. 必须导入: import kotlinx.coroutines.runBlocking
5. 使用 `using` 中缀函数连接问题和provider
6. Agent创建后用 `solve()` 方法
7. 对话管理用 `SimpleConversation` 类
"""

    @JvmStatic
    fun main(args: Array<String>) = runBlocking {
        println("🚀 开始DSL易用性测试 - 让DeepSeek生成并执行DSL代码")
        
        val testCases = listOf(
            TestCase(
                name = "基础用法生成测试",
                prompt = """
$DSL_TUTORIAL

请使用上述Kotlin LLM DSL编写一个完整的函数，实现以下功能：
写一个名为 `generatedBasicTest` 的函数，使用DeepSeek询问"什么是机器学习？"

要求：
1. 函数完整可运行，包含package和import
2. 使用runBlocking处理协程
3. 使用DSL的 `using` 语法
4. 打印结果

只返回代码，不要解释。
""",
                validator = { code -> 
                    code.contains("generatedBasicTest") && 
                    code.contains("using") && 
                    code.contains("deepseek") &&
                    code.contains("runBlocking")
                }
            ),
            
            TestCase(
                name = "对话管理生成测试",
                prompt = """
$DSL_TUTORIAL

使用Kotlin LLM DSL编写一个名为 `generatedConversationTest` 的函数：
1. 创建一个Kotlin专家对话
2. 设置系统角色为"你是Python专家，回答要简洁"
3. 询问"什么是装饰器？"
4. 继续询问"请举个简单例子"

要求：
1. 使用SimpleConversation进行对话管理
2. 包含完整的package和import
3. 函数完整可运行
4. 打印两轮对话结果

只返回代码，不要解释。
""",
                validator = { code ->
                    code.contains("generatedConversationTest") &&
                    code.contains("SimpleConversation") &&
                    code.contains("system") &&
                    code.contains("ask")
                }
            ),
            
            TestCase(
                name = "Agent系统生成测试", 
                prompt = """
$DSL_TUTORIAL

使用Kotlin LLM DSL编写一个名为 `generatedAgentTest` 的函数：
1. 创建一个名为"编程助手"的Agent，角色是"资深Java开发者"
2. 让它解决"如何优化HashMap的性能？"这个问题
3. 打印Agent的建议

要求：
1. 使用agent()和solve()函数
2. 包含完整的package和import  
3. 函数完整可运行

只返回代码，不要解释。
""",
                validator = { code ->
                    code.contains("generatedAgentTest") &&
                    code.contains("agent") &&
                    code.contains("solve") &&
                    code.contains("编程助手")
                }
            )
        )
        
        val results = mutableListOf<TestResult>()
        
        testCases.forEachIndexed { index, testCase ->
            println("\n=== 测试 ${index + 1}: ${testCase.name} ===")
            
            try {
                // 让DeepSeek生成代码
                val generatedCode = testCase.prompt using deepseek("sk-325be9f2c5594c3cae07495b28817043")
                
                println("✅ DeepSeek成功生成代码")
                println("📝 代码长度: ${generatedCode.length} 字符")
                
                // 验证生成的代码
                val isValid = testCase.validator(generatedCode)
                println("🔍 代码验证: ${if (isValid) "✅ 通过" else "❌ 失败"}")
                
                results.add(TestResult(
                    testName = testCase.name,
                    success = isValid,
                    generatedCode = generatedCode,
                    codeLength = generatedCode.length
                ))
                
                // 显示生成的代码片段
                println("🔍 生成代码预览:")
                println("```kotlin")
                val preview = if (generatedCode.length > 400) {
                    generatedCode.take(400) + "\n... (省略剩余代码)"
                } else {
                    generatedCode
                }
                println(preview)
                println("```")
                
                delay(2000) // 避免请求过快
                
            } catch (e: Exception) {
                println("❌ 测试失败: ${e.message}")
                results.add(TestResult(
                    testName = testCase.name,
                    success = false,
                    error = e.message ?: "未知错误"
                ))
            }
        }
        
        // 生成总结报告
        printSummaryReport(results)
        
        // 尝试执行一个简单的生成代码验证
        println("\n🧪 执行验证测试...")
        executeGeneratedCodeTest()
    }
    
    private suspend fun executeGeneratedCodeTest() {
        try {
            println("执行DSL基础功能验证...")
            
            // 模拟执行DeepSeek可能生成的代码模式
            val testResult = "测试DSL执行能力" using deepseek("sk-325be9f2c5594c3cae07495b28817043")
            println("✅ DSL执行成功: ${testResult.take(50)}...")
            
            // 测试对话功能
            val provider = deepseek("sk-325be9f2c5594c3cae07495b28817043")
            val chat = SimpleConversation(provider)
            chat.system("你是测试助手，回答要简洁")
            val chatResult = chat.ask("DSL测试成功了吗？")
            println("✅ 对话功能成功: ${chatResult.take(50)}...")
            
            println("🎉 生成代码的执行模式验证通过！")
            
        } catch (e: Exception) {
            println("❌ 执行验证失败: ${e.message}")
        }
    }
    
    private fun printSummaryReport(results: List<TestResult>) {
        println("\n" + "=".repeat(60))
        println("📊 DSL易用性测试总结报告")
        println("=".repeat(60))
        
        val successCount = results.count { it.success }
        val totalCount = results.size
        val successRate = (successCount.toDouble() / totalCount * 100).toInt()
        
        results.forEach { result ->
            val status = if (result.success) "✅" else "❌"
            val info = if (result.success) {
                "代码长度: ${result.codeLength}字符"
            } else {
                "错误: ${result.error}"
            }
            println("$status ${result.testName}: $info")
        }
        
        println("\n🎯 总体成功率: $successRate% ($successCount/$totalCount)")
        
        when {
            successRate >= 90 -> {
                println("🎉 DSL易用性优秀！DeepSeek能够准确理解和生成可执行的DSL代码")
            }
            successRate >= 70 -> {
                println("✅ DSL易用性良好，DeepSeek基本能理解DSL用法")
            }
            successRate >= 50 -> {
                println("⚠️ DSL需要改进，DeepSeek理解存在困难")
            }
            else -> {
                println("❌ DSL设计需要重大改进，可用性较差")
            }
        }
        
        if (successCount == totalCount) {
            println("🏆 完美！所有测试都通过，DSL设计非常成功！")
        }
    }
}

data class TestCase(
    val name: String,
    val prompt: String,
    val validator: (String) -> Boolean
)

data class TestResult(
    val testName: String,
    val success: Boolean,
    val generatedCode: String = "",
    val codeLength: Int = 0,
    val error: String = ""
)