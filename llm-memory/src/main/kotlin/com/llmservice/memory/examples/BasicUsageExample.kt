package com.llmservice.memory.examples

import com.llmservice.memory.*
import kotlinx.coroutines.runBlocking

/**
 * 基本使用示例
 * 演示如何使用 LLM Memory 模块的核心功能
 */
class BasicUsageExample {
    
    fun runExample() = runBlocking {
        println("=== LLM Memory 基本使用示例 ===\n")
        
        // 1. 创建记忆图
        val memoryGraph = MemoryGraph()
        println("✓ 创建记忆图")
        
        // 2. 添加记忆节点
        addSampleMemories(memoryGraph)
        
        // 3. 建立记忆关系
        addSampleRelations(memoryGraph)
        
        // 4. 演示记忆检索
        demonstrateRetrieval(memoryGraph)
        
        // 5. 演示邻居查找
        demonstrateNeighborSearch(memoryGraph)
        
        // 6. 演示记忆统计
        demonstrateStatistics(memoryGraph)
        
        // 7. 演示记忆清理
        demonstrateCleanup(memoryGraph)
    }
    
    private suspend fun addSampleMemories(memoryGraph: MemoryGraph) {
        println("\n--- 添加示例记忆 ---")
        
        val memories = listOf(
            MemoryNode(
                id = "kotlin-basic",
                content = "Kotlin是一种现代的编程语言，运行在JVM上，具有简洁的语法和强大的类型推断。",
                contentType = ContentType.CONCEPT,
                embedding = listOf(0.8f, 0.2f, 0.1f, 0.9f, 0.3f),
                importance = 0.8f,
                tags = setOf("kotlin", "programming", "jvm")
            ),
            MemoryNode(
                id = "coroutines-concept",
                content = "Kotlin协程是轻量级的并发原语，允许编写异步代码而不阻塞线程。",
                contentType = ContentType.CONCEPT,
                embedding = listOf(0.7f, 0.8f, 0.2f, 0.6f, 0.4f),
                importance = 0.9f,
                tags = setOf("kotlin", "coroutines", "async", "concurrency")
            ),
            MemoryNode(
                id = "suspend-function",
                content = "suspend函数是可以被暂停和恢复的函数，是协程的核心组成部分。",
                contentType = ContentType.PROCEDURE,
                embedding = listOf(0.6f, 0.9f, 0.1f, 0.5f, 0.3f),
                importance = 0.7f,
                tags = setOf("kotlin", "coroutines", "suspend", "function")
            ),
            MemoryNode(
                id = "data-class",
                content = "data class是Kotlin中用于保存数据的特殊类，自动生成equals、hashCode和toString方法。",
                contentType = ContentType.CONCEPT,
                embedding = listOf(0.9f, 0.1f, 0.3f, 0.8f, 0.2f),
                importance = 0.6f,
                tags = setOf("kotlin", "data-class", "syntax")
            ),
            MemoryNode(
                id = "type-inference",
                content = "Kotlin的类型推断允许编译器自动推断变量类型，减少冗余的类型声明。",
                contentType = ContentType.CONCEPT,
                embedding = listOf(0.8f, 0.3f, 0.4f, 0.7f, 0.1f),
                importance = 0.5f,
                tags = setOf("kotlin", "type-inference", "compiler")
            )
        )
        
        memories.forEach { memory ->
            val success = memoryGraph.addNode(memory)
            println("${if (success) "✓" else "✗"} 添加记忆: ${memory.id}")
        }
    }
    
    private suspend fun addSampleRelations(memoryGraph: MemoryGraph) {
        println("\n--- 建立记忆关系 ---")
        
        val relations = listOf(
            MemoryRelation(
                fromNodeId = "kotlin-basic",
                toNodeId = "coroutines-concept",
                relationType = RelationType.CONTAINS,
                strength = 0.8f
            ),
            MemoryRelation(
                fromNodeId = "coroutines-concept",
                toNodeId = "suspend-function",
                relationType = RelationType.CONTAINS,
                strength = 0.9f
            ),
            MemoryRelation(
                fromNodeId = "kotlin-basic",
                toNodeId = "data-class",
                relationType = RelationType.CONTAINS,
                strength = 0.7f
            ),
            MemoryRelation(
                fromNodeId = "kotlin-basic",
                toNodeId = "type-inference",
                relationType = RelationType.CONTAINS,
                strength = 0.6f
            ),
            MemoryRelation(
                fromNodeId = "data-class",
                toNodeId = "type-inference",
                relationType = RelationType.SIMILAR,
                strength = 0.5f
            )
        )
        
        relations.forEach { relation ->
            val success = memoryGraph.addRelation(relation)
            println("${if (success) "✓" else "✗"} 建立关系: ${relation.fromNodeId} ${relation.relationType} ${relation.toNodeId}")
        }
    }
    
