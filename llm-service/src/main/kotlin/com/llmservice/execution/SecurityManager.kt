package com.llmservice.execution

import java.io.File
import java.util.regex.Pattern

/**
 * 代码执行安全管理器
 * 负责代码安全检查、沙箱环境管理和资源限制
 */

object ExecutionSecurityManager {
    
    // 危险操作模式
    private val DANGEROUS_PATTERNS = mapOf(
        "SYSTEM_EXIT" to listOf(
            Pattern.compile("System\\.exit\\s*\\("),
            Pattern.compile("Runtime\\.getRuntime\\(\\)\\.exit\\s*\\(")
        ),
        "PROCESS_EXECUTION" to listOf(
            Pattern.compile("ProcessBuilder\\s*\\("),
            Pattern.compile("Runtime\\.getRuntime\\(\\)\\.exec\\s*\\("),
            Pattern.compile("Process\\s+\\w+\\s*=")
        ),
        "FILE_OPERATIONS" to listOf(
            Pattern.compile("File\\s*\\([^)]*\\)\\.delete"),
            Pattern.compile("\\.deleteRecursively\\s*\\("),
            Pattern.compile("Files\\.delete\\s*\\("),
            Pattern.compile("Files\\.deleteIfExists\\s*\\(")
        ),
        "NETWORK_ACCESS" to listOf(
            Pattern.compile("Socket\\s*\\("),
            Pattern.compile("ServerSocket\\s*\\("),
            Pattern.compile("URL\\s*\\([^)]*\\)\\.openConnection"),
            Pattern.compile("HttpURLConnection"),
            Pattern.compile("URLConnection")
        ),
        "REFLECTION" to listOf(
            Pattern.compile("Class\\.forName\\s*\\("),
            Pattern.compile("\\.getDeclaredField\\s*\\("),
            Pattern.compile("\\.getDeclaredMethod\\s*\\("),
            Pattern.compile("Field\\.setAccessible\\s*\\(true\\)")
        ),
        "THREAD_MANIPULATION" to listOf(
            Pattern.compile("Thread\\.sleep\\s*\\(\\s*[0-9]{6,}"), // 超过100秒的睡眠
            Pattern.compile("while\\s*\\(\\s*true\\s*\\)\\s*\\{"), // 无限循环
            Pattern.compile("for\\s*\\(\\s*;\\s*;\\s*\\)")  // 无限for循环
        ),
        "MEMORY_ABUSE" to listOf(
            Pattern.compile("Array\\s*\\(\\s*[0-9]{7,}"), // 创建超大数组
            Pattern.compile("ByteArray\\s*\\(\\s*[0-9]{7,}"),
            Pattern.compile("IntArray\\s*\\(\\s*[0-9]{7,}")
        )
    )
    
    // 允许的包导入白名单
    private val ALLOWED_IMPORTS = setOf(
        "kotlin.*",
        "kotlinx.coroutines.*",
        "kotlinx.serialization.*",
        "java.util.*",
        "java.time.*",
        "java.math.*",
        "java.text.*",
        "com.llmservice.dsl.*",
        "com.llmservice.model.*",
        "com.llmservice.provider.*"
    )
    
    // 禁止的包导入黑名单
    private val FORBIDDEN_IMPORTS = setOf(
        "java.io.*",
        "java.nio.file.*",
        "java.net.*",
        "java.lang.reflect.*",
        "java.lang.ProcessBuilder",
        "java.lang.Runtime",
        "javax.script.*",
        "sun.*",
        "com.sun.*"
    )
    
