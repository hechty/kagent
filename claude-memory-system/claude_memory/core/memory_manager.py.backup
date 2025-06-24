"""
Core Memory Manager - The heart of Claude's persistent memory system
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..models.memory import Memory, MemoryType, MemoryScope, MemoryQuery, MemoryResult
from ..models.capability import Capability, ExecutionResult
from ..models.snapshot import MemorySnapshot, ProjectOverview, ContextSummary, MemoryStatistics
from ..models.context import TaskContext, MemoryInsights
from ..models.snapshot import Suggestion
from ..storage.vector_store import VectorStore
from ..storage.file_store import FileStore
from ..engines.semantic_engine import SemanticEngine
from ..engines.capability_engine import CapabilityEngine
from .config import MemoryConfig


logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Claude Code Memory Manager
    
    Provides persistent memory capabilities with:
    - Dual-scope memory (global vs project)
    - Semantic search and retrieval
    - Capability execution and management
    - Intelligent memory organization
    - Context-aware suggestions
    """
    
    def __init__(self, 
                 project_path: Optional[Path] = None,
                 config: Optional[MemoryConfig] = None):
        """
        Initialize memory manager
        
        Args:
            project_path: Path to current project (None for global-only)
            config: Memory system configuration
        """
        # Setup configuration
        self.config = config or MemoryConfig()
        if project_path:
            self.config.storage.project_memory_path = project_path / ".memory"
        self.config.setup_paths()
        
        # Initialize storage backends
        self._vector_store = VectorStore(self.config)
        self._file_store = FileStore(self.config)
        
        # Initialize engines
        self._semantic_engine = SemanticEngine(self.config)
        self._capability_engine = CapabilityEngine(self.config)
        
        # Runtime state
        self._session_id = str(uuid.uuid4())
        self._current_context: Optional[TaskContext] = None
        self._awakened = False
        
        # Performance tracking
        self._operation_stats = {
            "memories_created": 0,
            "memories_retrieved": 0,
            "capabilities_executed": 0,
            "search_operations": 0,
        }
        
        logger.info(f"Memory manager initialized with session {self._session_id}")
    
    def awaken(self, context: Optional[str] = None) -> MemorySnapshot:
        """
        🌅 Awaken - Activate core memories and establish context
        
        This is the first method to call in any session. It:
        1. Loads essential project and global memories
        2. Analyzes current context and environment
        3. Prepares frequently-used capabilities
        4. Returns a comprehensive snapshot of the memory state
        
        Args:
            context: Optional context description for this session
            
        Returns:
            MemorySnapshot: Complete overview of activated memories
        """
        logger.info(f"Awakening memory system with context: {context}")
        start_time = datetime.now()
        
        try:
            # Detect project context
            project_overview = self._detect_project_context()
            
            # Load core memories
            recent_memories = self._load_recent_memories(limit=10)
            important_memories = self._load_important_memories(limit=10)
            
            # Load active capabilities
            active_capabilities = self._load_active_capabilities()
            
            # Generate context summary
            context_summary = self._generate_context_summary(context)
            
            # Generate suggestions and reminders
            suggestions = self._generate_suggestions(context)
            reminders = self._generate_reminders()
            
            # Calculate statistics
            stats = self._calculate_memory_statistics()
            
            # Create snapshot
            snapshot = MemorySnapshot(
                project_overview=project_overview,
                context_summary=context_summary,
                recent_memories=recent_memories,
                important_memories=important_memories,
                active_capabilities=active_capabilities,
                suggested_actions=suggestions,
                important_reminders=reminders,
                memory_statistics=stats,
                session_id=self._session_id
            )
            
            self._awakened = True
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Memory system awakened in {duration:.2f}s")
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to awaken memory system: {e}")
            raise
    
    def remember(self,
                content: Any,
                memory_type: Union[str, MemoryType],
                title: Optional[str] = None,
                tags: Optional[List[str]] = None,
                importance: float = 5.0,
                scope: Union[str, MemoryScope] = MemoryScope.PROJECT,
                location: Optional[str] = None,
                context: Optional[Dict[str, Any]] = None) -> str:
        """
        🧠 Remember - Store information in the memory system
        
        Args:
            content: The content to remember (text, code, data, etc.)
            memory_type: Type of memory (semantic, episodic, procedural, working)
            title: Optional title for the memory
            tags: Optional semantic tags
            importance: Importance score (0-10)
            scope: Memory scope (global or project)
            location: Specific memory palace location
            context: Additional context information
            
        Returns:
            str: Unique memory ID
        """
        if not self._awakened:
            logger.warning("Memory system not awakened, awakening now...")
            self.awaken()
        
        logger.info(f"Storing new {memory_type} memory: {title or 'Untitled'}")
        
        try:
            # Convert string enums
            if isinstance(memory_type, str):
                memory_type = MemoryType(memory_type.lower())
            if isinstance(scope, str):
                scope = MemoryScope(scope.lower())
            
            # Generate semantic analysis
            semantic_info = self._semantic_engine.analyze_content(content)
            
            # Auto-generate title if not provided
            if not title:
                title = semantic_info.suggested_title or f"{memory_type.value} memory"
            
            # Auto-generate tags if enabled
            if self.config.enable_auto_tagging:
                auto_tags = semantic_info.generated_tags
                tags = list(set((tags or []) + auto_tags))
            
            # Determine location
            if not location:
                location = semantic_info.suggested_location
            
            # Create memory object
            memory = Memory(
                id=str(uuid.uuid4()),
                title=title,
                content=content,
                memory_type=memory_type,
                scope=scope,
                location=location,
                tags=tags or [],
                importance=max(0.0, min(10.0, importance)),
                context=context or {},
                embedding=None  # Will be set by vector store
            )
            
            # Store in vector database for semantic search
            self._vector_store.store_memory(memory)
            
            # Store in file system for persistence
            self._file_store.store_memory(memory)
            
            # Find and create automatic relationships
            if self.config.enable_auto_relations:
                self._create_automatic_relations(memory)
            
            # Update statistics
            self._operation_stats["memories_created"] += 1
            
            logger.info(f"Successfully stored memory {memory.id}")
            return memory.id
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise
    
    def recall(self,
              query: str,
              memory_types: Optional[List[Union[str, MemoryType]]] = None,
              scopes: Optional[List[Union[str, MemoryScope]]] = None,
              max_results: int = 5,
              min_relevance: float = 0.7,
              include_context: bool = True) -> List[MemoryResult]:
        """
        💭 Recall - Search and retrieve relevant memories
        
        Args:
            query: Search query (natural language)
            memory_types: Filter by memory types
            scopes: Filter by memory scopes
            max_results: Maximum number of results
            min_relevance: Minimum relevance score
            include_context: Include context in results
            
        Returns:
            List[MemoryResult]: Relevant memories with relevance scores
        """
        if not self._awakened:
            logger.warning("Memory system not awakened, awakening now...")
            self.awaken()
        
        logger.info(f"Searching memories for: '{query}'")
        
        try:
            # Convert string enums
            if memory_types:
                memory_types = [MemoryType(t) if isinstance(t, str) else t for t in memory_types]
            if scopes:
                scopes = [MemoryScope(s) if isinstance(s, str) else s for s in scopes]
            
            # Create query object
            memory_query = MemoryQuery(
                query=query,
                memory_types=memory_types,
                scopes=scopes,
                max_results=max_results,
                min_relevance=min_relevance,
                include_context=include_context
            )
            
            # Perform semantic search
            results = self._vector_store.search_memories(memory_query)
            
            # Update access statistics for retrieved memories
            for result in results:
                result.memory.update_access()
                self._file_store.update_memory(result.memory)
            
            # Update statistics
            self._operation_stats["search_operations"] += 1
            self._operation_stats["memories_retrieved"] += len(results)
            
            logger.info(f"Found {len(results)} relevant memories")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            raise
    
    def invoke_capability(self,
                         capability_name: str,
                         params: Optional[Dict[str, Any]] = None,
                         auto_remember: bool = True) -> ExecutionResult:
        """
        ⚡ Invoke Capability - Execute a stored capability
        
        Args:
            capability_name: Name or description of capability
            params: Execution parameters
            auto_remember: Whether to remember the execution experience
            
        Returns:
            ExecutionResult: Result of capability execution
        """
        if not self._awakened:
            logger.warning("Memory system not awakened, awakening now...")
            self.awaken()
        
        logger.info(f"Invoking capability: {capability_name}")
        
        try:
            # Find the capability
            capability_memories = self.recall(
                query=capability_name,
                memory_types=[MemoryType.PROCEDURAL],
                max_results=3,
                min_relevance=0.6
            )
            
            if not capability_memories:
                raise ValueError(f"Capability '{capability_name}' not found")
            
            # Get the best matching capability
            best_match = capability_memories[0]
            capability_content = best_match.memory.content
            
            # Parse capability if it's stored as JSON
            if isinstance(capability_content, str):
                try:
                    capability_data = json.loads(capability_content)
                    capability = Capability(**capability_data)
                except (json.JSONDecodeError, TypeError):
                    # Treat as raw script content
                    capability = Capability(
                        name=capability_name,
                        description=f"Script: {capability_name}",
                        capability_type="script",
                        content=capability_content,
                        interface={}
                    )
            elif isinstance(capability_content, dict):
                capability = Capability(**capability_content)
            else:
                capability = capability_content
            
            # Execute the capability
            result = self._capability_engine.execute_capability(capability, params or {})
            
            # Remember the execution experience if requested
            if auto_remember and result.success:
                execution_memory = {
                    "capability": capability_name,
                    "params": params,
                    "result": result.output,
                    "execution_time": result.duration,
                    "timestamp": result.timestamp.isoformat()
                }
                
                self.remember(
                    content=execution_memory,
                    memory_type=MemoryType.EPISODIC,
                    title=f"Executed {capability_name}",
                    tags=["execution", "capability", capability_name],
                    importance=6.0,
                    context={"execution_result": "success"}
                )
            
            # Update statistics
            self._operation_stats["capabilities_executed"] += 1
            
            logger.info(f"Capability execution completed: success={result.success}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to invoke capability: {e}")
            raise
    
    def reflect(self) -> MemoryInsights:
        """
        🤔 Reflect - Analyze memory patterns and provide insights
        
        Returns:
            MemoryInsights: Analysis of memory usage and recommendations
        """
        if not self._awakened:
            logger.warning("Memory system not awakened, awakening now...")
            self.awaken()
        
        logger.info("Analyzing memory patterns and usage")
        
        try:
            # Load all memories for analysis
            all_memories = self._file_store.load_all_memories()
            
            # Calculate health scores
            health_score = self._calculate_health_score(all_memories)
            quality_score = self._calculate_quality_score(all_memories)
            
            # Analyze usage patterns
            usage_patterns = self._analyze_usage_patterns(all_memories)
            
            # Identify gaps and opportunities
            knowledge_gaps = self._identify_knowledge_gaps(all_memories)
            capability_gaps = self._identify_capability_gaps(all_memories)
            
            # Generate recommendations
            recommendations = self._generate_optimization_recommendations(all_memories)
            
            # Create insights object
            insights = MemoryInsights(
                health_score=health_score,
                quality_score=quality_score,
                most_used_types=usage_patterns["most_used_types"],
                most_accessed_memories=usage_patterns["most_accessed"],
                recent_trends=usage_patterns["trends"],
                knowledge_gaps=knowledge_gaps,
                capability_gaps=capability_gaps,
                recommendations=recommendations
            )
            
            logger.info(f"Memory analysis completed: health={health_score:.1f}, quality={quality_score:.1f}")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to analyze memories: {e}")
            raise
    
    def suggest(self, context: Optional[str] = None) -> List[Suggestion]:
        """
        💡 Suggest - Provide context-aware suggestions
        
        Args:
            context: Optional context for suggestions
            
        Returns:
            List[Suggestion]: Relevant suggestions
        """
        if not self._awakened:
            logger.warning("Memory system not awakened, awakening now...")
            self.awaken()
        
        logger.info(f"Generating suggestions for context: {context}")
        
        try:
            suggestions = []
            
            # Context-based suggestions
            if context:
                relevant_memories = self.recall(context, max_results=5)
                for memory_result in relevant_memories:
                    memory = memory_result.memory
                    if memory.memory_type == MemoryType.PROCEDURAL:
                        suggestions.append(Suggestion(
                            type="capability",
                            action=f"Use {memory.title}",
                            reason=f"Relevant to current context",
                            priority=memory.importance,
                            related_memories=[memory.id]
                        ))
            
            # General workflow suggestions
            recent_memories = self._load_recent_memories(limit=5)
            if recent_memories:
                last_memory = recent_memories[0]
                if last_memory.memory_type == MemoryType.SEMANTIC:
                    suggestions.append(Suggestion(
                        type="action",
                        action="Create related capability",
                        reason="Convert knowledge to executable capability",
                        priority=6.0,
                        related_memories=[last_memory.id]
                    ))
            
            # Maintenance suggestions
            if self._operation_stats["memories_created"] > 10:
                suggestions.append(Suggestion(
                    type="maintenance",
                    action="Run memory analysis",
                    reason="Optimize memory organization",
                    priority=4.0
                ))
            
            logger.info(f"Generated {len(suggestions)} suggestions")
            return suggestions[:5]  # Limit to top 5
            
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            return []
    
    # Private helper methods
    def _detect_project_context(self) -> ProjectOverview:
        """Detect current project context"""
        cwd = Path.cwd()
        project_name = cwd.name
        
        # Try to detect project type
        project_type = "general"
        technologies = []
        
        if (cwd / "pyproject.toml").exists():
            project_type = "python"
            technologies.append("Python")
        elif (cwd / "package.json").exists():
            project_type = "javascript"
            technologies.append("JavaScript")
        elif (cwd / "build.gradle.kts").exists():
            project_type = "kotlin"
            technologies.append("Kotlin")
        elif (cwd / "Cargo.toml").exists():
            project_type = "rust"
            technologies.append("Rust")
        
        return ProjectOverview(
            name=project_name,
            description=f"Project in {cwd}",
            type=project_type,
            technologies=technologies
        )
    
    def _load_recent_memories(self, limit: int = 10) -> List[Memory]:
        """Load recently accessed memories"""
        try:
            all_memories = self._file_store.load_all_memories()
            # Sort by last_accessed descending
            recent = sorted(all_memories, key=lambda m: m.last_accessed, reverse=True)
            return recent[:limit]
        except Exception:
            return []
    
    def _load_important_memories(self, limit: int = 10) -> List[Memory]:
        """Load high importance memories"""
        try:
            all_memories = self._file_store.load_all_memories()
            # Sort by importance descending
            important = sorted(all_memories, key=lambda m: m.importance, reverse=True)
            return important[:limit]
        except Exception:
            return []
    
    def _load_active_capabilities(self) -> List[Capability]:
        """Load active capabilities"""
        try:
            procedural_memories = self._file_store.load_memories_by_type(MemoryType.PROCEDURAL)
            capabilities = []
            
            for memory in procedural_memories:
                try:
                    if isinstance(memory.content, dict):
                        capability = Capability(**memory.content)
                        capabilities.append(capability)
                except Exception:
                    continue
            
            return capabilities[:10]  # Limit to 10 most recent
        except Exception:
            return []
    
    def _generate_context_summary(self, context: Optional[str]) -> ContextSummary:
        """Generate current context summary"""
        return ContextSummary(
            active_task=context,
            working_directory=str(Path.cwd()),
            session_memories=[],
            active_capabilities=[]
        )
    
    def _generate_suggestions(self, context: Optional[str]) -> List[Suggestion]:
        """Generate initial suggestions"""
        suggestions = []
        
        if context:
            suggestions.append(Suggestion(
                type="search",
                action=f"Search for memories related to: {context}",
                reason="Find relevant past experiences",
                priority=7.0
            ))
        
        return suggestions
    
    def _generate_reminders(self) -> List:
        """Generate important reminders"""
        # This would analyze memories for important reminders
        return []
    
    def _calculate_memory_statistics(self) -> MemoryStatistics:
        """Calculate memory system statistics"""
        try:
            all_memories = self._file_store.load_all_memories()
            
            stats = MemoryStatistics(
                total_memories=len(all_memories),
                global_memories=len([m for m in all_memories if m.scope == MemoryScope.GLOBAL]),
                project_memories=len([m for m in all_memories if m.scope == MemoryScope.PROJECT]),
                semantic_count=len([m for m in all_memories if m.memory_type == MemoryType.SEMANTIC]),
                episodic_count=len([m for m in all_memories if m.memory_type == MemoryType.EPISODIC]),
                procedural_count=len([m for m in all_memories if m.memory_type == MemoryType.PROCEDURAL]),
                working_count=len([m for m in all_memories if m.memory_type == MemoryType.WORKING])
            )
            
            if all_memories:
                stats.avg_importance = sum(m.importance for m in all_memories) / len(all_memories)
                stats.avg_access_frequency = sum(m.access_count for m in all_memories) / len(all_memories)
            
            return stats
        except Exception:
            return MemoryStatistics()
    
    def _create_automatic_relations(self, memory: Memory) -> None:
        """Create automatic relationships for a new memory"""
        # This would use semantic similarity to find related memories
        pass
    
    def _calculate_health_score(self, memories: List[Memory]) -> float:
        """Calculate overall memory system health"""
        if not memories:
            return 0.0
        
        # Simple health calculation based on various factors
        score = 5.0  # Base score
        
        # Bonus for having memories
        if len(memories) > 10:
            score += 2.0
        
        # Bonus for diverse memory types
        types = set(m.memory_type for m in memories)
        score += len(types) * 0.5
        
        # Penalty for old unused memories
        now = datetime.now()
        old_memories = [m for m in memories if (now - m.last_accessed).days > 30]
        if old_memories:
            score -= min(2.0, len(old_memories) * 0.1)
        
        return max(0.0, min(10.0, score))
    
    def _calculate_quality_score(self, memories: List[Memory]) -> float:
        """Calculate memory quality score"""
        if not memories:
            return 0.0
        
        # Quality based on importance and access patterns
        avg_importance = sum(m.importance for m in memories) / len(memories)
        
        # Normalize to 0-10 scale
        return min(10.0, avg_importance)
    
    def _analyze_usage_patterns(self, memories: List[Memory]) -> Dict[str, Any]:
        """Analyze memory usage patterns"""
        type_counts = {}
        for memory in memories:
            type_counts[memory.memory_type.value] = type_counts.get(memory.memory_type.value, 0) + 1
        
        most_used_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        most_accessed = sorted(memories, key=lambda m: m.access_count, reverse=True)
        
        return {
            "most_used_types": [t[0] for t in most_used_types[:3]],
            "most_accessed": [m.id for m in most_accessed[:5]],
            "trends": ["Memory creation is active"]
        }
    
    def _identify_knowledge_gaps(self, memories: List[Memory]) -> List[str]:
        """Identify potential knowledge gaps"""
        gaps = []
        
        # Check for missing capability types
        has_data_analysis = any("data" in m.tags for m in memories)
        if not has_data_analysis:
            gaps.append("Data analysis capabilities")
        
        has_testing = any("test" in m.tags for m in memories)
        if not has_testing:
            gaps.append("Testing frameworks and methods")
        
        return gaps
    
    def _identify_capability_gaps(self, memories: List[Memory]) -> List[str]:
        """Identify missing capabilities"""
        capabilities = [m for m in memories if m.memory_type == MemoryType.PROCEDURAL]
        
        gaps = []
        if len(capabilities) < 3:
            gaps.append("Need more automation scripts")
        
        return gaps
    
    def _generate_optimization_recommendations(self, memories: List[Memory]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Check for unused memories
        unused = [m for m in memories if m.access_count == 0]
        if len(unused) > 5:
            recommendations.append(f"Archive {len(unused)} unused memories")
        
        # Check for missing tags
        untagged = [m for m in memories if not m.tags]
        if len(untagged) > 3:
            recommendations.append(f"Add tags to {len(untagged)} memories")
        
        return recommendations