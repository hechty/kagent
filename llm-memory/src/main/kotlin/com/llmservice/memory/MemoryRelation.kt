package com.llmservice.memory

import kotlinx.serialization.Serializable
import java.time.Instant

/**
 * 记忆节点间的关系
 * 表示两个记忆节点之间的语义或逻辑连接
 */
@Serializable
data class MemoryRelation(
    val fromNodeId: String,
    val toNodeId: String,
    val relationType: RelationType,
    val strength: Float = 0.5f, // 关系强度 0.0 - 1.0
    val metadata: Map<String, String> = emptyMap(),
    val createdAt: Long = Instant.now().epochSecond,
    val lastReinforcedAt: Long = Instant.now().epochSecond,
    val reinforcementCount: Int = 0
) {
    
    /**
     * 计算关系的当前强度（考虑时间衰减）
     */
    fun getCurrentStrength(currentTime: Long = Instant.now().epochSecond): Float {
        val timeDiff = currentTime - lastReinforcedAt
        val daysPassed = timeDiff / (24 * 3600)
        val timeDecay = kotlin.math.exp(-daysPassed * 0.005).toFloat() // 关系衰减比节点慢
        val reinforcementBoost = kotlin.math.min(reinforcementCount * 0.05f, 0.5f)
        return (strength + reinforcementBoost) * timeDecay
    }
    
    /**
     * 加强关系
     */
    fun reinforce(strengthIncrease: Float = 0.1f): MemoryRelation {
        return copy(
            strength = kotlin.math.min(strength + strengthIncrease, 1.0f),
            lastReinforcedAt = Instant.now().epochSecond,
            reinforcementCount = reinforcementCount + 1
        )
    }
}

/**
 * 关系类型枚举
 */
@Serializable
enum class RelationType {
    // 语义关系
    SIMILAR,        // 相似
    OPPOSITE,       // 相反
    CONTAINS,       // 包含
    PART_OF,        // 属于
    
    // 逻辑关系
    CAUSES,         // 导致
    IMPLIES,        // 暗示
    PRECEDES,       // 先于
    FOLLOWS,        // 后于
    
    // 层次关系
    GENERALIZES,    // 泛化
    SPECIALIZES,    // 特化
    EXTENDS,        // 扩展
    
    // 上下文关系
    CONTEXT,        // 上下文
    EXAMPLE,        // 示例
    REFERENCE,      // 引用
    
    // 自定义关系
    CUSTOM
}