    fun validateCodeSecurity(code: String): SecurityValidationResult {
        val violations = mutableListOf<SecurityViolation>()
        
        // 1. 检查危险操作模式
        DANGEROUS_PATTERNS.forEach { (category, patterns) ->
            patterns.forEach { pattern ->
                val matcher = pattern.matcher(code)
                if (matcher.find()) {
                    violations.add(SecurityViolation(
                        type = category,
                        message = "检测到危险操作: ${matcher.group()}",
                        line = code.substring(0, matcher.start()).count { it == '\n' } + 1,
                        severity = SecuritySeverity.HIGH
                    ))
                }
            }
        }
        
        // 2. 检查导入语句
        val importLines = code.lines().filter { it.trim().startsWith("import ") }
        importLines.forEach { importLine ->
            val importPath = importLine.substringAfter("import ").substringBefore(" //").trim()
            
            if (FORBIDDEN_IMPORTS.any { forbidden -> importPath.startsWith(forbidden.removeSuffix("*")) }) {
                violations.add(SecurityViolation(
                    type = "FORBIDDEN_IMPORT",
                    message = "禁止导入: $importPath",
                    line = code.lines().indexOf(importLine) + 1,
                    severity = SecuritySeverity.HIGH
                ))
            }
        }
        
        // 3. 检查代码复杂度
        val codeComplexity = calculateCodeComplexity(code)
        if (codeComplexity.score > 100) {
            violations.add(SecurityViolation(
                type = "COMPLEXITY",
                message = "代码复杂度过高: ${codeComplexity.score}，可能影响执行性能",
                severity = SecuritySeverity.MEDIUM
            ))
        }
        
        // 4. 检查字符串长度
        if (code.length > 50_000) {
            violations.add(SecurityViolation(
                type = "CODE_SIZE", 
                message = "代码长度超过限制: ${code.length} 字符",
                severity = SecuritySeverity.MEDIUM
            ))
        }
        
        return SecurityValidationResult(
            isSecure = violations.none { it.severity == SecuritySeverity.HIGH },
            violations = violations,
            complexity = codeComplexity
        )
    }
    
    fun createSandboxEnvironment(executionId: String): SandboxEnvironment {
        val sandboxDir = File(System.getProperty("java.io.tmpdir"), "sandbox_$executionId")
        sandboxDir.mkdirs()
        
        return SandboxEnvironment(
            workingDirectory = sandboxDir,
            maxMemoryMB = 256,
            maxExecutionTimeSeconds = 30,
            allowedFiles = emptyList(),
            blockedNetworkAccess = true
        )
    }
    
    fun cleanupSandbox(sandbox: SandboxEnvironment) {
        try {
            sandbox.workingDirectory.deleteRecursively()
        } catch (e: Exception) {
            // 记录清理失败，但不抛出异常
            println("警告: 沙箱清理失败: ${e.message}")
        }
    }
    
    private fun calculateCodeComplexity(code: String): CodeComplexity {
        var score = 0
        val lines = code.lines()
        
        // 基础复杂度：行数
        score += lines.size
        
        // 循环结构复杂度
        score += code.count { it == '{' } * 2
        score += (code.split("for").size - 1) * 3
        score += (code.split("while").size - 1) * 3
        score += (code.split("if").size - 1) * 2
        
        // 函数调用复杂度
        score += code.split("(").size - 1
        
        // 嵌套深度
        var maxNesting = 0
        var currentNesting = 0
        code.forEach { char ->
            when (char) {
                '{' -> {
                    currentNesting++
                    maxNesting = maxOf(maxNesting, currentNesting)
                }
                '}' -> currentNesting--
            }
        }
        score += maxNesting * 5
        
        return CodeComplexity(
            score = score,
            lines = lines.size,
            maxNesting = maxNesting,
            functions = code.split("fun ").size - 1,
            classes = code.split("class ").size - 1
        )
    }
}

// 数据类定义

data class SecurityValidationResult(
    val isSecure: Boolean,
    val violations: List<SecurityViolation>,
    val complexity: CodeComplexity
)

data class SecurityViolation(
    val type: String,
    val message: String,
    val line: Int = 0,
    val severity: SecuritySeverity
)

enum class SecuritySeverity {
    LOW, MEDIUM, HIGH, CRITICAL
}

data class CodeComplexity(
    val score: Int,
    val lines: Int,
    val maxNesting: Int,
    val functions: Int,
    val classes: Int
)

data class SandboxEnvironment(
    val workingDirectory: File,
    val maxMemoryMB: Int,
    val maxExecutionTimeSeconds: Int,
    val allowedFiles: List<String>,
    val blockedNetworkAccess: Boolean
)