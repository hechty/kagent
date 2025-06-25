package com.llmservice.memory

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.serialization.Serializable

/**
 * 小参数模型记忆助手
 * 使用轻量级模型来辅助大模型进行记忆管理和检索
 */
class SmallModelMemoryAssistant(
    private val memoryGraph: MemoryGraph,
    private val embeddingService: EmbeddingService
) {
    
    /**
     * 为查询生成记忆上下文
     * 使用小模型分析查询并检索相关记忆
     */
    suspend fun generateMemoryContext(
        query: String,
        maxContextNodes: Int = 10,
        includeRelatedConcepts: Boolean = true
    ): MemoryContext {
        
        // 1. 分析查询意图和关键概念
        val queryAnalysis = analyzeQuery(query)
        
        // 2. 生成查询嵌入
        val queryEmbedding = embeddingService.generateEmbedding(query)
        
        // 3. 检索相似节点
        val similarNodes = memoryGraph.findSimilarNodes(
            queryEmbedding = queryEmbedding,
            threshold = 0.6f,
            limit = maxContextNodes
        )
        
        // 4. 如果需要，获取相关概念
        val relatedNodes = if (includeRelatedConcepts) {
            val allRelated = mutableSetOf<MemoryNode>()
            similarNodes.take(3).forEach { (node, _) ->
                val neighbors = memoryGraph.getNeighbors(
                    nodeId = node.id,
                    maxDistance = 2,
                    minRelationStrength = 0.4f
                )
                allRelated.addAll(neighbors)
            }
            allRelated.toList()
        } else {
            emptyList()
        }
        
        // 5. 构建记忆上下文
        return MemoryContext(
            query = query,
            queryAnalysis = queryAnalysis,
            primaryMemories = similarNodes.map { it.first },
            relatedMemories = relatedNodes,
            contextualRelevance = calculateContextualRelevance(similarNodes, relatedNodes),
            suggestions = generateMemorySuggestions(queryAnalysis, similarNodes)
        )
    }
    
    /**
     * 处理新的信息并更新记忆图
     */
    suspend fun processNewInformation(
        content: String,
        contentType: ContentType = ContentType.TEXT,
        context: String? = null
    ): ProcessingResult {
        
        // 1. 生成内容嵌入
        val embedding = embeddingService.generateEmbedding(content)
        
        // 2. 分析内容以提取关键信息
        val contentAnalysis = analyzeContent(content, contentType)
        
        // 3. 检查是否有相似的现有记忆
        val similarMemories = memoryGraph.findSimilarNodes(
            queryEmbedding = embedding,
            threshold = 0.8f,
            limit = 5
        )
        
        // 4. 决定是创建新节点还是更新现有节点
        return if (similarMemories.isNotEmpty() && similarMemories.first().second > 0.9f) {
            // 更新现有记忆
            updateExistingMemory(similarMemories.first().first, content, contentAnalysis)
        } else {
            // 创建新记忆节点
            createNewMemory(content, contentType, embedding, contentAnalysis, context)
        }
    }
    
    /**
     * 建议记忆整理策略
     */
    suspend fun suggestMemoryOrganization(): List<OrganizationSuggestion> {
        val statistics = memoryGraph.getStatistics()
        val suggestions = mutableListOf<OrganizationSuggestion>()
        
        // 建议清理低重要性记忆
        if (statistics.nodeCount > 1000) {
            suggestions.add(
                OrganizationSuggestion(
                    type = SuggestionType.CLEANUP,
                    description = "建议清理 ${statistics.nodeCount - 800} 个低重要性记忆节点",
                    priority = Priority.MEDIUM
                )
            )
        }
        
        // 建议合并相似记忆
        suggestions.add(
            OrganizationSuggestion(
                type = SuggestionType.MERGE,
                description = "检测到可能的重复记忆，建议合并以提高效率",
                priority = Priority.LOW
            )
        )
        
        // 建议加强重要关系
        if (statistics.averageConnectivity < 2.0) {
            suggestions.add(
                OrganizationSuggestion(
                    type = SuggestionType.STRENGTHEN_RELATIONS,
                    description = "记忆连接度较低，建议加强相关记忆间的关系",
                    priority = Priority.HIGH
                )
            )
        }
        
        return suggestions
    }
    
    /**
     * 生成记忆摘要报告
     */
    suspend fun generateMemoryReport(): MemoryReport {
        val stats = memoryGraph.getStatistics()
        val activeNodes = memoryGraph.getActiveNodes(20)
        
        return MemoryReport(
            totalNodes = stats.nodeCount,
            totalRelations = stats.relationCount,
            averageConnectivity = stats.averageConnectivity,
            mostImportantMemories = activeNodes.take(5),
            recentlyAccessedMemories = activeNodes
                .sortedByDescending { it.lastAccessedAt }
                .take(5),
            memoryDistribution = analyzeMemoryDistribution(activeNodes),
            healthScore = calculateMemoryHealthScore(stats)
        )
    }
    
    // 私有辅助方法
    
    private suspend fun analyzeQuery(query: String): QueryAnalysis {
        // 这里可以集成小型NLP模型来分析查询
        // 暂时使用简单的关键词提取
        val keywords = extractKeywords(query)
        val queryType = classifyQueryType(query)
        
        return QueryAnalysis(
            keywords = keywords,
            queryType = queryType,
            complexity = calculateComplexity(query),
            intent = inferIntent(query)
        )
    }
    
    private suspend fun analyzeContent(content: String, contentType: ContentType): ContentAnalysis {
        val keywords = extractKeywords(content)
        val concepts = extractConcepts(content, contentType)
        val importance = calculateImportance(content, contentType)
        
        return ContentAnalysis(
            keywords = keywords,
            concepts = concepts,
            importance = importance,
            suggestedTags = generateTags(keywords, concepts)
        )
    }
    
    private suspend fun updateExistingMemory(
        existingNode: MemoryNode,
        newContent: String,
        analysis: ContentAnalysis
    ): ProcessingResult {
        // 更新现有记忆的逻辑
        return ProcessingResult(
            success = true,
            nodeId = existingNode.id,
            action = ProcessingAction.UPDATED,
            message = "Updated existing memory with new information"
        )
    }
    
    private suspend fun createNewMemory(
        content: String,
        contentType: ContentType,
        embedding: List<Float>,
        analysis: ContentAnalysis,
        context: String?
    ): ProcessingResult {
        val newNode = MemoryNode(
            content = content,
            contentType = contentType,
            embedding = embedding,
            importance = analysis.importance,
            tags = analysis.suggestedTags,
            metadata = context?.let { mapOf("context" to it) } ?: emptyMap()
        )
        
        val success = memoryGraph.addNode(newNode)
        
        return ProcessingResult(
            success = success,
            nodeId = newNode.id,
            action = ProcessingAction.CREATED,
            message = if (success) "Created new memory node" else "Failed to create memory node"
        )
    }
    
    private fun calculateContextualRelevance(
        primaryMemories: List<Pair<MemoryNode, Float>>,
        relatedMemories: List<MemoryNode>
    ): Float {
        val primaryScore = primaryMemories.sumOf { it.second.toDouble() } / primaryMemories.size
        val relatedScore = relatedMemories.sumOf { it.importance.toDouble() } / relatedMemories.size.coerceAtLeast(1)
        return ((primaryScore + relatedScore * 0.3) / 1.3).toFloat()
    }
    
    private fun generateMemorySuggestions(
        queryAnalysis: QueryAnalysis,
        similarNodes: List<Pair<MemoryNode, Float>>
    ): List<String> {
        val suggestions = mutableListOf<String>()
        
        if (similarNodes.isNotEmpty()) {
            suggestions.add("Found ${similarNodes.size} related memories")
        }
        
        if (queryAnalysis.complexity > 0.7f) {
            suggestions.add("Complex query detected - consider breaking down into sub-questions")
        }
        
        return suggestions
    }
    
    private fun extractKeywords(text: String): List<String> {
        // 简单的关键词提取实现
        return text.lowercase()
            .split(Regex("[\\s\\p{Punct}]+"))
            .filter { it.length > 3 }
            .distinct()
    }
    
    private fun classifyQueryType(query: String): QueryType {
        return when {
            query.contains("what", ignoreCase = true) -> QueryType.FACTUAL
            query.contains("how", ignoreCase = true) -> QueryType.PROCEDURAL
            query.contains("why", ignoreCase = true) -> QueryType.CONCEPTUAL
            else -> QueryType.GENERAL
        }
    }
    
    private fun calculateComplexity(text: String): Float {
        val wordCount = text.split(Regex("\\s+")).size
        val sentenceCount = text.split(Regex("[.!?]+")).size
        return (wordCount.toFloat() / 20 + sentenceCount.toFloat() / 5).coerceAtMost(1.0f)
    }
    
    private fun inferIntent(query: String): String {
        return when {
            query.contains("remember", ignoreCase = true) -> "RECALL"
            query.contains("learn", ignoreCase = true) -> "LEARN"
            query.contains("explain", ignoreCase = true) -> "EXPLAIN"
            else -> "QUERY"
        }
    }
    
    private fun extractConcepts(content: String, contentType: ContentType): List<String> {
        // 根据内容类型提取概念
        return when (contentType) {
            ContentType.CODE -> extractCodeConcepts(content)
            ContentType.CONCEPT -> extractConceptualTerms(content)
            else -> extractKeywords(content)
        }
    }
    
    private fun extractCodeConcepts(code: String): List<String> {
        // 提取代码中的类名、函数名等
        val patterns = listOf(
            Regex("class\\s+(\\w+)"),
            Regex("fun\\s+(\\w+)"),
            Regex("val\\s+(\\w+)"),
            Regex("var\\s+(\\w+)")
        )
        return patterns.flatMap { pattern ->
            pattern.findAll(code).map { it.groupValues[1] }.toList()
        }.distinct()
    }
    
    private fun extractConceptualTerms(content: String): List<String> {
        // 提取概念性术语
        return content.split(Regex("[\\s\\p{Punct}]+"))
            .filter { it.length > 3 && it[0].isUpperCase() }
            .distinct()
    }
    
    private fun calculateImportance(content: String, contentType: ContentType): Float {
        var importance = 0.5f
        
        // 根据内容类型调整重要性
        importance += when (contentType) {
            ContentType.CONCEPT -> 0.2f
            ContentType.PROCEDURE -> 0.15f
            ContentType.FACT -> 0.1f
            else -> 0.0f
        }
        
        // 根据内容长度调整
        importance += (content.length / 1000f).coerceAtMost(0.2f)
        
        return importance.coerceAtMost(1.0f)
    }
    
    private fun generateTags(keywords: List<String>, concepts: List<String>): Set<String> {
        return (keywords.take(5) + concepts.take(3)).toSet()
    }
    
    private fun analyzeMemoryDistribution(nodes: List<MemoryNode>): Map<ContentType, Int> {
        return nodes.groupBy { it.contentType }
            .mapValues { it.value.size }
    }
    
    private fun calculateMemoryHealthScore(stats: MemoryGraphStatistics): Float {
        var score = 0.5f
        
        // 连接度评分
        if (stats.averageConnectivity > 1.5) score += 0.2f
        
        // 节点数量评分
        when (stats.nodeCount) {
            in 100..1000 -> score += 0.2f
            in 1001..5000 -> score += 0.1f
            else -> score -= 0.1f
        }
        
        // 关系数量评分
        if (stats.relationCount > stats.nodeCount) score += 0.1f
        
        return score.coerceIn(0.0f, 1.0f)
    }
}