    private suspend fun demonstrateRetrieval(memoryGraph: MemoryGraph) {
        println("\n--- 记忆检索演示 ---")
        
        // 使用向量相似性检索
        val queryEmbedding = listOf(0.7f, 0.8f, 0.2f, 0.6f, 0.4f) // 类似协程的向量
        val similarMemories = memoryGraph.findSimilarNodes(queryEmbedding, threshold = 0.6f, limit = 3)
        
        println("查询向量: $queryEmbedding")
        println("找到 ${similarMemories.size} 个相似记忆:")
        similarMemories.forEach { (node, similarity) ->
            println("  - ${node.id} (相似度: ${"%.2f".format(similarity)})")
            println("    内容: ${node.content.take(50)}...")
        }
    }
    
    private suspend fun demonstrateNeighborSearch(memoryGraph: MemoryGraph) {
        println("\n--- 邻居查找演示 ---")
        
        val startNodeId = "kotlin-basic"
        val neighbors = memoryGraph.getNeighbors(
            nodeId = startNodeId,
            maxDistance = 2,
            minRelationStrength = 0.5f
        )
        
        println("从节点 '$startNodeId' 开始查找邻居:")
        println("找到 ${neighbors.size} 个相关记忆:")
        neighbors.forEach { neighbor ->
            println("  - ${neighbor.id}")
            println("    内容: ${neighbor.content.take(50)}...")
            println("    重要性: ${"%.2f".format(neighbor.importance)}")
        }
    }
    
    private suspend fun demonstrateStatistics(memoryGraph: MemoryGraph) {
        println("\n--- 记忆统计演示 ---")
        
        val stats = memoryGraph.getStatistics()
        println("记忆图统计信息:")
        println("  - 节点总数: ${stats.nodeCount}")
        println("  - 关系总数: ${stats.relationCount}")
        println("  - 平均连接度: ${"%.2f".format(stats.averageConnectivity)}")
        println("  - 最重要的记忆:")
        stats.topNodes.take(3).forEach { (nodeId, importance) ->
            println("    * $nodeId (重要性: ${"%.2f".format(importance)})")
        }
        
        // 获取活跃记忆
        val activeMemories = memoryGraph.getActiveNodes(limit = 3)
        println("  - 当前最活跃的记忆:")
        activeMemories.forEach { memory ->
            println("    * ${memory.id} (衰减重要性: ${"%.2f".format(memory.getDecayedImportance())})")
        }
    }
    
    private suspend fun demonstrateCleanup(memoryGraph: MemoryGraph) {
        println("\n--- 记忆清理演示 ---")
        
        // 添加一个低重要性的记忆用于演示清理
        val lowImportanceMemory = MemoryNode(
            id = "low-importance",
            content = "这是一个不重要的记忆",
            importance = 0.05f
        )
        memoryGraph.addNode(lowImportanceMemory)
        
        val statsBefore = memoryGraph.getStatistics()
        println("清理前: ${statsBefore.nodeCount} 个节点, ${statsBefore.relationCount} 个关系")
        
        val cleanedCount = memoryGraph.cleanup(
            minImportance = 0.1f,
            minRelationStrength = 0.3f
        )
        
        val statsAfter = memoryGraph.getStatistics()
        println("清理后: ${statsAfter.nodeCount} 个节点, ${statsAfter.relationCount} 个关系")
        println("清理了 $cleanedCount 个低价值项目")
    }
}

/**
 * 运行示例的入口函数
 */
fun main() {
    val example = BasicUsageExample()
    example.runExample()
}