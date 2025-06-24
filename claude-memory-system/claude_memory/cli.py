"""
Command-line interface for Claude Memory System
"""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from .core.memory_manager import MemoryManager
from .models.memory import MemoryType, MemoryScope

app = typer.Typer(help="Claude Memory System - AI Memory Management")
console = Console()


@app.command()
def awaken(
    project_path: Optional[Path] = typer.Option(None, "--project", "-p", help="Project path"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Session context")
):
    """🌅 Awaken the memory system and show status"""
    try:
        memory = MemoryManager(project_path)
        snapshot = memory.awaken(context)
        
        # Display beautiful output
        console.print(Panel(snapshot.get_summary(), title="🧠 Memory System Awakened", expand=False))
        
        # Show statistics
        stats = snapshot.memory_statistics
        table = Table(title="📊 Memory Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Memories", str(stats.total_memories))
        table.add_row("Global Memories", str(stats.global_memories))
        table.add_row("Project Memories", str(stats.project_memories))
        table.add_row("Semantic", str(stats.semantic_count))
        table.add_row("Episodic", str(stats.episodic_count))
        table.add_row("Procedural", str(stats.procedural_count))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Failed to awaken memory system: {e}", style="red")
        sys.exit(1)


@app.command()
def remember(
    content: str = typer.Argument(..., help="Content to remember"),
    memory_type: str = typer.Option("semantic", "--type", "-t", help="Memory type"),
    title: Optional[str] = typer.Option(None, "--title", help="Memory title"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags"),
    importance: float = typer.Option(5.0, "--importance", "-i", help="Importance (0-10)"),
    scope: str = typer.Option("project", "--scope", "-s", help="Memory scope (global/project)"),
    project_path: Optional[Path] = typer.Option(None, "--project", "-p", help="Project path")
):
    """🧠 Store something in memory"""
    try:
        memory = MemoryManager(project_path)
        memory.awaken()
        
        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
        
        # Store memory
        memory_id = memory.remember(
            content=content,
            memory_type=memory_type,
            title=title,
            tags=tag_list,
            importance=importance,
            scope=scope
        )
        
        console.print(f"✅ Memory stored with ID: {memory_id}", style="green")
        
    except Exception as e:
        console.print(f"❌ Failed to store memory: {e}", style="red")
        sys.exit(1)


@app.command()
def recall(
    query: str = typer.Argument(..., help="Search query"),
    max_results: int = typer.Option(5, "--max", "-m", help="Maximum results"),
    memory_types: Optional[str] = typer.Option(None, "--types", help="Filter by types (comma-separated)"),
    project_path: Optional[Path] = typer.Option(None, "--project", "-p", help="Project path")
):
    """💭 Search and recall memories"""
    try:
        memory = MemoryManager(project_path)
        memory.awaken()
        
        # Parse memory types
        type_list = None
        if memory_types:
            type_list = [t.strip() for t in memory_types.split(",")]
        
        # Search memories
        results = memory.recall(
            query=query,
            memory_types=type_list,
            max_results=max_results
        )
        
        if not results:
            console.print("🔍 No matching memories found", style="yellow")
            return
        
        # Display results
        for i, result in enumerate(results, 1):
            mem = result.memory
            
            # Create panel content
            content_preview = str(mem.content)[:200]
            if len(str(mem.content)) > 200:
                content_preview += "..."
            
            panel_content = f"""
**Type:** {mem.memory_type.value}
**Scope:** {mem.scope.value}
**Importance:** {mem.importance}/10
**Relevance:** {result.relevance_score:.2f}
**Tags:** {', '.join(mem.tags) if mem.tags else 'None'}

**Content:**
{content_preview}
            """.strip()
            
            console.print(Panel(
                panel_content,
                title=f"🧠 Memory {i}: {mem.title}",
                expand=False
            ))
        
    except Exception as e:
        console.print(f"❌ Failed to recall memories: {e}", style="red")
        sys.exit(1)


@app.command()
def invoke(
    capability_name: str = typer.Argument(..., help="Capability name"),
    params: Optional[str] = typer.Option(None, "--params", help="JSON parameters"),
    project_path: Optional[Path] = typer.Option(None, "--project", "-p", help="Project path")
):
    """⚡ Invoke a stored capability"""
    try:
        memory = MemoryManager(project_path)
        memory.awaken()
        
        # Parse parameters
        param_dict = {}
        if params:
            param_dict = json.loads(params)
        
        # Invoke capability
        result = memory.invoke_capability(capability_name, param_dict)
        
        if result.success:
            console.print(f"✅ Capability executed successfully", style="green")
            console.print(f"**Output:**")
            console.print(result.output)
            console.print(f"**Duration:** {result.duration:.2f}s")
        else:
            console.print(f"❌ Capability execution failed: {result.error}", style="red")
        
    except Exception as e:
        console.print(f"❌ Failed to invoke capability: {e}", style="red")
        sys.exit(1)


@app.command()
def reflect(
    project_path: Optional[Path] = typer.Option(None, "--project", "-p", help="Project path")
):
    """🤔 Analyze memory patterns and get insights"""
    try:
        memory = MemoryManager(project_path)
        memory.awaken()
        
        insights = memory.reflect()
        
        console.print(Panel(insights.get_summary(), title="🤔 Memory Insights", expand=False))
        
    except Exception as e:
        console.print(f"❌ Failed to analyze memories: {e}", style="red")
        sys.exit(1)


@app.command()
def suggest(
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Context for suggestions"),
    project_path: Optional[Path] = typer.Option(None, "--project", "-p", help="Project path")
):
    """💡 Get context-aware suggestions"""
    try:
        memory = MemoryManager(project_path)
        memory.awaken()
        
        suggestions = memory.suggest(context)
        
        if not suggestions:
            console.print("💡 No suggestions at this time", style="yellow")
            return
        
        for i, suggestion in enumerate(suggestions, 1):
            panel_content = f"""
**Type:** {suggestion.type}
**Priority:** {suggestion.priority}/10
**Reason:** {suggestion.reason}
            """.strip()
            
            console.print(Panel(
                panel_content,
                title=f"💡 Suggestion {i}: {suggestion.action}",
                expand=False
            ))
        
    except Exception as e:
        console.print(f"❌ Failed to get suggestions: {e}", style="red")
        sys.exit(1)


@app.command()
def demo():
    """🎯 Run a demonstration of the memory system"""
    console.print("🎯 Claude Memory System Demo", style="bold blue")
    console.print()
    
    try:
        # Initialize memory manager
        memory = MemoryManager()
        
        # Awaken
        console.print("🌅 Awakening memory system...")
        snapshot = memory.awaken("Demo session")
        console.print(f"✅ Memory system awakened with {snapshot.memory_statistics.total_memories} existing memories")
        console.print()
        
        # Store some example memories
        console.print("🧠 Storing example memories...")
        
        # Store knowledge
        knowledge_id = memory.remember(
            content="Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
            memory_type="semantic",
            title="Python Programming Language",
            tags=["python", "programming", "language"],
            importance=8.0,
            scope="global"
        )
        console.print(f"   📚 Stored knowledge: {knowledge_id[:8]}...")
        
        # Store a capability
        script_content = '''
def analyze_file(file_path):
    """Analyze a file and return basic statistics"""
    import os
    
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    stats = os.stat(file_path)
    return {
        "size": stats.st_size,
        "lines": len(open(file_path).readlines()) if file_path.endswith('.txt') else None,
        "modified": stats.st_mtime
    }

# Example usage
if __name__ == "__main__":
    result = analyze_file("${file_path}")
    print(result)
'''
        
        capability_id = memory.remember(
            content=script_content,
            memory_type="procedural",
            title="File Analyzer Tool",
            tags=["file", "analysis", "tool", "python"],
            importance=7.0,
            scope="global"
        )
        console.print(f"   ⚡ Stored capability: {capability_id[:8]}...")
        
        # Store an experience
        experience_id = memory.remember(
            content="Solved a memory leak issue in Python by using weakref for circular references. The problem was caused by parent-child object relationships that prevented garbage collection.",
            memory_type="episodic",
            title="Memory Leak Solution",
            tags=["python", "memory", "debugging", "solution"],
            importance=6.0,
            scope="project"
        )
        console.print(f"   🎯 Stored experience: {experience_id[:8]}...")
        console.print()
        
        # Demonstrate recall
        console.print("💭 Recalling memories about Python...")
        results = memory.recall("Python programming", max_results=3)
        for i, result in enumerate(results, 1):
            console.print(f"   {i}. {result.memory.title} (relevance: {result.relevance_score:.2f})")
        console.print()
        
        # Demonstrate suggestions
        console.print("💡 Getting suggestions for file analysis...")
        suggestions = memory.suggest("analyze files in project")
        for i, suggestion in enumerate(suggestions, 1):
            console.print(f"   {i}. {suggestion.action}")
        console.print()
        
        # Demonstrate reflection
        console.print("🤔 Reflecting on memory patterns...")
        insights = memory.reflect()
        console.print(f"   📊 Memory health: {insights.health_score:.1f}/10")
        console.print(f"   ⭐ Quality score: {insights.quality_score:.1f}/10")
        if insights.recommendations:
            console.print(f"   💡 Recommendation: {insights.recommendations[0]}")
        console.print()
        
        console.print("✅ Demo completed successfully!", style="green")
        console.print("🚀 The memory system is ready for use!")
        
    except Exception as e:
        console.print(f"❌ Demo failed: {e}", style="red")
        sys.exit(1)


def main():
    """Entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()