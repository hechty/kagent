"""
Enhanced vector storage backend with real semantic search
"""

import logging
import numpy as np
from typing import List, Optional, Dict, Any

from ..models.memory import Memory, MemoryQuery, MemoryResult
from ..core.config import MemoryConfig

# Try to import scikit-learn with fallback
try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("scikit-learn not available, using fallback similarity calculation")

logger = logging.getLogger(__name__)

# Global model instance for efficiency
_sentence_model = None

def fallback_cosine_similarity(a, b):
    """Fallback cosine similarity calculation without scikit-learn"""
    dot_product = np.dot(a.flatten(), b.flatten())
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)


def get_embedding_via_api(text: str) -> Optional[np.ndarray]:
    """Get embedding using SiliconFlow API"""
    try:
        import requests
        
        # SiliconFlow API配置
        api_url = "https://api.siliconflow.cn/v1/embeddings"
        api_key = "sk-lpuljmmwvjwpkluhkglyuqvqhnpzyeumgftjmjlnkxmgjqct"
        model_name = "Pro/BAAI/bge-m3"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model_name,
            "input": text,
            "encoding_format": "float"
        }
        
        response = requests.post(api_url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            embedding = result["data"][0]["embedding"]
            return np.array(embedding, dtype=np.float32)
        else:
            logger.warning(f"API embedding failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.warning(f"API embedding error: {e}")
        return None


def get_sentence_model():
    """Get or initialize the sentence transformer model with API fallback"""
    global _sentence_model
    if _sentence_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded sentence transformer model: all-MiniLM-L6-v2")
        except ImportError:
            logger.warning("sentence-transformers not available, will try API embedding")
            _sentence_model = None
        except Exception as e:
            logger.warning(f"Failed to load sentence transformer model: {e}, will try API embedding")
            _sentence_model = None
    return _sentence_model


class VectorStore:
    """
    Enhanced vector storage for semantic memory search
    
    Features:
    - Real semantic embeddings using sentence-transformers
    - Cosine similarity calculation
    - Fallback to keyword search if models unavailable
    - Efficient caching and indexing
    """
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self._memory_embeddings = {}  # memory_id -> embedding
        self._memory_cache = {}       # memory_id -> memory
        self._model = get_sentence_model()
        
        logger.info(f"VectorStore initialized with semantic search: {self._model is not None}")
    
    def store_memory(self, memory: Memory) -> None:
        """Store memory with semantic embedding"""
        try:
            # Cache the memory
            self._memory_cache[memory.id] = memory
            
            # Generate embedding
            embedding = self._generate_embedding(memory)
            if embedding is not None:
                self._memory_embeddings[memory.id] = embedding
                logger.debug(f"Stored memory {memory.id} with semantic embedding")
            else:
                logger.warning(f"Failed to generate embedding for memory {memory.id}")
            
        except Exception as e:
            logger.error(f"Failed to store memory in vector store: {e}")
            raise
    
    def search_memories(self, query: MemoryQuery) -> List[MemoryResult]:
        """Search memories using semantic similarity"""
        try:
            if not self._memory_cache:
                logger.warning("No memories in cache")
                return []
            
            results = []
            
            # Generate query embedding for semantic search
            query_embedding = None
            
            # Try local model first
            if self._model is not None:
                try:
                    query_embedding = self._model.encode([query.query])[0]
                    logger.debug("Generated local query embedding")
                except Exception as e:
                    logger.warning(f"Local query encoding failed: {e}, trying API")
            
            # Fallback to API embedding for query
            if query_embedding is None:
                query_embedding = get_embedding_via_api(query.query)
                if query_embedding is not None:
                    logger.debug("Generated API query embedding")
            
            # Search through all memories
            for memory_id, memory in self._memory_cache.items():
                relevance = self._calculate_relevance(memory, query, query_embedding)
                
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
            
            logger.info(f"Semantic search for '{query.query}' found {len(results)} results")
            return results[:query.max_results]
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    def _generate_embedding(self, memory: Memory) -> Optional[np.ndarray]:
        """Generate semantic embedding for a memory"""
        # Combine title, content, and tags for embedding
        text_content = f"{memory.title} {memory.content} {' '.join(memory.tags)}"
        
        # Try local model first
        if self._model is not None:
            try:
                embedding = self._model.encode([text_content])[0]
                logger.debug(f"Generated local embedding for memory {memory.id}")
                return embedding
            except Exception as e:
                logger.warning(f"Local embedding failed: {e}, trying API")
        
        # Fallback to API embedding
        api_embedding = get_embedding_via_api(text_content)
        if api_embedding is not None:
            logger.debug(f"Generated API embedding for memory {memory.id}")
            return api_embedding
        
        logger.warning(f"Failed to generate any embedding for memory {memory.id}")
        return None
    
    def _calculate_relevance(self, memory: Memory, query: MemoryQuery, query_embedding: Optional[np.ndarray]) -> float:
        """Calculate relevance score between memory and query"""
        relevance_score = 0.0
        
        # Semantic similarity (primary method)
        if query_embedding is not None and memory.id in self._memory_embeddings:
            try:
                memory_embedding = self._memory_embeddings[memory.id]
                
                if SKLEARN_AVAILABLE:
                    semantic_similarity = cosine_similarity(
                        query_embedding.reshape(1, -1),
                        memory_embedding.reshape(1, -1)
                    )[0][0]
                else:
                    # Use fallback cosine similarity
                    semantic_similarity = fallback_cosine_similarity(query_embedding, memory_embedding)
                
                # Semantic similarity contributes 70% of the score
                relevance_score += float(semantic_similarity) * 0.7
                
                logger.debug(f"Semantic similarity for memory {memory.id}: {semantic_similarity:.3f}")
                
            except Exception as e:
                logger.warning(f"Failed to calculate semantic similarity: {e}")
        
        # Fallback to keyword-based relevance (30% of score)
        keyword_score = self._calculate_keyword_relevance(memory, query)
        relevance_score += keyword_score * 0.3
        
        # Importance bonus (up to 10% boost)
        importance_bonus = (memory.importance / 10.0) * 0.1
        relevance_score += importance_bonus
        
        return min(1.0, relevance_score)
    
    def _calculate_keyword_relevance(self, memory: Memory, query: MemoryQuery) -> float:
        """Calculate keyword-based relevance (fallback method)"""
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
        
        score += title_overlap * 0.1
        score += content_overlap * 0.05
        
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
        
        # Add semantic match reason if available
        if self._model is not None and memory.id in self._memory_embeddings:
            reasons.append("Semantic similarity")
        
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
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            "total_memories": len(self._memory_cache),
            "embeddings_generated": len(self._memory_embeddings),
            "semantic_search_available": self._model is not None,
            "model_name": "all-MiniLM-L6-v2" if self._model else None
        }
