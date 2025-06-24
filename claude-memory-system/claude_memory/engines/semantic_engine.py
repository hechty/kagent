"""
Semantic analysis engine for memory content
"""

import logging
import re
from typing import Any, List

from ..models.context import SemanticInfo
from ..models.memory import MemoryType, MemoryLocation
from ..core.config import MemoryConfig

logger = logging.getLogger(__name__)


class SemanticEngine:
    """
    Semantic analysis engine
    
    Analyzes content to extract:
    - Primary concepts and entities
    - Memory type classification
    - Suggested location in memory palace
    - Auto-generated tags and metadata
    """
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        
        # Keywords for memory type classification
        self._type_keywords = {
            MemoryType.SEMANTIC: [
                "architecture", "design", "concept", "definition", "explanation",
                "theory", "principle", "framework", "knowledge", "documentation"
            ],
            MemoryType.PROCEDURAL: [
                "script", "function", "command", "tool", "automation", "workflow",
                "process", "procedure", "code", "implementation", "execute"
            ],
            MemoryType.EPISODIC: [
                "solution", "problem", "experience", "lesson", "example", "case",
                "issue", "fix", "debug", "troubleshoot", "result", "outcome"
            ],
            MemoryType.WORKING: [
                "current", "session", "temporary", "draft", "work", "progress",
                "ongoing", "active", "todo", "task"
            ]
        }
        
        # Keywords for location classification
        self._location_keywords = {
            MemoryLocation.KNOWLEDGE_WING: [
                "architecture", "design", "concept", "theory", "documentation",
                "specification", "requirement", "analysis"
            ],
            MemoryLocation.CAPABILITY_WING: [
                "script", "tool", "function", "automation", "command", "utility",
                "template", "generator", "builder"
            ],
            MemoryLocation.EXPERIENCE_WING: [
                "solution", "problem", "bug", "fix", "example", "case", "lesson",
                "experience", "troubleshoot", "debug"
            ],
            MemoryLocation.ENTRANCE_HALL: [
                "project", "overview", "summary", "important", "core", "main",
                "primary", "key", "essential"
            ]
        }
    
    def analyze_content(self, content: Any) -> SemanticInfo:
        """Analyze content and extract semantic information"""
        try:
            content_str = str(content)
            
            # Extract concepts and entities
            concepts = self._extract_concepts(content_str)
            entities = self._extract_entities(content_str)
            
            # Classify memory type
            memory_type, type_confidence = self._classify_memory_type(content_str)
            
            # Suggest location
            location = self._suggest_location(content_str, memory_type)
            
            # Generate tags
            tags = self._generate_tags(content_str, concepts, entities)
            
            # Generate title if possible
            title = self._suggest_title(content_str)
            
            # Generate summary
            summary = self._generate_summary(content_str)
            
            # Calculate complexity
            complexity = self._calculate_complexity(content_str)
            
            return SemanticInfo(
                primary_concepts=concepts[:5],  # Top 5 concepts
                secondary_concepts=concepts[5:10],  # Next 5
                entities=entities,
                predicted_type=memory_type.value,
                confidence=type_confidence,
                suggested_location=location.value,
                topics=self._extract_topics(content_str),
                complexity_score=complexity,
                generated_tags=tags,
                suggested_title=title,
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze content: {e}")
            # Return default semantic info
            return SemanticInfo(
                predicted_type=MemoryType.SEMANTIC.value,
                confidence=0.5,
                suggested_location=MemoryLocation.KNOWLEDGE_WING.value
            )
    
    def _extract_concepts(self, content: str) -> List[str]:
        """Extract key concepts from content"""
        concepts = []
        
        # Look for technical terms (capitalized words, camelCase, etc.)
        patterns = [
            r'\b[A-Z][a-zA-Z]*\b',  # Capitalized words
            r'\b[a-z]+[A-Z][a-zA-Z]*\b',  # camelCase
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b\w+\.\w+\b',  # Dotted notation (packages, etc.)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            concepts.extend(matches)
        
        # Remove duplicates and common words
        concepts = list(set(concepts))
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must'}
        concepts = [c for c in concepts if c.lower() not in common_words and len(c) > 2]
        
        return concepts[:20]  # Return top 20
    
    def _extract_entities(self, content: str) -> List[str]:
        """Extract named entities (files, URLs, etc.)"""
        entities = []
        
        # File paths
        file_patterns = [
            r'\b\w+\.\w{2,4}\b',  # filename.ext
            r'[/\\][\w/\\.-]+',   # paths
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, content)
            entities.extend(matches)
        
        # URLs
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, content)
        entities.extend(urls)
        
        return list(set(entities))[:10]  # Return top 10 unique
    
    def _classify_memory_type(self, content: str) -> tuple[MemoryType, float]:
        """Classify memory type based on content"""
        content_lower = content.lower()
        type_scores = {}
        
        # Score each memory type based on keyword matches
        for memory_type, keywords in self._type_keywords.items():
            score = 0
            for keyword in keywords:
                count = content_lower.count(keyword)
                score += count
            
            # Normalize by content length
            if len(content) > 0:
                type_scores[memory_type] = score / (len(content) / 1000 + 1)
            else:
                type_scores[memory_type] = 0
        
        # Find type with highest score
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            confidence = min(1.0, type_scores[best_type] / 5.0)  # Cap at 1.0
        else:
            best_type = MemoryType.SEMANTIC
            confidence = 0.5
        
        return best_type, confidence
    
    def _suggest_location(self, content: str, memory_type: MemoryType) -> MemoryLocation:
        """Suggest memory palace location"""
        content_lower = content.lower()
        location_scores = {}
        
        # Score each location based on keywords
        for location, keywords in self._location_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in content_lower:
                    score += 1
            location_scores[location] = score
        
        # Choose location with highest score, or default based on type
        if location_scores and max(location_scores.values()) > 0:
            return max(location_scores, key=location_scores.get)
        
        # Default locations based on memory type
        type_to_location = {
            MemoryType.SEMANTIC: MemoryLocation.KNOWLEDGE_WING,
            MemoryType.PROCEDURAL: MemoryLocation.CAPABILITY_WING,
            MemoryType.EPISODIC: MemoryLocation.EXPERIENCE_WING,
            MemoryType.WORKING: MemoryLocation.ENTRANCE_HALL
        }
        
        return type_to_location.get(memory_type, MemoryLocation.KNOWLEDGE_WING)
    
    def _generate_tags(self, content: str, concepts: List[str], entities: List[str]) -> List[str]:
        """Generate automatic tags"""
        tags = []
        
        # Add concept-based tags
        for concept in concepts[:5]:
            if len(concept) > 2:
                tags.append(concept.lower())
        
        # Add domain-specific tags
        domain_keywords = {
            "python": ["python", "pip", "venv", "import", "def ", "class ", ".py"],
            "javascript": ["javascript", "node", "npm", "function", "const ", "let ", ".js"],
            "kotlin": ["kotlin", "gradle", "fun ", "class ", "val ", "var ", ".kt"],
            "web": ["http", "html", "css", "url", "api", "rest", "json"],
            "database": ["sql", "database", "table", "query", "select", "insert"],
            "docker": ["docker", "container", "image", "dockerfile", "compose"],
            "git": ["git", "commit", "branch", "merge", "pull", "push", "clone"],
            "testing": ["test", "assert", "mock", "pytest", "junit", "spec"],
            "data": ["data", "csv", "json", "analysis", "statistics", "pandas"],
            "ai": ["ai", "ml", "model", "training", "neural", "llm", "gpt"]
        }
        
        content_lower = content.lower()
        for domain, keywords in domain_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                tags.append(domain)
        
        # Add entity-based tags
        for entity in entities:
            if entity.endswith(('.py', '.js', '.kt', '.java', '.cpp')):
                tags.append("code")
            elif entity.endswith(('.md', '.txt', '.doc')):
                tags.append("documentation")
            elif entity.startswith('http'):
                tags.append("web")
        
        return list(set(tags))[:10]  # Return unique tags, max 10
    
    def _suggest_title(self, content: str) -> str:
        """Suggest a title for the content"""
        lines = content.strip().split('\n')
        
        # Try to find a title from first line
        if lines:
            first_line = lines[0].strip()
            
            # Check if first line looks like a title
            if len(first_line) < 100 and not first_line.endswith(('.', ';', ':')):
                # Remove common prefixes
                title = re.sub(r'^#+\s*', '', first_line)  # Remove markdown headers
                title = re.sub(r'^//\s*', '', title)       # Remove comment markers
                title = re.sub(r'^#\s*', '', title)        # Remove shell comments
                
                if len(title) > 3:
                    return title
        
        # Try to extract from function/class definitions
        patterns = [
            r'def\s+(\w+)',      # Python functions
            r'function\s+(\w+)', # JavaScript functions
            r'class\s+(\w+)',    # Class definitions
            r'fun\s+(\w+)',      # Kotlin functions
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return f"{match.group(1)} function"
        
        # Default based on content type
        if len(content) < 100:
            return "Short note"
        elif any(keyword in content.lower() for keyword in ["function", "def ", "class "]):
            return "Code snippet"
        elif any(keyword in content.lower() for keyword in ["error", "bug", "fix", "problem"]):
            return "Problem solution"
        else:
            return "Knowledge note"
    
    def _generate_summary(self, content: str) -> str:
        """Generate a brief summary of the content"""
        # Simple summary: first sentence or first 150 characters
        sentences = re.split(r'[.!?]+', content.strip())
        
        if sentences and len(sentences[0]) > 10:
            first_sentence = sentences[0].strip()
            if len(first_sentence) < 200:
                return first_sentence
        
        # Fallback: first 150 characters
        summary = content.strip()[:150]
        if len(content) > 150:
            summary += "..."
        
        return summary
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topic classifications"""
        topics = []
        
        topic_keywords = {
            "development": ["code", "programming", "development", "software"],
            "configuration": ["config", "setup", "install", "environment"],
            "documentation": ["readme", "docs", "guide", "manual"],
            "troubleshooting": ["error", "bug", "fix", "problem", "issue"],
            "architecture": ["design", "architecture", "pattern", "structure"],
            "automation": ["script", "automation", "tool", "utility"],
        }
        
        content_lower = content.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _calculate_complexity(self, content: str) -> float:
        """Calculate content complexity score"""
        factors = []
        
        # Length factor
        length_score = min(1.0, len(content) / 1000)
        factors.append(length_score)
        
        # Technical terms factor
        tech_patterns = [
            r'\b[A-Z][a-zA-Z]*\b',  # Capitalized words
            r'\b\w+\.\w+\b',        # Dotted notation
            r'\([^)]*\)',           # Function calls
            r'\{[^}]*\}',           # Code blocks
        ]
        
        tech_count = sum(len(re.findall(pattern, content)) for pattern in tech_patterns)
        tech_score = min(1.0, tech_count / 20)
        factors.append(tech_score)
        
        # Line complexity
        lines = content.split('\n')
        avg_line_length = sum(len(line) for line in lines) / max(len(lines), 1)
        line_score = min(1.0, avg_line_length / 80)
        factors.append(line_score)
        
        # Overall complexity
        complexity = sum(factors) / len(factors)
        return round(complexity * 10, 1)  # Scale to 0-10