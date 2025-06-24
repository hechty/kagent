package com.llmservice.dsl

import kotlin.test.Test
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class BasicDSLTest {
    
    @Test
    fun testDSLBuilderCreation() {
        val builder = LLMBuilder()
        assertNotNull(builder)
    }
    
    @Test
    fun testLLMConfigCreation() {
        val config = LLMConfig()
        assertTrue(config.temperature >= 0.0)
        assertTrue(config.timeout.inWholeSeconds > 0)
    }
}