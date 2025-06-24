"""
Capability execution engine
"""

import logging
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from ..models.capability import Capability, ExecutionResult, CapabilityType
from ..core.config import MemoryConfig

logger = logging.getLogger(__name__)


class CapabilityEngine:
    """
    Engine for executing stored capabilities
    
    Supports:
    - Python scripts
    - Shell commands
    - Function execution
    - Template processing
    """
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self._execution_timeout = 30.0  # Default timeout in seconds
    
    def execute_capability(self, capability: Capability, params: Dict[str, Any]) -> ExecutionResult:
        """Execute a capability with given parameters"""
        start_time = time.time()
        
        try:
            logger.info(f"Executing capability: {capability.name}")
            
            # Validate parameters
            validation_error = self._validate_parameters(capability, params)
            if validation_error:
                return ExecutionResult(
                    success=False,
                    error=f"Parameter validation failed: {validation_error}",
                    duration=time.time() - start_time,
                    input_params=params
                )
            
            # Execute based on capability type
            if capability.capability_type == CapabilityType.SCRIPT:
                result = self._execute_script(capability, params)
            elif capability.capability_type == CapabilityType.COMMAND:
                result = self._execute_command(capability, params)
            elif capability.capability_type == CapabilityType.FUNCTION:
                result = self._execute_function(capability, params)
            elif capability.capability_type == CapabilityType.TEMPLATE:
                result = self._process_template(capability, params)
            else:
                result = ExecutionResult(
                    success=False,
                    error=f"Unsupported capability type: {capability.capability_type}",
                    duration=time.time() - start_time,
                    input_params=params
                )
            
            # Update execution time
            result.duration = time.time() - start_time
            
            # Record execution in capability
            capability.record_execution(result)
            
            logger.info(f"Capability execution completed: success={result.success}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute capability: {e}")
            return ExecutionResult(
                success=False,
                error=str(e),
                duration=time.time() - start_time,
                input_params=params
            )
    
    def _validate_parameters(self, capability: Capability, params: Dict[str, Any]) -> str:
        """Validate input parameters against capability interface"""
        try:
            required_params = [
                p.name for p in capability.interface.input_parameters 
                if p.required
            ]
            
            # Check required parameters
            missing = [p for p in required_params if p not in params]
            if missing:
                return f"Missing required parameters: {missing}"
            
            # Validate parameter types (basic validation)
            for param_def in capability.interface.input_parameters:
                if param_def.name in params:
                    value = params[param_def.name]
                    
                    # Basic type checking
                    if param_def.type == "integer" and not isinstance(value, int):
                        try:
                            params[param_def.name] = int(value)
                        except ValueError:
                            return f"Parameter {param_def.name} must be an integer"
                    
                    elif param_def.type == "float" and not isinstance(value, (int, float)):
                        try:
                            params[param_def.name] = float(value)
                        except ValueError:
                            return f"Parameter {param_def.name} must be a number"
                    
                    elif param_def.type == "boolean" and not isinstance(value, bool):
                        if isinstance(value, str):
                            params[param_def.name] = value.lower() in ('true', '1', 'yes', 'on')
                        else:
                            return f"Parameter {param_def.name} must be a boolean"
            
            return None  # No validation errors
            
        except Exception as e:
            return f"Validation error: {e}"
    
    def _execute_script(self, capability: Capability, params: Dict[str, Any]) -> ExecutionResult:
        """Execute a Python script capability"""
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                script_content = capability.content
                
                # Simple parameter substitution
                for param_name, param_value in params.items():
                    placeholder = f"${{{param_name}}}"
                    script_content = script_content.replace(placeholder, str(param_value))
                
                f.write(script_content)
                script_path = f.name
            
            try:
                # Execute the script
                result = subprocess.run(
                    ["python", script_path],
                    capture_output=True,
                    text=True,
                    timeout=self._execution_timeout
                )
                
                if result.returncode == 0:
                    return ExecutionResult(
                        success=True,
                        output=result.stdout,
                        input_params=params,
                        environment={"script_path": script_path}
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        error=result.stderr,
                        output=result.stdout,
                        input_params=params
                    )
                    
            finally:
                # Clean up temporary file
                Path(script_path).unlink(missing_ok=True)
                
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                error=f"Script execution timed out after {self._execution_timeout}s",
                input_params=params
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Script execution failed: {e}",
                input_params=params
            )
    
    def _execute_command(self, capability: Capability, params: Dict[str, Any]) -> ExecutionResult:
        """Execute a shell command capability"""
        try:
            command = capability.content
            
            # Simple parameter substitution
            for param_name, param_value in params.items():
                placeholder = f"${{{param_name}}}"
                command = command.replace(placeholder, str(param_value))
            
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self._execution_timeout
            )
            
            if result.returncode == 0:
                return ExecutionResult(
                    success=True,
                    output=result.stdout,
                    input_params=params,
                    environment={"command": command}
                )
            else:
                return ExecutionResult(
                    success=False,
                    error=result.stderr,
                    output=result.stdout,
                    input_params=params
                )
                
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                error=f"Command execution timed out after {self._execution_timeout}s",
                input_params=params
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Command execution failed: {e}",
                input_params=params
            )
    
    def _execute_function(self, capability: Capability, params: Dict[str, Any]) -> ExecutionResult:
        """Execute a Python function capability"""
        try:
            # This is a simplified implementation
            # In production, this would need proper sandboxing
            
            # Create a safe execution environment
            exec_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'max': max,
                    'min': min,
                    'sum': sum,
                }
            }
            
            # Execute the function code
            exec(capability.content, exec_globals)
            
            # Call the entry point function
            entry_point = capability.entry_point or "main"
            if entry_point in exec_globals:
                func = exec_globals[entry_point]
                output = func(**params)
                
                return ExecutionResult(
                    success=True,
                    output=output,
                    input_params=params
                )
            else:
                return ExecutionResult(
                    success=False,
                    error=f"Entry point function '{entry_point}' not found",
                    input_params=params
                )
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Function execution failed: {e}",
                input_params=params
            )
    
    def _process_template(self, capability: Capability, params: Dict[str, Any]) -> ExecutionResult:
        """Process a template capability"""
        try:
            template_content = capability.content
            
            # Simple template substitution
            for param_name, param_value in params.items():
                placeholder = f"${{{param_name}}}"
                template_content = template_content.replace(placeholder, str(param_value))
            
            return ExecutionResult(
                success=True,
                output=template_content,
                input_params=params
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Template processing failed: {e}",
                input_params=params
            )