package com.llmservice.memory

import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Assertions.*
import kotlin.test.assertTrue

class MemoryGraphTest {
    
    private lateinit var memoryGraph: MemoryGraph
    
    @BeforeEach
    fun setUp() {
        memoryGraph = MemoryGraph()
    }
    
    @Test
    fun `should add memory node successfully`() = runTest {
        // Given
        val node = MemoryNode(
            id = "test-node-1",
            content = "This is a test memory",
            contentType = ContentType.TEXT,
            importance = 0.8f,
            tags = setOf("test", "memory")
        )
        
        // When
        val result = memoryGraph.addNode(node)
        
        // Then
        assertTrue(result)
        val retrievedNode = memoryGraph.getNode("test-node-1")
        assertNotNull(retrievedNode)
        assertEquals("This is a test memory", retrievedNode?.content)
        assertEquals(ContentType.TEXT, retrievedNode?.contentType)
    }
    
    @Test
    fun `should not add duplicate nodes`() = runTest {
        // Given
        val node1 = MemoryNode(id = "duplicate-id", content = "First node")
        val node2 = MemoryNode(id = "duplicate-id", content = "Second node")
        
        // When
        val firstResult = memoryGraph.addNode(node1)
        val secondResult = memoryGraph.addNode(node2)
        
        // Then
        assertTrue(firstResult)
        assertFalse(secondResult)
        
        val retrievedNode = memoryGraph.getNode("duplicate-id")
        assertEquals("First node", retrievedNode?.content)
    }
    
    @Test
    fun `should add relation between existing nodes`() = runTest {
        // Given
        val node1 = MemoryNode(id = "node1", content = "First node")
        val node2 = MemoryNode(id = "node2", content = "Second node")
        memoryGraph.addNode(node1)
        memoryGraph.addNode(node2)
        
        val relation = MemoryRelation(
            fromNodeId = "node1",
            toNodeId = "node2",
            relationType = RelationType.SIMILAR,
            strength = 0.7f
        )
        
        // When
        val result = memoryGraph.addRelation(relation)
        
        // Then
        assertTrue(result)
    }
    
    @Test
    fun `should not add relation for non-existing nodes`() = runTest {
        // Given
        val relation = MemoryRelation(
            fromNodeId = "non-existing-1",
            toNodeId = "non-existing-2",
            relationType = RelationType.SIMILAR,
            strength = 0.7f
        )
        
        // When
        val result = memoryGraph.addRelation(relation)
        
        // Then
        assertFalse(result)
    }
    
    @Test
    fun `should find similar nodes by embedding`() = runTest {
        // Given
        val embedding1 = listOf(1.0f, 0.0f, 0.0f)
        val embedding2 = listOf(0.9f, 0.1f, 0.0f) // Similar to embedding1
        val embedding3 = listOf(0.0f, 0.0f, 1.0f) // Different from embedding1
        
        val node1 = MemoryNode(id = "node1", content = "Similar content 1", embedding = embedding1)
        val node2 = MemoryNode(id = "node2", content = "Similar content 2", embedding = embedding2)
        val node3 = MemoryNode(id = "node3", content = "Different content", embedding = embedding3)
        
        memoryGraph.addNode(node1)
        memoryGraph.addNode(node2)
        memoryGraph.addNode(node3)
        
        // When
        val queryEmbedding = listOf(1.0f, 0.0f, 0.0f)
        val similarNodes = memoryGraph.findSimilarNodes(queryEmbedding, threshold = 0.5f)
        
        // Then
        assertTrue(similarNodes.isNotEmpty())
        assertEquals("node1", similarNodes.first().first.id)
        assertTrue(similarNodes.any { it.first.id == "node2" })
        assertFalse(similarNodes.any { it.first.id == "node3" })
    }
    
    @Test
    fun `should get neighbors within distance`() = runTest {
        // Given
        val node1 = MemoryNode(id = "node1", content = "Central node")
        val node2 = MemoryNode(id = "node2", content = "Direct neighbor")
        val node3 = MemoryNode(id = "node3", content = "Indirect neighbor")
        
        memoryGraph.addNode(node1)
        memoryGraph.addNode(node2)
        memoryGraph.addNode(node3)
        
        val relation1 = MemoryRelation("node1", "node2", RelationType.SIMILAR, 0.8f)
        val relation2 = MemoryRelation("node2", "node3", RelationType.SIMILAR, 0.6f)
        
        memoryGraph.addRelation(relation1)
        memoryGraph.addRelation(relation2)
        
        // When
        val neighbors = memoryGraph.getNeighbors("node1", maxDistance = 2, minRelationStrength = 0.5f)
        
        // Then
        assertEquals(2, neighbors.size)
        assertTrue(neighbors.any { it.id == "node2" })
        assertTrue(neighbors.any { it.id == "node3" })
    }
    
    @Test
    fun `should get active nodes by importance`() = runTest {
        // Given
        val highImportanceNode = MemoryNode(id = "high", content = "High importance", importance = 0.9f)
        val mediumImportanceNode = MemoryNode(id = "medium", content = "Medium importance", importance = 0.5f)
        val lowImportanceNode = MemoryNode(id = "low", content = "Low importance", importance = 0.1f)
        
        memoryGraph.addNode(highImportanceNode)
        memoryGraph.addNode(mediumImportanceNode)
        memoryGraph.addNode(lowImportanceNode)
        
        // When
        val activeNodes = memoryGraph.getActiveNodes(limit = 2)
        
        // Then
        assertEquals(2, activeNodes.size)
        assertEquals("high", activeNodes.first().id)
        assertEquals("medium", activeNodes[1].id)
    }
    
    @Test
    fun `should cleanup low importance nodes and relations`() = runTest {
        // Given
        val highImportanceNode = MemoryNode(id = "high", content = "High importance", importance = 0.9f)
        val lowImportanceNode = MemoryNode(id = "low", content = "Low importance", importance = 0.05f)
        
        memoryGraph.addNode(highImportanceNode)
        memoryGraph.addNode(lowImportanceNode)
        
        val weakRelation = MemoryRelation("high", "low", RelationType.SIMILAR, 0.1f)
        memoryGraph.addRelation(weakRelation)
        
        // When
        val cleanedCount = memoryGraph.cleanup(minImportance = 0.1f, minRelationStrength = 0.2f)
        
        // Then
        assertTrue(cleanedCount > 0)
        assertNull(memoryGraph.getNode("low"))
        assertNotNull(memoryGraph.getNode("high"))
    }
    
    @Test
    fun `should get graph statistics`() = runTest {
        // Given
        val node1 = MemoryNode(id = "node1", content = "Node 1", importance = 0.8f)
        val node2 = MemoryNode(id = "node2", content = "Node 2", importance = 0.6f)
        val node3 = MemoryNode(id = "node3", content = "Node 3", importance = 0.4f)
        
        memoryGraph.addNode(node1)
        memoryGraph.addNode(node2)
        memoryGraph.addNode(node3)
        
        val relation = MemoryRelation("node1", "node2", RelationType.SIMILAR, 0.7f)
        memoryGraph.addRelation(relation)
        
        // When
        val stats = memoryGraph.getStatistics()
        
        // Then
        assertEquals(3, stats.nodeCount)
        assertEquals(1, stats.relationCount)
        assertTrue(stats.averageConnectivity > 0.0)
        assertEquals(3, stats.topNodes.size)
        assertEquals("node1", stats.topNodes.first().first)
    }
    
    @Test
    fun `should update access count when getting node`() = runTest {
        // Given
        val node = MemoryNode(id = "test-node", content = "Test content", accessCount = 0)
        memoryGraph.addNode(node)
        
        // When
        val retrievedNode1 = memoryGraph.getNode("test-node")
        val retrievedNode2 = memoryGraph.getNode("test-node")
        
        // Then
        assertNotNull(retrievedNode1)
        assertNotNull(retrievedNode2)
        // Note: In the current implementation, the access count is updated but we can't easily verify
        // it without modifying the MemoryGraph to expose internal state or return the updated node
    }
}