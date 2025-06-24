"""Memory snapshot models for awakening"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .memory import Memory, MemoryType
from .capability import Capability


class ProjectOverview(BaseModel):
    """Project overview information"""
    
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    type: str = Field(..., description="Project type")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    current_phase: str = Field(default="active", description="Current project phase")
    last_activity: datetime = Field(default_factory=datetime.now, description="Last activity timestamp")
    
    # Key metrics
    total_memories: int = Field(default=0, description="Total memories in project")
    total_capabilities: int = Field(default=0, description="Total capabilities")
    complexity_score: float = Field(default=0.0, description="Project complexity score")


class ContextSummary(BaseModel):
    """Current context summary"""
    
    active_task: Optional[str] = Field(default=None, description="Current active task")
    recent_actions: List[str] = Field(default_factory=list, description="Recent actions taken")
    current_focus: Optional[str] = Field(default=None, description="Current area of focus")
    pending_tasks: List[str] = Field(default_factory=list, description="Pending tasks")
    
    # Working memory
    session_memories: List[str] = Field(default_factory=list, description="Session memory IDs")
    active_capabilities: List[str] = Field(default_factory=list, description="Currently active capabilities")
    
    # Environment
    working_directory: Optional[str] = Field(default=None, description="Current working directory")
    environment_vars: Dict[str, str] = Field(default_factory=dict, description="Relevant environment variables")


class MemoryStatistics(BaseModel):
    """Memory system statistics"""
    
    # Overall stats
    total_memories: int = Field(default=0, description="Total memories")
    global_memories: int = Field(default=0, description="Global scope memories")
    project_memories: int = Field(default=0, description="Project scope memories")
    
    # By type
    semantic_count: int = Field(default=0, description="Semantic memories")
    episodic_count: int = Field(default=0, description="Episodic memories")
    procedural_count: int = Field(default=0, description="Procedural memories")
    working_count: int = Field(default=0, description="Working memories")
    
    # Quality metrics
    avg_importance: float = Field(default=0.0, description="Average importance score")
    avg_access_frequency: float = Field(default=0.0, description="Average access frequency")
    memory_health_score: float = Field(default=0.0, description="Overall memory health")
    
    # Relationships
    total_relations: int = Field(default=0, description="Total memory relationships")
    avg_relations_per_memory: float = Field(default=0.0, description="Average relations per memory")


class Suggestion(BaseModel):
    """AI suggestion for action or memory"""
    
    type: str = Field(..., description="Suggestion type")
    action: str = Field(..., description="Suggested action")
    reason: str = Field(..., description="Reason for suggestion")
    priority: float = Field(default=5.0, ge=0.0, le=10.0, description="Suggestion priority")
    
    # Context
    related_memories: List[str] = Field(default_factory=list, description="Related memory IDs")
    required_capabilities: List[str] = Field(default_factory=list, description="Required capabilities")
    estimated_effort: Optional[str] = Field(default=None, description="Estimated effort")


class ImportantReminder(BaseModel):
    """Important reminder from memory"""
    
    title: str = Field(..., description="Reminder title")
    content: str = Field(..., description="Reminder content")
    urgency: float = Field(default=5.0, ge=0.0, le=10.0, description="Urgency level")
    memory_id: str = Field(..., description="Source memory ID")
    created_at: datetime = Field(..., description="When reminder was created")


class MemorySnapshot(BaseModel):
    """Complete memory snapshot for awakening"""
    
    # Core information
    project_overview: ProjectOverview = Field(..., description="Project overview")
    context_summary: ContextSummary = Field(..., description="Current context")
    
    # Memory content
    recent_memories: List[Memory] = Field(default_factory=list, description="Recently accessed memories")
    important_memories: List[Memory] = Field(default_factory=list, description="High importance memories")
    active_capabilities: List[Capability] = Field(default_factory=list, description="Available capabilities")
    
    # Guidance
    important_reminders: List[ImportantReminder] = Field(default_factory=list, description="Important reminders")
    suggested_actions: List[Suggestion] = Field(default_factory=list, description="Suggested next actions")
    
    # Analytics
    memory_statistics: MemoryStatistics = Field(default_factory=MemoryStatistics, description="Memory stats")
    
    # Metadata
    snapshot_time: datetime = Field(default_factory=datetime.now, description="Snapshot creation time")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the snapshot"""
        lines = [
            f"🧠 Memory Snapshot - {self.snapshot_time.strftime('%Y-%m-%d %H:%M')}",
            "",
            f"📁 Project: {self.project_overview.name}",
            f"📊 Total Memories: {self.memory_statistics.total_memories}",
            f"⚡ Active Capabilities: {len(self.active_capabilities)}",
            "",
        ]
        
        if self.context_summary.active_task:
            lines.extend([
                f"🎯 Current Task: {self.context_summary.active_task}",
                ""
            ])
        
        if self.important_reminders:
            lines.extend([
                "🔔 Important Reminders:",
                *[f"  • {reminder.title}" for reminder in self.important_reminders[:3]],
                ""
            ])
        
        if self.suggested_actions:
            lines.extend([
                "💡 Suggested Actions:",
                *[f"  • {action.action}" for action in self.suggested_actions[:3]],
                ""
            ])
        
        return "\n".join(lines)
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }