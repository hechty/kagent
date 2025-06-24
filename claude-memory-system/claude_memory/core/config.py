"""Memory system configuration"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class StorageConfig(BaseModel):
    """Storage configuration"""
    
    # Base paths
    global_memory_path: Path = Field(default=Path.home() / ".claude_memory", description="Global memory storage")
    project_memory_path: Optional[Path] = Field(default=None, description="Project-specific memory storage")
    
    # Database settings
    vector_db_type: str = Field(default="chroma", description="Vector database type")
    vector_dimension: int = Field(default=384, description="Embedding vector dimension")
    
    # File formats
    memory_format: str = Field(default="json", description="Memory storage format")
    backup_enabled: bool = Field(default=True, description="Enable automatic backups")
    backup_interval: int = Field(default=3600, description="Backup interval in seconds")


class SearchConfig(BaseModel):
    """Search and retrieval configuration"""
    
    # Embedding model
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="Sentence transformer model")
    embedding_cache_size: int = Field(default=1000, description="Embedding cache size")
    
    # Search parameters
    default_max_results: int = Field(default=5, description="Default max search results")
    default_min_relevance: float = Field(default=0.7, description="Default minimum relevance")
    semantic_weight: float = Field(default=0.7, description="Weight of semantic similarity")
    keyword_weight: float = Field(default=0.3, description="Weight of keyword matching")
    
    # Performance
    search_timeout: float = Field(default=5.0, description="Search timeout in seconds")
    cache_results: bool = Field(default=True, description="Cache search results")


class MaintenanceConfig(BaseModel):
    """Memory maintenance configuration"""
    
    # Cleanup settings
    auto_cleanup: bool = Field(default=True, description="Enable automatic cleanup")
    cleanup_interval: int = Field(default=86400, description="Cleanup interval in seconds")
    
    # Archive settings
    archive_threshold_days: int = Field(default=90, description="Days before archiving unused memories")
    archive_importance_threshold: float = Field(default=3.0, description="Importance threshold for archiving")
    
    # Optimization
    optimize_on_startup: bool = Field(default=True, description="Optimize indices on startup")
    rebuild_indices_interval: int = Field(default=604800, description="Index rebuild interval in seconds")
    
    # Quality control
    detect_duplicates: bool = Field(default=True, description="Automatically detect duplicate memories")
    merge_similar_threshold: float = Field(default=0.95, description="Similarity threshold for merging")


class SecurityConfig(BaseModel):
    """Security and privacy configuration"""
    
    # Access control
    require_authentication: bool = Field(default=False, description="Require authentication")
    session_timeout: int = Field(default=3600, description="Session timeout in seconds")
    
    # Data protection
    encrypt_sensitive: bool = Field(default=True, description="Encrypt sensitive memories")
    anonymize_personal_data: bool = Field(default=True, description="Anonymize personal information")
    
    # Audit
    audit_log_enabled: bool = Field(default=True, description="Enable audit logging")
    audit_log_retention: int = Field(default=2592000, description="Audit log retention in seconds")


class MemoryConfig(BaseModel):
    """Complete memory system configuration"""
    
    # Core settings
    project_name: Optional[str] = Field(default=None, description="Current project name")
    session_id: Optional[str] = Field(default=None, description="Current session ID")
    
    # Component configurations
    storage: StorageConfig = Field(default_factory=StorageConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    maintenance: MaintenanceConfig = Field(default_factory=MaintenanceConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    
    # Feature flags
    enable_semantic_analysis: bool = Field(default=True, description="Enable semantic analysis")
    enable_auto_tagging: bool = Field(default=True, description="Enable automatic tagging")
    enable_auto_relations: bool = Field(default=True, description="Enable automatic relationship detection")
    enable_capability_execution: bool = Field(default=True, description="Enable capability execution")
    
    # Logging and debugging
    log_level: str = Field(default="INFO", description="Logging level")
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    performance_monitoring: bool = Field(default=True, description="Enable performance monitoring")
    
    @classmethod
    def from_file(cls, config_path: Path) -> "MemoryConfig":
        """Load configuration from file"""
        import yaml
        
        if not config_path.exists():
            # Create default config
            config = cls()
            config.save_to_file(config_path)
            return config
        
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return cls(**data)
    
    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to file"""
        import yaml
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(self.dict(), f, default_flow_style=False, indent=2)
    
    def setup_paths(self) -> None:
        """Setup storage paths"""
        # Ensure global memory path exists
        self.storage.global_memory_path.mkdir(parents=True, exist_ok=True)
        
        # Setup project memory path if specified
        if self.project_name and not self.storage.project_memory_path:
            current_dir = Path.cwd()
            self.storage.project_memory_path = current_dir / ".memory"
        
        if self.storage.project_memory_path:
            self.storage.project_memory_path.mkdir(parents=True, exist_ok=True)
    
    def get_storage_path(self, scope: str) -> Path:
        """Get storage path for given scope"""
        if scope == "global":
            return self.storage.global_memory_path
        elif scope == "project" and self.storage.project_memory_path:
            return self.storage.project_memory_path
        else:
            return self.storage.global_memory_path
    
    def get_environment_overrides(self) -> Dict[str, any]:
        """Get configuration overrides from environment variables"""
        overrides = {}
        
        # Check for common environment overrides
        if "CLAUDE_MEMORY_PATH" in os.environ:
            overrides["storage.global_memory_path"] = Path(os.environ["CLAUDE_MEMORY_PATH"])
        
        if "CLAUDE_PROJECT_NAME" in os.environ:
            overrides["project_name"] = os.environ["CLAUDE_PROJECT_NAME"]
        
        if "CLAUDE_DEBUG" in os.environ:
            overrides["debug_mode"] = os.environ["CLAUDE_DEBUG"].lower() in ("true", "1", "yes")
        
        if "CLAUDE_LOG_LEVEL" in os.environ:
            overrides["log_level"] = os.environ["CLAUDE_LOG_LEVEL"].upper()
        
        return overrides
    
    def apply_overrides(self, overrides: Dict[str, any]) -> None:
        """Apply configuration overrides"""
        for key, value in overrides.items():
            if "." in key:
                # Handle nested keys
                parts = key.split(".")
                obj = self
                for part in parts[:-1]:
                    obj = getattr(obj, part)
                setattr(obj, parts[-1], value)
            else:
                setattr(self, key, value)