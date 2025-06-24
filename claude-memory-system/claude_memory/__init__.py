"""
Claude Memory System - AI Memory Management for Claude Code

A persistent memory management system that enables Claude Code to:
- Maintain knowledge across sessions
- Accumulate and reuse capabilities
- Build contextual understanding over time
- Distinguish between global and project-specific memories

Version: 0.1.0
Author: Claude Code
"""

__version__ = "0.1.0"
__author__ = "Claude Code"

from .core.memory_manager import MemoryManager
from .models.memory import Memory, MemoryType
from .models.capability import Capability
from .models.snapshot import MemorySnapshot

__all__ = [
    "MemoryManager",
    "Memory", 
    "MemoryType",
    "Capability",
    "MemorySnapshot",
]