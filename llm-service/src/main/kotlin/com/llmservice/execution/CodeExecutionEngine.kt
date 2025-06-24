package com.llmservice.execution

import kotlinx.coroutines.*
import java.io.File
import java.io.StringWriter
import java.io.PrintWriter
import java.util.concurrent.TimeUnit
import java.security.MessageDigest
import kotlin.system.measureTimeMillis

/**
 * 动态Kotlin代码执行引擎
 * 独立的代码执行系统，支持安全的代码编译和运行
 */

interface CodeExecutionEngine {
    suspend fun executeCode(request: CodeExecutionRequest): CodeExecutionResult
    suspend fun validateCode(code: String): CodeValidationResult
    fun getSupportedLanguages(): List<String>
}

class KotlinExecutionEngine : CodeExecutionEngine {
    
    private val tempDir = File(System.getProperty("java.io.tmpdir"), "kotlin-execution")
    private val maxExecutionTime = 30_000L // 30秒超时
    private val maxMemory = 256 * 1024 * 1024L // 256MB内存限制
    
    init {
        // 确保临时目录存在
        tempDir.mkdirs()
    }
    
    override suspend fun executeCode(request: CodeExecutionRequest): CodeExecutionResult {
        return withContext(Dispatchers.IO) {
            val startTime = System.currentTimeMillis()
            val executionId = generateExecutionId(request.code)
            
            try {
                // 1. 代码验证
                val validation = validateCode(request.code)
                if (!validation.isValid) {
                    return@withContext CodeExecutionResult(
                        success = false,
                        error = "代码验证失败: ${validation.errors.joinToString("; ")}",
                        executionId = executionId
                    )
                }
                
                // 2. 准备执行环境
                val workingDir = File(tempDir, executionId)
                workingDir.mkdirs()
                
                // 3. 生成完整的可执行代码
                val fullCode = generateExecutableCode(request.code, request.template)
                val sourceFile = File(workingDir, "Main.kt")
                sourceFile.writeText(fullCode)
                
                // 4. 编译代码
                val compilationResult = compileKotlinCode(sourceFile, workingDir)
                if (!compilationResult.success) {
                    return@withContext CodeExecutionResult(
                        success = false,
                        error = "编译失败: ${compilationResult.error}",
                        executionId = executionId,
                        compilationOutput = compilationResult.output
                    )
                }
                
                // 5. 执行代码
                val executionTimeMs = measureTimeMillis {
                    val runResult = executeCompiledCode(workingDir, request.arguments)
                    
                    return@withContext CodeExecutionResult(
                        success = runResult.success,
                        output = runResult.output,
                        error = runResult.error,
                        executionId = executionId,
                        executionTimeMs = System.currentTimeMillis() - startTime,
                        compilationOutput = compilationResult.output
                    )
                }
                
                // 默认返回（不应该到达这里）
                CodeExecutionResult(
                    success = false,
                    error = "未知执行路径",
                    executionId = executionId
                )
                
            } catch (e: Exception) {
                CodeExecutionResult(
                    success = false,
                    error = "执行引擎异常: ${e.message}",
                    executionId = executionId,
                    executionTimeMs = System.currentTimeMillis() - startTime
                )
            } finally {
                // 清理临时文件
                try {
                    File(tempDir, executionId).deleteRecursively()
                } catch (e: Exception) {
                    // 忽略清理错误
                }
            }
        }
    }
    
    override suspend fun validateCode(code: String): CodeValidationResult {
        val errors = mutableListOf<String>()
        val warnings = mutableListOf<String>()
        
        // 基础安全检查
        val dangerousPatterns = listOf(
            "System.exit" to "禁止使用System.exit",
            "Runtime.getRuntime" to "禁止直接调用Runtime",
            "ProcessBuilder" to "禁止创建新进程",
            "File.*delete" to "禁止删除文件操作",
            "java.net.Socket" to "禁止网络连接",
            "Thread.sleep.*[0-9]{5,}" to "禁止长时间休眠"
        )
        
        dangerousPatterns.forEach { (pattern, message) ->
            if (code.contains(Regex(pattern))) {
                errors.add(message)
            }
        }
        
        // 代码复杂度检查
        if (code.length > 10_000) {
            warnings.add("代码过长，可能影响执行性能")
        }
        
        // 检查是否包含main函数或可执行结构
        if (!code.contains("fun main") && !code.contains("runBlocking") && !code.contains("suspend fun")) {
            warnings.add("代码可能缺少可执行入口点")
        }
        
        return CodeValidationResult(
            isValid = errors.isEmpty(),
            errors = errors,
            warnings = warnings
        )
    }
    
    override fun getSupportedLanguages(): List<String> {
        return listOf("kotlin", "kt")
    }
    
    private fun generateExecutableCode(userCode: String, template: CodeTemplate?): String {
        val baseTemplate = template ?: DEFAULT_KOTLIN_TEMPLATE
        
        return baseTemplate.template
            .replace("%USER_CODE%", userCode)
            .replace("%IMPORTS%", baseTemplate.imports.joinToString("\n"))
            .replace("%DEPENDENCIES%", baseTemplate.dependencies.joinToString("\n"))
    }
    
