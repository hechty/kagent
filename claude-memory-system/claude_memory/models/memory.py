"""Core memory data models"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import numpy as np


class MemoryType(str, Enum):
    """Memory types based on cognitive science"""
    WORKING = "working"        # Current session context
    SEMANTIC = "semantic"      # Knowledge, concepts, architecture  
    EPISODIC = "episodic"      # Specific experiences, solutions
    PROCEDURAL = "procedural"  # Scripts, tools, workflows


class MemoryScope(str, Enum):
    """Memory scope - global vs project-specific"""
    GLOBAL = "global"          # Universal capabilities and knowledge
    PROJECT = "project"        # Project-specific context and tools


class MemoryLocation(str, Enum):
    """Memory palace locations"""
    ENTRANCE_HALL = "entrance_hall"      # Core memories
    KNOWLEDGE_WING = "knowledge_wing"    # Semantic memories  
    CAPABILITY_WING = "capability_wing"  # Procedural memories
    EXPERIENCE_WING = "experience_wing"  # Episodic memories
    MEMORY_GARDEN = "memory_garden"      # Association network


class Memory(BaseModel):
    """Core memory data structure"""
    
    id: str = Field(..., description="Unique memory identifier")
    title: str = Field(..., description="Memory title")
    content: Any = Field(..., description="Memory content")
    memory_type: MemoryType = Field(..., description="Type of memory")
    scope: MemoryScope = Field(..., description="Global or project scope")
    location: MemoryLocation = Field(..., description="Memory palace location")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Semantic tags")
    importance: float = Field(default=5.0, ge=0.0, le=10.0, description="Importance score")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    # Usage statistics
    access_count: int = Field(default=0, description="Number of times accessed")
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0, description="Success rate if capability")
    
    # Relationships
    relations: List[str] = Field(default_factory=list, description="Related memory IDs")
    dependencies: List[str] = Field(default_factory=list, description="Dependency memory IDs")
    
    # Context and semantic info
    context: Dict[str, Any] = Field(default_factory=dict, description="Context information")
    embedding: Optional[List[float]] = Field(default=None, description="Semantic embedding vector")
    
    # File system info
    file_path: Optional[str] = Field(default=None, description="Associated file path")
    content_hash: Optional[str] = Field(default=None, description="Content hash for change detection")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            np.ndarray: lambda v: v.tolist() if v is not None else None
        }
        
    def update_access(self) -> None:
        """Update access statistics"""
        self.last_accessed = datetime.now()
        self.access_count += 1
        
    def add_relation(self, memory_id: str) -> None:
        """Add a relation to another memory"""
        if memory_id not in self.relations:
            self.relations.append(memory_id)
            
    def add_tag(self, tag: str) -> None:
        """Add a semantic tag"""
        if tag not in self.tags:
            self.tags.append(tag)
            
    def update_importance(self, new_importance: float) -> None:
        """Update importance score with validation"""
        self.importance = max(0.0, min(10.0, new_importance))
        self.updated_at = datetime.now()


class MemoryQuery(BaseModel):
    """Query structure for memory retrieval"""
    
    query: str = Field(..., description="Search query")
    memory_types: Optional[List[MemoryType]] = Field(default=None, description="Filter by memory types")
    scopes: Optional[List[MemoryScope]] = Field(default=None, description="Filter by scope")
    locations: Optional[List[MemoryLocation]] = Field(default=None, description="Filter by location")
    tags: Optional[List[str]] = Field(default=None, description="Filter by tags")
    
    # Search parameters
    max_results: int = Field(default=5, ge=1, le=50, description="Maximum results")
    min_relevance: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum relevance score")
    include_context: bool = Field(default=True, description="Include context in results")
    
    # Sorting and filtering
    sort_by: str = Field(default="relevance", description="Sort criteria")
    include_archived: bool = Field(default=False, description="Include archived memories")


class MemoryResult(BaseModel):
    """Memory search result with relevance scoring"""
    
    memory: Memory = Field(..., description="The memory object")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance to query")
    match_reasons: List[str] = Field(default_factory=list, description="Why this memory matched")
    context_snippet: Optional[str] = Field(default=None, description="Relevant context snippet")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }