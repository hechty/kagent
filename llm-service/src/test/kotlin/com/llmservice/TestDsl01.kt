package com.llmservice

/**
 * @author 黄传伟
 * @date 2025/6/24
 * @description
 */
class TestDsl01 {
    @Test
    fun testDSLBuilderCreation() {
        llm(llmService) { }
    }
}