// 数据类定义

@Serializable
data class MemoryContext(
    val query: String,
    val queryAnalysis: QueryAnalysis,
    val primaryMemories: List<MemoryNode>,
    val relatedMemories: List<MemoryNode>,
    val contextualRelevance: Float,
    val suggestions: List<String>
)

@Serializable
data class QueryAnalysis(
    val keywords: List<String>,
    val queryType: QueryType,
    val complexity: Float,
    val intent: String
)

@Serializable
enum class QueryType {
    FACTUAL, PROCEDURAL, CONCEPTUAL, GENERAL
}

@Serializable
data class ContentAnalysis(
    val keywords: List<String>,
    val concepts: List<String>,
    val importance: Float,
    val suggestedTags: Set<String>
)

@Serializable
data class ProcessingResult(
    val success: Boolean,
    val nodeId: String,
    val action: ProcessingAction,
    val message: String
)

@Serializable
enum class ProcessingAction {
    CREATED, UPDATED, MERGED, IGNORED
}

@Serializable
data class OrganizationSuggestion(
    val type: SuggestionType,
    val description: String,
    val priority: Priority
)

@Serializable
enum class SuggestionType {
    CLEANUP, MERGE, STRENGTHEN_RELATIONS, REORGANIZE
}

@Serializable
enum class Priority {
    LOW, MEDIUM, HIGH
}

@Serializable
data class MemoryReport(
    val totalNodes: Int,
    val totalRelations: Int,
    val averageConnectivity: Double,
    val mostImportantMemories: List<MemoryNode>,
    val recentlyAccessedMemories: List<MemoryNode>,
    val memoryDistribution: Map<ContentType, Int>,
    val healthScore: Float
)

/**
 * 嵌入服务接口
 * 用于生成文本的向量表示
 */
interface EmbeddingService {
    suspend fun generateEmbedding(text: String): List<Float>
    suspend fun generateBatchEmbeddings(texts: List<String>): List<List<Float>>
}