"""
Algorithm Base Module
=====================

This module defines the abstract base classes and data structures that form the
foundation for all analysis algorithms in the NeuroPrime framework.

Key Components:
- ParameterType: Enum defining supported parameter types
- AlgorithmParameter: Data class for parameter definitions
- AlgorithmInput: Data class for algorithm input data
- AlgorithmOutput: Data class for algorithm output results
- BaseAlgorithm: Abstract base class for all analysis algorithms
- create_parameter: Utility function for parameter creation

Design Philosophy:
- Provides a consistent interface for all algorithms
- Enforces type safety and validation
- Supports flexible data structures for electrophysiology data
- Includes built-in execution tracking and error handling
- Enables easy extension with new algorithms

Usage Example:
    from src.algorithms.base import BaseAlgorithm, create_parameter, ParameterType
    
    class MyAlgorithm(BaseAlgorithm):
        def get_parameters_schema(self):
            return [
                create_parameter("threshold", ParameterType.FLOAT, "Detection threshold", 3.0)
            ]
        
        def validate_input(self, input_data):
            return input_data.spike_times is not None
        
        def run(self, input_data, parameters):
            # Algorithm implementation
            return AlgorithmOutput(success=True)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class ParameterType(Enum):
    """
    Enumeration of supported parameter types for algorithm configuration.
    
    Types:
        INTEGER: Whole number values
        FLOAT: Floating-point number values
        STRING: Text values
        BOOLEAN: True/False values
        SELECT: Selection from predefined options
        RANGE: Numeric range with min/max bounds
    """
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    SELECT = "select"
    RANGE = "range"


@dataclass
class AlgorithmParameter:
    """
    Data class defining an algorithm parameter.
    
    This class encapsulates all metadata needed to describe a parameter,
    including its type, description, default value, and constraints.
    
    Attributes:
        name: Parameter identifier used in code
        param_type: Type of parameter (see ParameterType enum)
        description: Human-readable description for UI
        default_value: Default value when not specified
        min_value: Minimum allowed value (for numeric types)
        max_value: Maximum allowed value (for numeric types)
        options: List of allowed values (for SELECT type)
        required: Whether this parameter must be provided
    """
    name: str
    param_type: ParameterType
    description: str
    default_value: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    options: Optional[List[str]] = None  # Used for SELECT type
    required: bool = True


@dataclass
class AlgorithmInput:
    """
    Data class for algorithm input data.
    
    This class aggregates all possible input data types that algorithms
    might need, including neural signals, spike data, behavioral data,
    and metadata.
    
    Attributes:
        lfp_data: Local field potential data [channels × samples]
        spike_times: Array of spike timestamps in seconds
        spike_waveforms: Spike waveform data [n_spikes × samples]
        spike_elec_ids: Array mapping spikes to electrode channels
        trial_info: List of dictionaries containing trial metadata
        events: List of dictionaries containing event information
        sampling_rate: Data sampling rate in Hz (default: 2000.0)
        duration: Total recording duration in seconds
        num_channels: Number of recording channels
        time_range: Tuple specifying time window for analysis (start, end)
        trial_indices: List of trial indices to include in analysis
        extra_data: Dictionary for additional custom data
    """
    # Signal data
    lfp_data: Optional[np.ndarray] = None  # Shape: [n_channels × n_samples]
    spike_times: Optional[np.ndarray] = None
    spike_waveforms: Optional[np.ndarray] = None
    spike_elec_ids: Optional[np.ndarray] = None
    
    # Behavioral data
    trial_info: Optional[List[Dict]] = None
    events: Optional[List[Dict]] = None
    
    # Metadata
    sampling_rate: float = 2000.0
    duration: float = 0.0
    num_channels: int = 0
    
    # Time alignment configuration
    time_range: Optional[tuple] = None  # (start, end) in seconds
    trial_indices: Optional[List[int]] = None  # Selected trial indices
    
    # Additional data
    extra_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlgorithmOutput:
    """
    Data class for algorithm output results.
    
    This class structures the output from algorithm execution, including
    raw data, statistical summaries, visualization configurations,
    and execution metadata.
    
    Attributes:
        data: Dictionary of numpy arrays containing analysis results
        statistics: Dictionary of computed statistical metrics
        plot_config: Configuration for visualization rendering
        export_data: Data prepared for export to external formats
        metadata: Additional metadata about the analysis
        execution_time: Time taken to run the algorithm in seconds
        success: Whether the algorithm completed successfully
        error_message: Error description if execution failed
    """
    # Analysis results
    data: Dict[str, np.ndarray] = field(default_factory=dict)
    statistics: Dict[str, float] = field(default_factory=dict)
    
    # Plot configuration for visualization
    plot_config: Dict[str, Any] = field(default_factory=dict)
    
    # Data prepared for export
    export_data: Dict[str, np.ndarray] = field(default_factory=dict)
    
    # Metadata about the analysis
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Execution information
    execution_time: float = 0.0
    success: bool = True
    error_message: str = ""


class BaseAlgorithm(ABC):
    """
    Abstract base class for all analysis algorithms.
    
    This class defines the interface and common functionality that all
    algorithms must implement. It provides parameter management, input
    validation, execution tracking, and result structuring.
    
    Subclasses must implement:
        - get_parameters_schema(): Return list of AlgorithmParameter objects
        - validate_input(input_data): Check if input is valid
        - run(input_data, parameters): Execute the algorithm
    
    Attributes:
        name: Algorithm class name
        description: Human-readable description
        version: Version identifier
        category: Algorithm category (e.g., 'Spike', 'LFP', 'Behavior')
        required_data_types: List of required data types
        data_requirements_description: Description of data requirements
        _execution_history: List tracking past executions
    """
    
    def __init__(self):
        """Initialize algorithm with default settings"""
        self.name = self.__class__.__name__
        self.description = ""
        self.version = "1.0"
        self.category = "General"  # Algorithm category for organization
        
        # Track execution history for debugging and performance monitoring
        self._execution_history: List[Dict] = []
        
        # Define data requirements
        # Valid types: 'lfp', 'spike', 'behavior'
        self.required_data_types: List[str] = []
        self.data_requirements_description: str = ""
    
    def get_data_requirements(self) -> Dict[str, Any]:
        """
        Get information about the algorithm's data requirements.
        
        Returns:
            Dictionary containing required data types and description
        """
        return {
            'required_types': self.required_data_types,
            'description': self.data_requirements_description,
            'requires_trial_info': 'behavior' in self.required_data_types or 'spike' in self.required_data_types
        }
    
    @abstractmethod
    def get_parameters_schema(self) -> List[AlgorithmParameter]:
        """
        Define the parameter schema for this algorithm.
        
        Returns:
            List of AlgorithmParameter objects defining all parameters
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        """
        Validate that input data meets the algorithm's requirements.
        
        Args:
            input_data: AlgorithmInput object containing input data
        
        Returns:
            True if input is valid for processing, False otherwise
        """
        pass
    
    @abstractmethod
    def run(self, input_data: AlgorithmInput, 
            parameters: Dict[str, Any]) -> AlgorithmOutput:
        """
        Execute the algorithm with the provided input data and parameters.
        
        Args:
            input_data: AlgorithmInput object with input data
            parameters: Dictionary of parameter values
        
        Returns:
            AlgorithmOutput object containing results
        """
        pass
    
    def get_default_parameters(self) -> Dict[str, Any]:
        """
        Get a dictionary of default parameter values.
        
        Returns:
            Dictionary mapping parameter names to their default values
        """
        schema = self.get_parameters_schema()
        return {p.name: p.default_value for p in schema}
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> tuple:
        """
        Validate that provided parameters meet constraints.
        
        Args:
            parameters: Dictionary of parameter values to validate
        
        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        """
        schema = self.get_parameters_schema()
        errors = []
        
        for param in schema:
            # Check for required parameters
            if param.required and param.name not in parameters:
                errors.append(f"Missing required parameter: {param.name}")
                continue
            
            if param.name not in parameters:
                continue
            
            value = parameters[param.name]
            
            # Type validation
            if param.param_type == ParameterType.INTEGER:
                if not isinstance(value, (int, np.integer)):
                    errors.append(f"Parameter '{param.name}' must be an integer")
                    continue
            elif param.param_type == ParameterType.FLOAT:
                if not isinstance(value, (int, float, np.number)):
                    errors.append(f"Parameter '{param.name}' must be a number")
                    continue
            elif param.param_type == ParameterType.BOOLEAN:
                if not isinstance(value, bool):
                    errors.append(f"Parameter '{param.name}' must be a boolean")
                    continue
            elif param.param_type == ParameterType.SELECT:
                if param.options and value not in param.options:
                    errors.append(f"Parameter '{param.name}' must be one of {param.options}")
                    continue
            
            # Range validation for numeric types
            if param.min_value is not None and value < param.min_value:
                errors.append(f"Parameter '{param.name}' must be >= {param.min_value}")
            
            if param.max_value is not None and value > param.max_value:
                errors.append(f"Parameter '{param.name}' must be <= {param.max_value}")
        
        return len(errors) == 0, errors
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the algorithm.
        
        Returns:
            Dictionary containing name, description, version, category, and parameters
        """
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'category': self.category,
            'parameters': [
                {
                    'name': p.name,
                    'type': p.param_type.value,
                    'description': p.description,
                    'default': p.default_value,
                    'required': p.required
                }
                for p in self.get_parameters_schema()
            ]
        }
    
    def _record_execution(self, input_data: AlgorithmInput, 
                         parameters: Dict[str, Any],
                         output: AlgorithmOutput):
        """
        Record execution details for history tracking.
        
        Args:
            input_data: The input data used
            parameters: The parameters used
            output: The resulting output
        """
        import time
        from datetime import datetime
        
        self._execution_history.append({
            'timestamp': datetime.now().isoformat(),
            'parameters': parameters,
            'execution_time': output.execution_time,
            'success': output.success
        })
    
    def prepare_visualization_data(self, input_data: AlgorithmInput) -> Dict[str, Any]:
        """
        Prepare input data for visualization.
        
        Args:
            input_data: AlgorithmInput object
        
        Returns:
            Dictionary containing visualization-ready data
        """
        output_data = {}
        
        if input_data.lfp_data is not None:
            # Prepare LFP signal data for visualization
            output_data['signal_data'] = input_data.lfp_data
            output_data['sampling_rate'] = input_data.sampling_rate
            # Generate time axis
            times = np.arange(input_data.lfp_data.shape[1]) / input_data.sampling_rate
            output_data['times'] = times
            output_data['plot_type'] = 'raw_signal'
        elif input_data.spike_times is not None:
            # Prepare spike data for visualization
            output_data['spike_times'] = input_data.spike_times
            output_data['trial_info'] = input_data.trial_info
            output_data['plot_type'] = 'spike_raster'
        
        return output_data


# Utility function
def create_parameter(name: str, param_type: ParameterType,
                    description: str, default_value: Any,
                    **kwargs) -> AlgorithmParameter:
    """
    Convenience function to create an AlgorithmParameter.
    
    Args:
        name: Parameter identifier
        param_type: Type of parameter (from ParameterType enum)
        description: Human-readable description
        default_value: Default parameter value
        **kwargs: Additional parameters (min_value, max_value, options, required)
    
    Returns:
        AlgorithmParameter object with the specified properties
    """
    return AlgorithmParameter(
        name=name,
        param_type=param_type,
        description=description,
        default_value=default_value,
        **kwargs
    )


if __name__ == '__main__':
    """
    Self-test for base algorithm classes.
    Verifies parameter handling, validation, and basic algorithm execution.
    """
    print("=== Testing BaseAlgorithm ===\n")
    
    # Create a test algorithm
    class TestAlgorithm(BaseAlgorithm):
        def __init__(self):
            super().__init__()
            self.description = "A test algorithm for validation"
            self.category = "Test"
        
        def get_parameters_schema(self):
            return [
                create_parameter(
                    "threshold", ParameterType.FLOAT,
                    "Detection threshold in standard deviations", 3.5,
                    min_value=0.1, max_value=10.0
                ),
                create_parameter(
                    "window_size", ParameterType.INTEGER,
                    "Analysis window size in milliseconds", 50,
                    min_value=10, max_value=200
                ),
                create_parameter(
                    "use_filter", ParameterType.BOOLEAN,
                    "Apply bandpass filter before analysis", True
                ),
                create_parameter(
                    "method", ParameterType.SELECT,
                    "Analysis method selection", "method1",
                    options=["method1", "method2", "method3"]
                )
            ]
        
        def validate_input(self, input_data):
            return input_data.lfp_data is not None
        
        def run(self, input_data, parameters):
            import time
            start_time = time.time()
            
            # Simulate algorithm execution
            result_data = np.random.randn(100, 100)
            
            execution_time = time.time() - start_time
            
            return AlgorithmOutput(
                data={'result': result_data},
                statistics={'mean': np.mean(result_data), 'std': np.std(result_data)},
                execution_time=execution_time,
                success=True
            )
    
    # Test the algorithm
    algo = TestAlgorithm()
    
    print("1. Algorithm Information:")
    info = algo.get_info()
    print(f"   Name: {info['name']}")
    print(f"   Description: {info['description']}")
    print(f"   Category: {info['category']}")
    print(f"   Parameters ({len(info['parameters'])}):")
    for param in info['parameters']:
        print(f"     - {param['name']} ({param['type']}): {param['description']}")
    print()
    
    print("2. Default Parameters:")
    defaults = algo.get_default_parameters()
    for name, value in defaults.items():
        print(f"   {name}: {value}")
    print()
    
    print("3. Parameter Validation:")
    # Test valid parameters
    valid_params = {'threshold': 5.0, 'window_size': 100, 'use_filter': False, 'method': 'method2'}
    is_valid, errors = algo.validate_parameters(valid_params)
    print(f"   Valid parameters test: {is_valid}")
    
    # Test invalid parameters
    invalid_params = {'threshold': 15.0, 'window_size': 5, 'method': 'invalid_method'}
    is_valid, errors = algo.validate_parameters(invalid_params)
    print(f"   Invalid parameters test: {is_valid}")
    print(f"   Error messages: {errors}")
    print()
    
    print("4. Algorithm Execution:")
    input_data = AlgorithmInput(
        lfp_data=np.random.randn(10, 1000),
        sampling_rate=2000.0
    )
    output = algo.run(input_data, valid_params)
    print(f"   Success: {output.success}")
    print(f"   Execution time: {output.execution_time:.4f}s")
    print(f"   Output data shape: {output.data['result'].shape}")
    print(f"   Statistics: mean={output.statistics['mean']:.4f}, std={output.statistics['std']:.4f}")
    print()
    
    print("✅ BaseAlgorithm tests completed successfully!")
