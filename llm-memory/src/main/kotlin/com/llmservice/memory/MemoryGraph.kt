package com.llmservice.memory

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import org.jgrapht.Graph
import org.jgrapht.graph.DefaultDirectedWeightedGraph
import org.jgrapht.graph.DefaultWeightedEdge
import java.util.concurrent.ConcurrentHashMap

/**
 * 记忆图：管理记忆节点和它们之间的关系
 * 使用图结构来表示和操作记忆网络
 */
class MemoryGraph {
    
    private val nodes = ConcurrentHashMap<String, MemoryNode>()
    private val relations = ConcurrentHashMap<String, MemoryRelation>()
    private val graph: Graph<String, DefaultWeightedEdge> = DefaultDirectedWeightedGraph(DefaultWeightedEdge::class.java)
    
    /**
     * 添加记忆节点
     */
    suspend fun addNode(node: MemoryNode): Boolean {
        return if (nodes.putIfAbsent(node.id, node) == null) {
            graph.addVertex(node.id)
            true
        } else {
            false
        }
    }
    
    /**
     * 获取记忆节点
     */
    suspend fun getNode(nodeId: String): MemoryNode? {
        return nodes[nodeId]?.accessed()?.also { accessedNode ->
            nodes[nodeId] = accessedNode
        }
    }
    
    /**
     * 添加关系
     */
    suspend fun addRelation(relation: MemoryRelation): Boolean {
        if (!nodes.containsKey(relation.fromNodeId) || !nodes.containsKey(relation.toNodeId)) {
            return false
        }
        
        val relationKey = "${relation.fromNodeId}->${relation.toNodeId}-${relation.relationType}"
        val existingRelation = relations[relationKey]
        
        return if (existingRelation == null) {
            relations[relationKey] = relation
            val edge = graph.addEdge(relation.fromNodeId, relation.toNodeId)
            if (edge != null) {
                graph.setEdgeWeight(edge, relation.strength.toDouble())
            }
            true
        } else {
            // 加强已存在的关系
            relations[relationKey] = existingRelation.reinforce()
            val edge = graph.getEdge(relation.fromNodeId, relation.toNodeId)
            if (edge != null) {
                graph.setEdgeWeight(edge, existingRelation.getCurrentStrength().toDouble())
            }
            true
        }
    }
    
    /**
     * 根据内容相似度查找相关节点
     */
    suspend fun findSimilarNodes(
        queryEmbedding: List<Float>,
        threshold: Float = 0.7f,
        limit: Int = 10
    ): List<Pair<MemoryNode, Float>> {
        return nodes.values
            .map { node ->
                val similarity = cosineSimilarity(queryEmbedding, node.embedding)
                node to similarity
            }
            .filter { it.second >= threshold }
            .sortedByDescending { it.second }
            .take(limit)
    }
    
    /**
     * 获取节点的邻居节点
     */
    suspend fun getNeighbors(
        nodeId: String,
        maxDistance: Int = 2,
        minRelationStrength: Float = 0.3f
    ): List<MemoryNode> {
        val visited = mutableSetOf<String>()
        val result = mutableListOf<MemoryNode>()
        val queue = mutableListOf(nodeId to 0)
        
        while (queue.isNotEmpty()) {
            val (currentId, distance) = queue.removeAt(0)
            
            if (currentId in visited || distance > maxDistance) continue
            visited.add(currentId)
            
            if (distance > 0) {
                nodes[currentId]?.let { result.add(it) }
            }
            
            if (distance < maxDistance) {
                graph.outgoingEdgesOf(currentId).forEach { edge ->
                    val targetId = graph.getEdgeTarget(edge)
                    val weight = graph.getEdgeWeight(edge).toFloat()
                    if (weight >= minRelationStrength && targetId !in visited) {
                        queue.add(targetId to distance + 1)
                    }
                }
            }
        }
        
        return result
    }
    
    /**
     * 根据重要性和新鲜度获取活跃节点
     */
    suspend fun getActiveNodes(limit: Int = 50): List<MemoryNode> {
        return nodes.values
            .sortedByDescending { it.getDecayedImportance() }
            .take(limit)
    }
    
    /**
     * 清理低重要性的节点和关系
     */
    suspend fun cleanup(
        minImportance: Float = 0.1f,
        minRelationStrength: Float = 0.2f
    ): Int {
        var cleanedCount = 0
        
        // 清理低重要性节点
        val nodesToRemove = nodes.values
            .filter { it.getDecayedImportance() < minImportance }
            .map { it.id }
        
        nodesToRemove.forEach { nodeId ->
            removeNode(nodeId)
            cleanedCount++
        }
        
        // 清理弱关系
        val relationsToRemove = relations.values
            .filter { it.getCurrentStrength() < minRelationStrength }
        
        relationsToRemove.forEach { relation ->
            val relationKey = "${relation.fromNodeId}->${relation.toNodeId}-${relation.relationType}"
            relations.remove(relationKey)
            val edge = graph.getEdge(relation.fromNodeId, relation.toNodeId)
            if (edge != null) {
                graph.removeEdge(edge)
            }
            cleanedCount++
        }
        
        return cleanedCount
    }
    
    /**
     * 移除节点及其所有关系
     */
    private suspend fun removeNode(nodeId: String) {
        nodes.remove(nodeId)
        graph.removeVertex(nodeId)
        
        // 移除相关的关系
        relations.keys.removeAll { key ->
            key.startsWith("$nodeId->") || key.contains("->$nodeId-")
        }
    }
    
    /**
     * 获取图的统计信息
     */
    suspend fun getStatistics(): MemoryGraphStatistics {
        return MemoryGraphStatistics(
            nodeCount = nodes.size,
            relationCount = relations.size,
            averageConnectivity = if (nodes.isEmpty()) 0.0 else relations.size.toDouble() / nodes.size,
            topNodes = nodes.values
                .sortedByDescending { it.getDecayedImportance() }
                .take(5)
                .map { it.id to it.getDecayedImportance() }
        )
    }
    
    /**
     * 导出节点流
     */
    fun exportNodes(): Flow<MemoryNode> = flow {
        nodes.values.forEach { emit(it) }
    }
    
    /**
     * 导出关系流
     */
    fun exportRelations(): Flow<MemoryRelation> = flow {
        relations.values.forEach { emit(it) }
    }
    
    /**
     * 计算余弦相似度
     */
    private fun cosineSimilarity(a: List<Float>, b: List<Float>): Float {
        if (a.isEmpty() || b.isEmpty() || a.size != b.size) return 0f
        
        var dotProduct = 0f
        var normA = 0f
        var normB = 0f
        
        for (i in a.indices) {
            dotProduct += a[i] * b[i]
            normA += a[i] * a[i]
            normB += b[i] * b[i]
        }
        
        val denominator = kotlin.math.sqrt(normA * normB)
        return if (denominator == 0f) 0f else dotProduct / denominator
    }
}

/**
 * 记忆图统计信息
 */
data class MemoryGraphStatistics(
    val nodeCount: Int,
    val relationCount: Int,
    val averageConnectivity: Double,
    val topNodes: List<Pair<String, Float>>
)