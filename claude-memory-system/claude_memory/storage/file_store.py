"""
File-based storage backend for memory persistence
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..models.memory import Memory, MemoryType, MemoryScope
from ..core.config import MemoryConfig

logger = logging.getLogger(__name__)


class FileStore:
    """
    File-based storage for memory persistence
    
    Organizes memories in a directory structure:
    - global/
      - semantic/
      - episodic/
      - procedural/
      - working/
    - project/
      - semantic/
      - episodic/
      - procedural/
      - working/
    """
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self._setup_directory_structure()
    
    def _setup_directory_structure(self) -> None:
        """Setup the directory structure for memory storage"""
        for scope in [MemoryScope.GLOBAL, MemoryScope.PROJECT]:
            base_path = self.config.get_storage_path(scope.value)
            if base_path:
                for memory_type in MemoryType:
                    type_path = base_path / scope.value / memory_type.value
                    type_path.mkdir(parents=True, exist_ok=True)
                
                # Create metadata directory
                (base_path / scope.value / "_metadata").mkdir(parents=True, exist_ok=True)
    
    def store_memory(self, memory: Memory) -> None:
        """Store a memory to the file system"""
        try:
            # Get storage path
            base_path = self.config.get_storage_path(memory.scope.value)
            memory_dir = base_path / memory.scope.value / memory.memory_type.value
            
            # Create file path
            memory_file = memory_dir / f"{memory.id}.json"
            
            # Serialize memory
            memory_data = memory.dict()
            memory_data["stored_at"] = datetime.now().isoformat()
            
            # Write to file
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Update index
            self._update_index(memory)
            
            logger.debug(f"Stored memory {memory.id} to {memory_file}")
            
        except Exception as e:
            logger.error(f"Failed to store memory {memory.id}: {e}")
            raise
    
    def load_memory(self, memory_id: str) -> Optional[Memory]:
        """Load a memory by ID"""
        try:
            # Search in both global and project scopes
            for scope in [MemoryScope.GLOBAL, MemoryScope.PROJECT]:
                base_path = self.config.get_storage_path(scope.value)
                if not base_path or not base_path.exists():
                    continue
                
                # Search in all memory type directories
                for memory_type in MemoryType:
                    memory_file = base_path / scope.value / memory_type.value / f"{memory_id}.json"
                    if memory_file.exists():
                        with open(memory_file, 'r', encoding='utf-8') as f:
                            memory_data = json.load(f)
                        
                        # Remove storage metadata
                        memory_data.pop("stored_at", None)
                        
                        return Memory(**memory_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load memory {memory_id}: {e}")
            return None
    
    def update_memory(self, memory: Memory) -> None:
        """Update an existing memory"""
        try:
            # Memory ID should remain the same, just re-store
            self.store_memory(memory)
            logger.debug(f"Updated memory {memory.id}")
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory.id}: {e}")
            raise
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        try:
            # Find and delete the memory file
            for scope in [MemoryScope.GLOBAL, MemoryScope.PROJECT]:
                base_path = self.config.get_storage_path(scope.value)
                if not base_path or not base_path.exists():
                    continue
                
                for memory_type in MemoryType:
                    memory_file = base_path / scope.value / memory_type.value / f"{memory_id}.json"
                    if memory_file.exists():
                        memory_file.unlink()
                        self._remove_from_index(memory_id)
                        logger.debug(f"Deleted memory {memory_id}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False
    
    def load_all_memories(self) -> List[Memory]:
        """Load all memories from storage"""
        memories = []
        
        try:
            for scope in [MemoryScope.GLOBAL, MemoryScope.PROJECT]:
                base_path = self.config.get_storage_path(scope.value)
                if not base_path or not base_path.exists():
                    continue
                
                scope_dir = base_path / scope.value
                if not scope_dir.exists():
                    continue
                
                # Load from each memory type directory
                for memory_type in MemoryType:
                    type_dir = scope_dir / memory_type.value
                    if not type_dir.exists():
                        continue
                    
                    # Load all JSON files in directory
                    for memory_file in type_dir.glob("*.json"):
                        try:
                            with open(memory_file, 'r', encoding='utf-8') as f:
                                memory_data = json.load(f)
                            
                            # Remove storage metadata
                            memory_data.pop("stored_at", None)
                            
                            memory = Memory(**memory_data)
                            memories.append(memory)
                            
                        except Exception as e:
                            logger.warning(f"Failed to load memory from {memory_file}: {e}")
                            continue
            
            logger.debug(f"Loaded {len(memories)} memories from storage")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to load memories: {e}")
            return []
    
    def load_memories_by_type(self, memory_type: MemoryType, 
                             scope: Optional[MemoryScope] = None) -> List[Memory]:
        """Load memories of a specific type"""
        memories = []
        
        try:
            scopes_to_search = [scope] if scope else [MemoryScope.GLOBAL, MemoryScope.PROJECT]
            
            for search_scope in scopes_to_search:
                base_path = self.config.get_storage_path(search_scope.value)
                if not base_path or not base_path.exists():
                    continue
                
                type_dir = base_path / search_scope.value / memory_type.value
                if not type_dir.exists():
                    continue
                
                # Load all JSON files in directory
                for memory_file in type_dir.glob("*.json"):
                    try:
                        with open(memory_file, 'r', encoding='utf-8') as f:
                            memory_data = json.load(f)
                        
                        # Remove storage metadata
                        memory_data.pop("stored_at", None)
                        
                        memory = Memory(**memory_data)
                        memories.append(memory)
                        
                    except Exception as e:
                        logger.warning(f"Failed to load memory from {memory_file}: {e}")
                        continue
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to load {memory_type.value} memories: {e}")
            return []
    
    def load_memories_by_scope(self, scope: MemoryScope) -> List[Memory]:
        """Load all memories from a specific scope"""
        memories = []
        
        try:
            base_path = self.config.get_storage_path(scope.value)
            if not base_path or not base_path.exists():
                return []
            
            scope_dir = base_path / scope.value
            if not scope_dir.exists():
                return []
            
            # Load from each memory type directory
            for memory_type in MemoryType:
                type_memories = self.load_memories_by_type(memory_type, scope)
                memories.extend(type_memories)
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to load {scope.value} memories: {e}")
            return []
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Get statistics about stored memories"""
        stats = {
            "total": 0,
            "global": 0,
            "project": 0
        }
        
        # Add memory type stats
        for memory_type in MemoryType:
            stats[memory_type.value] = 0
        
        try:
            all_memories = self.load_all_memories()
            stats["total"] = len(all_memories)
            
            for memory in all_memories:
                stats[memory.scope.value] += 1
                stats[memory.memory_type.value] += 1
            
        except Exception as e:
            logger.error(f"Failed to calculate memory stats: {e}")
        
        return stats
    
    def _update_index(self, memory: Memory) -> None:
        """Update the memory index for fast lookups"""
        try:
            base_path = self.config.get_storage_path(memory.scope.value)
            index_file = base_path / memory.scope.value / "_metadata" / "index.json"
            
            # Load existing index
            index = {}
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            
            # Update index entry
            index[memory.id] = {
                "type": memory.memory_type.value,
                "title": memory.title,
                "tags": memory.tags,
                "importance": memory.importance,
                "created_at": memory.created_at.isoformat(),
                "last_accessed": memory.last_accessed.isoformat()
            }
            
            # Write updated index
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.warning(f"Failed to update memory index: {e}")
    
    def _remove_from_index(self, memory_id: str) -> None:
        """Remove a memory from the index"""
        try:
            for scope in [MemoryScope.GLOBAL, MemoryScope.PROJECT]:
                base_path = self.config.get_storage_path(scope.value)
                if not base_path:
                    continue
                
                index_file = base_path / scope.value / "_metadata" / "index.json"
                if not index_file.exists():
                    continue
                
                # Load and update index
                with open(index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
                
                if memory_id in index:
                    del index[memory_id]
                    
                    with open(index_file, 'w', encoding='utf-8') as f:
                        json.dump(index, f, indent=2, ensure_ascii=False)
                    break
                    
        except Exception as e:
            logger.warning(f"Failed to remove from memory index: {e}")
    
    def cleanup_orphaned_files(self) -> int:
        """Clean up orphaned memory files"""
        cleaned = 0
        
        try:
            for scope in [MemoryScope.GLOBAL, MemoryScope.PROJECT]:
                base_path = self.config.get_storage_path(scope.value)
                if not base_path or not base_path.exists():
                    continue
                
                scope_dir = base_path / scope.value
                if not scope_dir.exists():
                    continue
                
                # Check each memory type directory
                for memory_type in MemoryType:
                    type_dir = scope_dir / memory_type.value
                    if not type_dir.exists():
                        continue
                    
                    # Check each memory file
                    for memory_file in type_dir.glob("*.json"):
                        try:
                            with open(memory_file, 'r', encoding='utf-8') as f:
                                memory_data = json.load(f)
                            
                            # Try to create Memory object to validate
                            Memory(**memory_data)
                            
                        except Exception as e:
                            logger.warning(f"Removing invalid memory file {memory_file}: {e}")
                            memory_file.unlink()
                            cleaned += 1
            
            logger.info(f"Cleaned up {cleaned} orphaned memory files")
            return cleaned
            
        except Exception as e:
            logger.error(f"Failed to cleanup orphaned files: {e}")
            return 0