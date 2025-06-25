package com.llmservice.memory

import kotlinx.serialization.Serializable
import java.time.Instant
import java.util.UUID

/**
 * 记忆图节点，表示一个独立的记忆单元
 * 每个节点包含内容、向量嵌入、元数据和关系信息
 */
@Serializable
data class MemoryNode(
    val id: String = UUID.randomUUID().toString(),
    val content: String,
    val contentType: ContentType = ContentType.TEXT,
    val embedding: List<Float> = emptyList(),
    val metadata: Map<String, String> = emptyMap(),
    val createdAt: Long = Instant.now().epochSecond,
    val lastAccessedAt: Long = Instant.now().epochSecond,
    val accessCount: Int = 0,
    val importance: Float = 0.5f, // 0.0 - 1.0
    val tags: Set<String> = emptySet()
) {
    
    /**
     * 计算节点的衰减重要性
     * 基于时间衰减、访问频率和固有重要性
     */
    fun getDecayedImportance(currentTime: Long = Instant.now().epochSecond): Float {
        val timeDiff = currentTime - lastAccessedAt
        val daysPassed = timeDiff / (24 * 3600)
        val timeDecay = kotlin.math.exp(-daysPassed * 0.01).toFloat() // 时间衰减因子
        val accessBoost = kotlin.math.min(accessCount * 0.1f, 1.0f) // 访问次数加成
        return importance * timeDecay * (1 + accessBoost)
    }
    
    /**
     * 更新访问信息
     */
    fun accessed(): MemoryNode {
        return copy(
            lastAccessedAt = Instant.now().epochSecond,
            accessCount = accessCount + 1
        )
    }
}

/**
 * 内容类型枚举
 */
@Serializable
enum class ContentType {
    TEXT,
    CODE,
    CONCEPT,
    FACT,
    PROCEDURE,
    RELATIONSHIP,
    CONTEXT
}