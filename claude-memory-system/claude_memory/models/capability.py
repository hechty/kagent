"""Capability models for executable memories"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class CapabilityType(str, Enum):
    """Types of capabilities"""
    SCRIPT = "script"              # Python scripts
    TOOL = "tool"                  # Command-line tools
    TEMPLATE = "template"          # Code/config templates
    WORKFLOW = "workflow"          # Multi-step workflows
    FUNCTION = "function"          # Python functions
    COMMAND = "command"            # Shell commands


class ParameterType(str, Enum):
    """Parameter types for capability interfaces"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    FILE_PATH = "file_path"
    DIRECTORY = "directory"


class Parameter(BaseModel):
    """Capability parameter definition"""
    
    name: str = Field(..., description="Parameter name")
    type: ParameterType = Field(..., description="Parameter type")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(default=True, description="Whether parameter is required")
    default: Optional[Any] = Field(default=None, description="Default value")
    options: Optional[List[Any]] = Field(default=None, description="Valid options if applicable")
    validation_pattern: Optional[str] = Field(default=None, description="Regex validation pattern")


class CapabilityInterface(BaseModel):
    """Interface definition for a capability"""
    
    input_parameters: List[Parameter] = Field(default_factory=list, description="Input parameters")
    output_format: str = Field(default="string", description="Output format description")
    output_schema: Optional[Dict[str, Any]] = Field(default=None, description="JSON schema for output")
    
    # Execution requirements
    requires_files: List[str] = Field(default_factory=list, description="Required files")
    requires_env: List[str] = Field(default_factory=list, description="Required environment variables")
    requires_tools: List[str] = Field(default_factory=list, description="Required external tools")


class ExecutionResult(BaseModel):
    """Result of capability execution"""
    
    success: bool = Field(..., description="Whether execution succeeded")
    output: Any = Field(default=None, description="Execution output")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    duration: float = Field(default=0.0, description="Execution duration in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Execution timestamp")
    
    # Context
    input_params: Dict[str, Any] = Field(default_factory=dict, description="Input parameters used")
    environment: Dict[str, str] = Field(default_factory=dict, description="Environment info")


class Capability(BaseModel):
    """Executable capability stored in memory"""
    
    # Basic info
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="What this capability does")
    capability_type: CapabilityType = Field(..., description="Type of capability")
    
    # Execution info
    content: str = Field(..., description="Script content, command, or template")
    interface: CapabilityInterface = Field(..., description="Input/output interface")
    entry_point: Optional[str] = Field(default=None, description="Entry point function/method")
    
    # Metadata
    version: str = Field(default="1.0.0", description="Capability version")
    author: Optional[str] = Field(default=None, description="Capability author")
    tags: List[str] = Field(default_factory=list, description="Capability tags")
    
    # Dependencies and requirements
    dependencies: List[str] = Field(default_factory=list, description="Python package dependencies")
    system_requirements: List[str] = Field(default_factory=list, description="System requirements")
    
    # Usage tracking
    created_at: datetime = Field(default_factory=datetime.now)
    last_used: Optional[datetime] = Field(default=None, description="Last execution time")
    usage_count: int = Field(default=0, description="Number of times used")
    success_count: int = Field(default=0, description="Number of successful executions")
    
    # Examples and documentation
    usage_examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")
    documentation: Optional[str] = Field(default=None, description="Additional documentation")
    
    # Performance metrics
    avg_duration: float = Field(default=0.0, description="Average execution duration")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance data")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.usage_count == 0:
            return 0.0
        return self.success_count / self.usage_count
    
    def record_execution(self, result: ExecutionResult) -> None:
        """Record execution result and update metrics"""
        self.last_used = result.timestamp
        self.usage_count += 1
        
        if result.success:
            self.success_count += 1
            
        # Update average duration
        if self.usage_count == 1:
            self.avg_duration = result.duration
        else:
            self.avg_duration = (
                (self.avg_duration * (self.usage_count - 1) + result.duration) 
                / self.usage_count
            )
    
    def add_example(self, name: str, input_params: Dict[str, Any], 
                   expected_output: Any, description: str = "") -> None:
        """Add a usage example"""
        example = {
            "name": name,
            "input_params": input_params,
            "expected_output": expected_output,
            "description": description
        }
        self.usage_examples.append(example)
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }