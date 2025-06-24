"""
Vector storage backend for semantic search
"""

import logging
from typing import List, Optional

from ..models.memory import Memory, MemoryQuery, MemoryResult
from ..core.config import MemoryConfig

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector storage for semantic memory search
    
    Note: This is a simplified implementation.
    In production, this would use ChromaDB or similar vector database.
    """
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self._memory_embeddings = {}  # memory_id -> embedding
        self._memory_cache = {}       # memory_id -> memory
    
    def store_memory(self, memory: Memory) -> None:
        """Store memory with semantic embedding"""
        try:
            # In a real implementation, this would:
            # 1. Generate embedding using sentence transformer
            # 2. Store in vector database (ChromaDB, etc.)
            # 3. Create indices for fast search
            
            # For now, just cache the memory
            self._memory_cache[memory.id] = memory
            
            # Simulate embedding storage
            self._memory_embeddings[memory.id] = self._mock_embedding(memory)
            
            logger.debug(f"Stored memory {memory.id} in vector store")
            
        except Exception as e:
            logger.error(f"Failed to store memory in vector store: {e}")
            raise
    
    def search_memories(self, query: MemoryQuery) -> List[MemoryResult]:
        """Search memories using semantic similarity"""
        try:
            results = []
            
            # Simple keyword-based search for now
            # In production, this would use vector similarity search
            for memory_id, memory in self._memory_cache.items():
                relevance = self._calculate_relevance(memory, query)
                
                if relevance >= query.min_relevance:
                    # Apply filters
                    if query.memory_types and memory.memory_type not in query.memory_types:
                        continue
                    if query.scopes and memory.scope not in query.scopes:
                        continue
                    if query.tags and not any(tag in memory.tags for tag in query.tags):
                        continue
                    
                    result = MemoryResult(
                        memory=memory,
                        relevance_score=relevance,
                        match_reasons=self._get_match_reasons(memory, query),
                        context_snippet=self._get_context_snippet(memory, query)
                    )
                    results.append(result)
            
            # Sort by relevance
            results.sort(key=lambda r: r.relevance_score, reverse=True)
            
            return results[:query.max_results]
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    def _mock_embedding(self, memory: Memory) -> List[float]:
        """Generate mock embedding (in production, use real embedding model)"""
        # This would use sentence-transformers in production
        content_str = f"{memory.title} {memory.content} {' '.join(memory.tags)}"
        
        # Mock embedding based on content hash
        import hashlib
        hash_obj = hashlib.md5(content_str.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert to mock 384-dimensional vector
        embedding = []
        for i in range(0, min(len(hash_hex), 96), 2):
            val = int(hash_hex[i:i+2], 16) / 255.0  # Normalize to 0-1
            embedding.extend([val] * 4)  # Repeat to get 384 dimensions
        
        # Pad or truncate to exact dimension
        while len(embedding) < 384:
            embedding.append(0.0)
        
        return embedding[:384]
    
    def _calculate_relevance(self, memory: Memory, query: MemoryQuery) -> float:
        """Calculate relevance score between memory and query"""
        score = 0.0
        query_lower = query.query.lower()
        
        # Title match
        if query_lower in memory.title.lower():
            score += 0.4
        
        # Content match
        content_str = str(memory.content).lower()
        if query_lower in content_str:
            score += 0.3
        
        # Tag match
        for tag in memory.tags:
            if query_lower in tag.lower():
                score += 0.2
                break
        
        # Context match
        for key, value in memory.context.items():
            if query_lower in str(value).lower():
                score += 0.1
                break
        
        # Word overlap bonus
        query_words = set(query_lower.split())
        title_words = set(memory.title.lower().split())
        content_words = set(content_str.split())
        
        title_overlap = len(query_words & title_words) / max(len(query_words), 1)
        content_overlap = len(query_words & content_words) / max(len(query_words), 1)
        
        score += title_overlap * 0.2
        score += content_overlap * 0.1
        
        # Importance bonus
        score += (memory.importance / 10.0) * 0.1
        
        return min(1.0, score)
    
    def _get_match_reasons(self, memory: Memory, query: MemoryQuery) -> List[str]:
        """Get reasons why this memory matched the query"""
        reasons = []
        query_lower = query.query.lower()
        
        if query_lower in memory.title.lower():
            reasons.append("Title match")
        
        if query_lower in str(memory.content).lower():
            reasons.append("Content match")
        
        for tag in memory.tags:
            if query_lower in tag.lower():
                reasons.append(f"Tag match: {tag}")
                break
        
        if memory.importance > 7.0:
            reasons.append("High importance")
        
        return reasons
    
    def _get_context_snippet(self, memory: Memory, query: MemoryQuery) -> Optional[str]:
        """Get relevant context snippet from memory content"""
        if not query.include_context:
            return None
        
        content_str = str(memory.content)
        query_lower = query.query.lower()
        
        # Find first occurrence of query in content
        content_lower = content_str.lower()
        pos = content_lower.find(query_lower)
        
        if pos >= 0:
            # Extract snippet around the match
            start = max(0, pos - 50)
            end = min(len(content_str), pos + len(query.query) + 50)
            snippet = content_str[start:end]
            
            if start > 0:
                snippet = "..." + snippet
            if end < len(content_str):
                snippet = snippet + "..."
            
            return snippet
        
        # If no direct match, return first 100 characters
        if len(content_str) > 100:
            return content_str[:100] + "..."
        
        return content_str