"""Context and analysis models"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskContext(BaseModel):
    """Current task context information"""
    
    # Task identification
    task_id: Optional[str] = Field(default=None, description="Task identifier")
    task_name: str = Field(..., description="Task name or description")
    task_type: str = Field(default="general", description="Type of task")
    
    # Context
    domain: Optional[str] = Field(default=None, description="Problem domain")
    technologies: List[str] = Field(default_factory=list, description="Relevant technologies")
    constraints: List[str] = Field(default_factory=list, description="Task constraints")
    objectives: List[str] = Field(default_factory=list, description="Task objectives")
    
    # Environment
    working_directory: Optional[str] = Field(default=None, description="Working directory")
    relevant_files: List[str] = Field(default_factory=list, description="Relevant file paths")
    environment_context: Dict[str, Any] = Field(default_factory=dict, description="Environment info")
    
    # Timeline
    started_at: datetime = Field(default_factory=datetime.now, description="Task start time")
    estimated_duration: Optional[float] = Field(default=None, description="Estimated duration in hours")
    deadline: Optional[datetime] = Field(default=None, description="Task deadline")
    
    # Progress
    progress: float = Field(default=0.0, ge=0.0, le=1.0, description="Task progress (0-1)")
    status: str = Field(default="active", description="Task status")
    blockers: List[str] = Field(default_factory=list, description="Current blockers")


class MemoryInsights(BaseModel):
    """Insights about memory usage and patterns"""
    
    # Overall health
    health_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Memory system health score")
    quality_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Memory quality score")
    
    # Usage patterns
    most_used_types: List[str] = Field(default_factory=list, description="Most used memory types")
    most_accessed_memories: List[str] = Field(default_factory=list, description="Most accessed memory IDs")
    recent_trends: List[str] = Field(default_factory=list, description="Recent usage trends")
    
    # Gaps and recommendations
    knowledge_gaps: List[str] = Field(default_factory=list, description="Identified knowledge gaps")
    capability_gaps: List[str] = Field(default_factory=list, description="Missing capabilities")
    redundant_memories: List[str] = Field(default_factory=list, description="Redundant memories")
    
    # Optimization suggestions
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")
    merge_suggestions: List[Dict[str, Any]] = Field(default_factory=list, description="Memory merge suggestions")
    archive_suggestions: List[str] = Field(default_factory=list, description="Memories to archive")
    
    # Learning progress
    learning_velocity: float = Field(default=0.0, description="Rate of new memory creation")
    retention_rate: float = Field(default=0.0, description="Memory retention rate")
    skill_progression: Dict[str, float] = Field(default_factory=dict, description="Skill area progression")
    
    # Network analysis
    connection_density: float = Field(default=0.0, description="Memory network density")
    isolated_memories: List[str] = Field(default_factory=list, description="Isolated memory IDs")
    central_memories: List[str] = Field(default_factory=list, description="Central hub memories")
    
    # Performance metrics
    avg_retrieval_time: float = Field(default=0.0, description="Average memory retrieval time")
    cache_hit_rate: float = Field(default=0.0, description="Memory cache hit rate")
    storage_efficiency: float = Field(default=0.0, description="Storage efficiency score")
    
    # Generated timestamp
    analyzed_at: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    
    def get_summary(self) -> str:
        """Get human-readable insights summary"""
        lines = [
            f"🧠 Memory Insights - {self.analyzed_at.strftime('%Y-%m-%d %H:%M')}",
            "",
            f"🏥 Health Score: {self.health_score:.1f}/10",
            f"⭐ Quality Score: {self.quality_score:.1f}/10",
            "",
        ]
        
        if self.knowledge_gaps:
            lines.extend([
                "🔍 Knowledge Gaps:",
                *[f"  • {gap}" for gap in self.knowledge_gaps[:3]],
                ""
            ])
        
        if self.recommendations:
            lines.extend([
                "💡 Recommendations:",
                *[f"  • {rec}" for rec in self.recommendations[:3]],
                ""
            ])
        
        if self.recent_trends:
            lines.extend([
                "📈 Recent Trends:",
                *[f"  • {trend}" for trend in self.recent_trends[:3]],
                ""
            ])
        
        return "\n".join(lines)


class Association(BaseModel):
    """Memory association/relationship"""
    
    source_memory_id: str = Field(..., description="Source memory ID")
    target_memory_id: str = Field(..., description="Target memory ID")
    relationship_type: str = Field(..., description="Type of relationship")
    strength: float = Field(default=1.0, ge=0.0, le=1.0, description="Association strength")
    
    # Context
    discovered_at: datetime = Field(default_factory=datetime.now, description="When association was discovered")
    context: Dict[str, Any] = Field(default_factory=dict, description="Association context")
    reasoning: Optional[str] = Field(default=None, description="Why this association exists")
    
    # Validation
    validated: bool = Field(default=False, description="Whether association is validated")
    validation_count: int = Field(default=0, description="Times this association was confirmed")


class SemanticInfo(BaseModel):
    """Semantic analysis information"""
    
    # Core concepts
    primary_concepts: List[str] = Field(default_factory=list, description="Primary concepts identified")
    secondary_concepts: List[str] = Field(default_factory=list, description="Secondary concepts")
    entities: List[str] = Field(default_factory=list, description="Named entities")
    
    # Classification
    predicted_type: str = Field(..., description="Predicted memory type")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Classification confidence")
    suggested_location: str = Field(..., description="Suggested memory palace location")
    
    # Semantic features
    topics: List[str] = Field(default_factory=list, description="Topic classifications")
    sentiment: Optional[str] = Field(default=None, description="Sentiment if applicable")
    complexity_score: float = Field(default=0.0, description="Content complexity score")
    
    # Auto-generated metadata
    generated_tags: List[str] = Field(default_factory=list, description="Auto-generated tags")
    suggested_title: Optional[str] = Field(default=None, description="Suggested title")
    summary: Optional[str] = Field(default=None, description="Content summary")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }