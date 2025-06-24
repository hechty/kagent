package com.llmservice.execution

/**
 * 代码模板管理系统
 * 管理不同类型的代码执行模板，支持各种场景
 */

object CodeTemplateManager {
    
    private val templates = mutableMapOf<String, CodeTemplate>()
    
    init {
        registerBuiltInTemplates()
    }
    
    fun registerTemplate(template: CodeTemplate) {
        templates[template.name] = template
    }
    
    fun getTemplate(name: String): CodeTemplate? {
        return templates[name]
    }
    
    fun getAllTemplates(): Map<String, CodeTemplate> {
        return templates.toMap()
    }
    
    fun getTemplateNames(): List<String> {
        return templates.keys.toList()
    }
    
    private fun registerBuiltInTemplates() {
        // 基础Kotlin模板
        registerTemplate(BASIC_KOTLIN_TEMPLATE)
        
        // 协程模板
        registerTemplate(COROUTINE_TEMPLATE)
        
        // DSL测试模板
        registerTemplate(DSL_TEST_TEMPLATE)
        
        // 简单函数模板
        registerTemplate(FUNCTION_TEMPLATE)
        
        // 类定义模板
        registerTemplate(CLASS_TEMPLATE)
    }
}

// 内置模板定义

val BASIC_KOTLIN_TEMPLATE = CodeTemplate(
    name = "basic",
    template = """
%IMPORTS%

fun main() {
    %USER_CODE%
}
""",
    imports = listOf(
        "import kotlin.system.measureTimeMillis"
    )
)

val COROUTINE_TEMPLATE = CodeTemplate(
    name = "coroutine",
    template = """
%IMPORTS%

fun main() = runBlocking {
    %USER_CODE%
}
""",
    imports = listOf(
        "import kotlinx.coroutines.*"
    )
)

val DSL_TEST_TEMPLATE = CodeTemplate(
    name = "dsl_test",
    template = """
package com.llmservice.dsl

%IMPORTS%

%USER_CODE%

fun main() = runBlocking {
    try {
        println("🚀 开始执行DSL代码...")
        executeTest()
        println("✅ DSL代码执行成功！")
    } catch (e: Exception) {
        println("❌ DSL代码执行失败: ${'$'}{e.message}")
        e.printStackTrace()
    }
}
""",
    imports = listOf(
        "import kotlinx.coroutines.runBlocking",
        "import kotlinx.coroutines.delay"
    ),
    dependencies = listOf(
        "// DSL dependencies will be added by build system"
    )
)

val FUNCTION_TEMPLATE = CodeTemplate(
    name = "function",
    template = """
%IMPORTS%

%USER_CODE%

fun main() {
    println("执行用户定义的函数...")
    // 这里可以调用用户定义的函数
}
""",
    imports = listOf(
        "import kotlin.math.*"
    )
)

val CLASS_TEMPLATE = CodeTemplate(
    name = "class",
    template = """
%IMPORTS%

%USER_CODE%

fun main() {
    println("执行用户定义的类...")
    // 这里可以实例化和使用用户定义的类
}
""",
    imports = listOf(
        "import kotlin.reflect.full.*"
    )
)