    private suspend fun compileKotlinCode(sourceFile: File, workingDir: File): CompilationResult {
        return withContext(Dispatchers.IO) {
            try {
                val kotlincPath = findKotlinCompiler()
                if (kotlincPath == null) {
                    return@withContext CompilationResult(
                        success = false,
                        error = "未找到Kotlin编译器"
                    )
                }
                
                // 构建classpath - 包含当前项目的依赖
                val classpath = buildClasspath()
                
                val command = listOf(
                    kotlincPath,
                    "-cp", classpath,
                    "-d", workingDir.absolutePath,
                    sourceFile.absolutePath
                )
                
                val process = ProcessBuilder(command)
                    .directory(workingDir)
                    .redirectErrorStream(true)
                    .start()
                
                val output = process.inputStream.bufferedReader().readText()
                val success = process.waitFor(10, TimeUnit.SECONDS) && process.exitValue() == 0
                
                if (!success && process.isAlive) {
                    process.destroyForcibly()
                }
                
                CompilationResult(
                    success = success,
                    output = output,
                    error = if (!success) output else ""
                )
                
            } catch (e: Exception) {
                CompilationResult(
                    success = false,
                    error = "编译异常: ${e.message}"
                )
            }
        }
    }
    
    private suspend fun executeCompiledCode(workingDir: File, arguments: List<String>): ExecutionResult {
        return withContext(Dispatchers.IO) {
            try {
                val javaPath = System.getProperty("java.home") + "/bin/java"
                val classpath = "${workingDir.absolutePath}:${buildClasspath()}"
                
                val command = mutableListOf(
                    javaPath,
                    "-cp", classpath,
                    "-Xmx${maxMemory}",
                    "MainKt"  // Kotlin默认的main类名
                ).apply { addAll(arguments) }
                
                val process = ProcessBuilder(command)
                    .directory(workingDir)
                    .redirectErrorStream(false)
                    .start()
                
                // 设置超时执行
                val isFinished = process.waitFor(maxExecutionTime, TimeUnit.MILLISECONDS)
                
                if (!isFinished) {
                    process.destroyForcibly()
                    return@withContext ExecutionResult(
                        success = false,
                        error = "执行超时（${maxExecutionTime}ms）"
                    )
                }
                
                val output = process.inputStream.bufferedReader().readText()
                val error = process.errorStream.bufferedReader().readText()
                val exitCode = process.exitValue()
                
                ExecutionResult(
                    success = exitCode == 0,
                    output = output,
                    error = if (exitCode != 0) error else ""
                )
                
            } catch (e: Exception) {
                ExecutionResult(
                    success = false,
                    error = "运行异常: ${e.message}"
                )
            }
        }
    }
    
    private fun findKotlinCompiler(): String? {
        // 尝试找到kotlinc编译器
        val possiblePaths = listOf(
            "/usr/bin/kotlinc",
            "/usr/local/bin/kotlinc",
            System.getenv("KOTLIN_HOME")?.let { "$it/bin/kotlinc" },
            // 也可以尝试使用gradle编译
        ).filterNotNull()
        
        return possiblePaths.firstOrNull { File(it).exists() && File(it).canExecute() }
    }
    
    private fun buildClasspath(): String {
        // 构建包含当前项目依赖的classpath
        val currentClasspath = System.getProperty("java.class.path")
        val projectDeps = listOf(
            "build/classes/kotlin/main",
            "build/classes/java/main"
        ).map { File(it).absolutePath }
        
        return (listOf(currentClasspath) + projectDeps).joinToString(":")
    }
    
    private fun generateExecutionId(code: String): String {
        val md5 = MessageDigest.getInstance("MD5")
        val hash = md5.digest(code.toByteArray())
        return hash.joinToString("") { "%02x".format(it) }.take(8)
    }
}

// 数据类定义
data class CodeExecutionRequest(
    val code: String,
    val language: String = "kotlin",
    val template: CodeTemplate? = null,
    val arguments: List<String> = emptyList(),
    val timeout: Long? = null
)

data class CodeExecutionResult(
    val success: Boolean,
    val output: String = "",
    val error: String = "",
    val executionId: String = "",
    val executionTimeMs: Long = 0,
    val compilationOutput: String = ""
)

data class CodeValidationResult(
    val isValid: Boolean,
    val errors: List<String> = emptyList(),
    val warnings: List<String> = emptyList()
)

data class CodeTemplate(
    val name: String,
    val template: String,
    val imports: List<String> = emptyList(),
    val dependencies: List<String> = emptyList()
)

data class CompilationResult(
    val success: Boolean,
    val output: String = "",
    val error: String = ""
)

data class ExecutionResult(
    val success: Boolean,
    val output: String = "",
    val error: String = ""
)

// 默认模板
val DEFAULT_KOTLIN_TEMPLATE = CodeTemplate(
    name = "default",
    template = """
%IMPORTS%
import kotlinx.coroutines.*

%USER_CODE%

""",
    imports = listOf(
        "import kotlinx.coroutines.runBlocking",
        "import kotlinx.coroutines.delay"
    )
)