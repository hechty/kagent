package com.llmservice.config

import kotlin.time.Duration
import kotlin.time.Duration.Companion.seconds

/**
 * 改进4: DSL配置管理
 * 统一管理超时、重试、环境等配置，让DSL更加健壮
 */
data class DSLConfig(
    // 超时配置
    val requestTimeout: Duration = 90.seconds,
    val connectTimeout: Duration = 10.seconds,
    val socketTimeout: Duration = 90.seconds,
    
    // 重试配置
    val maxRetries: Int = 2,
    val retryOnTimeout: Boolean = true,
    val retryOnServerError: Boolean = true,
    
    // 环境配置
    val ignoreSystemProxy: Boolean = true,  // 对本地调用忽略代理
    val enableDetailedErrors: Boolean = true,
    val enableMetrics: Boolean = false,
    
    // LLM特定配置
    val defaultTemperature: Double = 0.7,
    val defaultMaxTokens: Int? = null,
    val enableStreaming: Boolean = false
) {
    companion object {
        /**
         * 开发环境配置 - 更快的超时，详细错误
         */
        val DEVELOPMENT = DSLConfig(
            requestTimeout = 30.seconds,
            connectTimeout = 5.seconds,
            enableDetailedErrors = true,
            enableMetrics = true
        )
        
        /**
         * 生产环境配置 - 更长的超时，简化错误
         */
        val PRODUCTION = DSLConfig(
            requestTimeout = 120.seconds,
            connectTimeout = 15.seconds,
            enableDetailedErrors = false,
            enableMetrics = true,
            maxRetries = 3
        )
        
        /**
         * 快速测试配置 - 最短超时
         */
        val QUICK_TEST = DSLConfig(
            requestTimeout = 10.seconds,
            connectTimeout = 3.seconds,
            maxRetries = 1,
            enableDetailedErrors = true
        )
    }
}

/**
 * 环境检测和自动配置
 */
object EnvironmentDetector {
    fun detectEnvironment(): String {
        return when {
            System.getProperty("env") == "prod" -> "production"
            System.getProperty("env") == "test" -> "test"
            else -> "development"
        }
    }
    
    fun getRecommendedConfig(): DSLConfig {
        return when (detectEnvironment()) {
            "production" -> DSLConfig.PRODUCTION
            "test" -> DSLConfig.QUICK_TEST
            else -> DSLConfig.DEVELOPMENT
        }
    }
    
    /**
     * 检测代理配置冲突
     */
    fun hasProxyConflict(): Boolean {
        val proxyVars = listOf("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY")
        return proxyVars.any { System.getenv(it)?.isNotEmpty() == true }
    }
    
    /**
     * 提供代理配置建议
     */
    fun getProxyAdvice(): String {
        return if (hasProxyConflict()) {
            "检测到系统代理配置，这可能影响本地服务调用。建议在DSL调用时禁用代理。"
        } else {
            "代理配置正常"
        }
    }
}